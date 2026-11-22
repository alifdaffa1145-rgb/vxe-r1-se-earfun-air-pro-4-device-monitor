#!/usr/bin/env python3
"""Bridge HTTP lokal untuk Device Monitor UI.

Menyediakan GET /api/status dan POST /api/{mouse,tws} pada 127.0.0.1:8765.
Memakai skrip probe yang sudah terverifikasi. Tidak ada dependency di luar stdlib.
"""
import ctypes
import json
import struct
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import probe_earbud as pe
import probe_mouse as pm

PORT = 8765
LOCK = {"mouse": threading.Lock(), "tws": threading.Lock()}
CACHE = {"mouse": {}, "tws": {}}
CACHE_TS = {"mouse": 0.0, "tws": 0.0}
CACHE_ERR = {"mouse": None, "tws": None}
CACHE_ERR_TS = {"mouse": 0.0, "tws": 0.0}
FRESH = 5.0        # detik: data dianggap masih segar
ERR_WAIT = 12.0    # detik: jeda percobaan ulang setelah gagal
LOCK_WAIT = 3.5    # detik: batas menunggu perangkat lain selesai


def refresh(name, fn):
    """Baca perangkat di balik lock; kegagalan dicatat, cache lama dipertahankan."""
    with LOCK[name]:
        try:
            CACHE[name].update(fn())
            CACHE_ERR[name] = None
            CACHE_TS[name] = time.monotonic()
        except Exception as exc:
            CACHE_ERR[name] = str(exc)
            CACHE_ERR_TS[name] = time.monotonic()


def refresh_if_due(name, fn):
    """Baca ulang hanya kalau cache basi; setelah gagal, tunggu ERR_WAIT."""
    now = time.monotonic()
    if CACHE_ERR[name] is None:
        if now - CACHE_TS[name] < FRESH:
            return False
    elif now - CACHE_ERR_TS[name] < ERR_WAIT:
        return False
    refresh(name, fn)
    return True


def is_connected(name):
    return CACHE_ERR[name] is None and (time.monotonic() - CACHE_TS[name]) <= FRESH

POLL_CODES = {0x08: 125, 0x04: 250, 0x02: 500, 0x01: 1000, 0x10: 2000, 0x20: 4000, 0x40: 8000}
FREQS = [0x005E, 0x00BD, 0x0177, 0x02EE, 0x05DC, 0x0BB8, 0x1770, 0x2EE0, 0x5DC0, 0xBB80]


def mouse_frame(cmd, addr, data=b""):
    core = bytes([cmd, 0, (addr >> 8) & 0xFF, addr & 0xFF, len(data)]) + data
    core = core[:15].ljust(15, b"\x00")
    chk = (0x55 - ((0x08 + sum(core)) & 0xFF)) & 0xFF
    return bytes([0x08]) + core + bytes([chk])


def mouse_open():
    for path in pm.interfaces():
        if "vid_3554&pid_f58e" not in path.lower():
            continue
        h, caps = pm.caps_for(path)
        if caps and caps.UsagePage == 0xFF02 and caps.InputReportByteLength == 17 \
                and caps.OutputReportByteLength == 17:
            return h
    return None


def mouse_io(h, frame, write=True, timeout_ms=1000, read_ms=1500):
    _, err = pm.do_io(h, frame, write, timeout_ms)
    if err:
        raise RuntimeError(err)
    time.sleep(0.04)
    data, err = pm.do_io(h, bytes(17), False, read_ms)
    if err:
        raise RuntimeError(err)
    if (sum(data) & 0xFF) != 0x55:
        raise RuntimeError("checksum")
    return data


def mouse_read():
    last = None
    for attempt in range(2):
        h = mouse_open()
        if not h:
            raise RuntimeError("mouse tidak ditemukan / sleep")
        try:
            def io(frame):
                # mouse yang tidur tidak boleh menahan API belasan detik
                return mouse_io(h, frame, timeout_ms=400, read_ms=700)

            out = {}
            r = io(bytes([0x08, 0x04] + [0] * 14 + [0x49]))
            out["battery"] = r[6]
            out["charging"] = bool(r[7])
            out["mv"] = (r[8] << 8) | r[9]

            r = io(mouse_frame(0x08, 0x0000, b"\x00" * 10))
            d = r[6:16]
            pairs = [(d[i], d[i + 1]) for i in range(0, 10, 2)]
            out["polling"] = POLL_CODES.get(pairs[0][0], 1000)
            out["activeStage"] = pairs[2][0] if len(pairs) > 2 else 1

            r = io(mouse_frame(0x08, 0x000A, b"\x00" * 10))
            out["lod"] = r[6] if r[6] in (1, 2) else 1

            r = io(mouse_frame(0x08, 0x0070, b"\x00" * 10))
            payload = r[6:16]
            for i in range(0, 10, 4):
                g = payload[i:i + 4]
                if len(g) == 4 and (sum(g) & 0xFF) == 0x55 and g[0] == 0x02:
                    out["debounce"] = g[1]
                    break
            return out
        except Exception as exc:
            last = exc
            time.sleep(0.25)
        finally:
            pm.k32.CloseHandle(h)
    raise last


def tws_open():
    h = pe.k32.CreateFileW("\\\\.\\COM3", 0x80000000 | 0x40000000,
                           0, None, 3, 0, None)
    if h in (None, ctypes_invalid()):
        raise RuntimeError("COM3 tidak tersedia")
    pe.k32.SetCommState(h, pe.make_dcb())
    pe.k32.SetCommTimeouts(h, ctypes.byref(pe.CommTimeouts(30, 0, 900, 0, 900)))
    return h


def ctypes_invalid():
    return pe.ctypes.c_void_p(-1).value


def tws_query(h, cmd):
    frames, err = pe.exchange(h, cmd, b"", 1.2)
    if err or not frames or len(frames[0][3]) < 2:
        raise RuntimeError(err or "no reply")
    return frames[0][3][1]


def tws_read():
    h = tws_open()
    try:
        out = {
            "left": tws_query(h, 0x0306),
            "right": tws_query(h, 0x0307),
            "caseBat": tws_query(h, 0x0317),
            "noiseMode": tws_query(h, 0x0315),
            "ancSub": tws_query(h, 0x033B),
            "ambSub": tws_query(h, 0x033D),
            "game": bool(tws_query(h, 0x0313)),
            "inEar": bool(tws_query(h, 0x034A)),
            "gestureLock": bool(tws_query(h, 0x0335)),
            "codec": tws_query(h, 0x032F),
            "mic": tws_query(h, 0x0331),
            "prompt": tws_query(h, 0x0339),
        }
        if out["caseBat"] == 0xFF:
            out["caseBat"] = None
        return out
    finally:
        pe.k32.CloseHandle(h)


def mouse_polling_code(hz):
    for code, value in POLL_CODES.items():
        if value == hz:
            return code
    return 0x01


def mouse_write(key, value):
    h = mouse_open()
    if not h:
        raise RuntimeError("mouse tidak ditemukan / sleep")
    try:
        if key == "polling":
            r = mouse_io(h, mouse_frame(0x08, 0x0000, b"\x00" * 10))
            d = bytearray(r[6:16])
            code = mouse_polling_code(int(value))
            d[0] = code
            d[1] = (0x55 - code) & 0xFF
            mouse_io(h, mouse_frame(0x07, 0x0000, bytes(d)), True)
            return mouse_io(h, mouse_frame(0x08, 0x0000, b"\x00" * 10))[6]
        if key in ("lod", "debounce"):
            sel = 0x03 if key == "lod" else 0x02
            v = int(value)
            pair = bytes([sel, v, 0x00, (0x55 - sel - v) & 0xFF])
            mouse_io(h, mouse_frame(0x07, 0x0070, pair), True)
            return v
        raise RuntimeError("mouse key tidak didukung: " + key)
    finally:
        pm.k32.CloseHandle(h)


TWS_SET = {
    "noiseMode": 0x0314,
    "ancSub": 0x033A,
    "ambSub": 0x033C,
    "game": 0x0312,
    "inEar": 0x0349,
    "gestureLock": 0x0334,
    "mic": 0x0330,
    "prompt": 0x0338,
    "findDevice": 0x0332,
}
TWS_QUERY = {
    "noiseMode": 0x0315,
    "ancSub": 0x033B,
    "ambSub": 0x033D,
    "game": 0x0313,
    "inEar": 0x034A,
    "gestureLock": 0x0335,
    "mic": 0x0331,
    "prompt": 0x0339,
    "findDevice": 0x0333,
}

GESTURE_TYPES = [1, 1, 2, 2, 3, 3, 17, 17]


def tws_write_gesture(actions):
    h = tws_open()
    try:
        for i, action in enumerate(actions[:8]):
            t = GESTURE_TYPES[i]
            payload = bytes([t, int(action), 0, 0]) if i % 2 == 0 else bytes([0, 0, t, int(action)])
            pe.exchange(h, 0x030A, payload, 1.2)
            time.sleep(0.12)
        return len(actions[:8])
    finally:
        pe.k32.CloseHandle(h)


def tws_write_eq(values):
    h = tws_open()
    try:
        for i, v in enumerate(values):
            gain = int(round(float(v) * 36))
            signed = struct.pack(">h", gain)
            payload = bytes([0xA1 + i, 0xFF, 0x98]) + struct.pack(">H", FREQS[i]) \
                + signed + struct.pack(">H", 0x0B33)
            frame = bytes([0xFF, 0x04, 0x00, len(payload), 0x00, 0x1D, 0x0E, 0x01]) + payload
            n = pe.k32.c_ulong()
            ok = pe.k32.WriteFile(h, frame, len(frame), ctypes.byref(n), None)
            if not ok:
                raise RuntimeError("EQ write gagal pada band " + str(i))
            time.sleep(0.03)
        return len(values)
    finally:
        pe.k32.CloseHandle(h)


def tws_write(key, value):
    if key == "eq":
        return tws_write_eq(value)
    if key == "gesture":
        return tws_write_gesture(value)
    if key not in TWS_SET:
        raise RuntimeError("TWS key tidak didukung / berisiko: " + key)
    h = tws_open()
    try:
        cmd = TWS_SET[key]
        v = 1 if value is True else 0 if value is False else int(value)
        pe.exchange(h, cmd, bytes([v]), 1.2)
        time.sleep(0.35)
        return tws_query(h, TWS_QUERY[key])
    finally:
        pe.k32.CloseHandle(h)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def send_json(self, obj, code=200):
        body = json.dumps(obj).encode()
        try:
            self.send_response(code)
            self.cors()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()
        except OSError:
            # klien (browser/poll) membatalkan koneksi sebelum body terkirim
            self.close_connection = True

    def do_OPTIONS(self):
        self.send_response(204)
        self.cors()
        self.end_headers()

    def do_GET(self):
        if self.path != "/api/status":
            self.send_json({"error": "not found"}, 404)
            return
        refresh_if_due("mouse", mouse_read)
        refresh_if_due("tws", tws_read)
        result = {
            "mouse": dict(CACHE["mouse"]),
            "tws": dict(CACHE["tws"]),
            "errors": dict(CACHE_ERR),
            "connected": {name: is_connected(name) for name in CACHE},
        }
        self.send_json(result)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            self.send_json({"error": "invalid json"}, 400)
            return
        parts = self.path.strip("/").split("/")
        if len(parts) != 2 or parts[0] != "api" or parts[1] not in ("mouse", "tws"):
            self.send_json({"error": "not found"}, 404)
            return
        device = parts[1]
        try:
            with LOCK[device]:
                if device == "mouse":
                    value = mouse_write(body.get("key"), body.get("value"))
                    CACHE["mouse"][body["key"]] = value
                else:
                    value = tws_write(body.get("key"), body.get("value"))
                    if body["key"] in TWS_QUERY:
                        CACHE["tws"][body["key"]] = value
            self.send_json({"ok": True, "readback": value})
        except Exception as exc:
            CACHE_ERR[device] = str(exc)
            self.send_json({"error": str(exc)}, 500)


class QuietServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        # jangan tumpahkan traceback saat klien memutus koneksi
        pass


if __name__ == "__main__":
    print(f"Device bridge listening on http://127.0.0.1:{PORT}", flush=True)
    QuietServer(("127.0.0.1", PORT), Handler).serve_forever()
