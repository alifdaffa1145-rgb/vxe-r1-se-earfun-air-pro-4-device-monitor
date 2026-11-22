#!/usr/bin/env python3
"""Probe write reversible untuk mouse VXE R1 SE+ (0xFF02).

Alur:
1. Tunggu mouse bangun (gerakkan fisik).
2. Naikkan sleep timer 0x00B5 byte 2 -> 180 (1800 s) supaya mouse tak tidur.
3. Uji write tiap field: tulis -> readback -> restore baseline.
4. Kembalikan sleep timer ke nilai semula.

Output: JSON di argv[1] (default scratch).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bridge  # noqa: E402

PM = bridge.pm
K32 = PM.k32
INVALID = PM.ctypes.c_void_p(-1).value


def open_mouse():
    for _ in range(3):
        h = bridge.mouse_open()
        if h:
            return h
        time.sleep(1)
    return None


def read(h, addr, length=10):
    r = bridge.mouse_io(h, bridge.mouse_frame(0x08, addr, b"\x00" * length))
    return r[6:6 + length]


def write(h, addr, data, settle=0.35):
    bridge.mouse_io(h, bridge.mouse_frame(0x07, addr, bytes(data)))
    time.sleep(settle)
    return read(h, addr, len(data))


def wait_awake(limit=900):
    """Tunggu mouse bangun stabil (2x read berurutan sukses), handle tetap hidup."""
    t0 = time.monotonic()
    stable = 0
    ready = None
    while time.monotonic() - t0 < limit:
        h = open_mouse()
        if not h:
            stable = 0
            time.sleep(1.0)
            continue
        try:
            read(h, 0x0000, 10)
            read(h, 0x00B5, 10)
            read(h, 0x0070, 10)
            stable += 1
            if stable >= 2:
                print("mouse bangun stabil", flush=True)
                ready = h
                break
        except Exception:
            stable = 0
        finally:
            if ready is None:
                try:
                    K32.CloseHandle(h)
                except Exception:
                    pass
        time.sleep(1.2)
    return ready


def pair(value):
    return [value & 0xFF, (0x55 - value) & 0xFF]


def main():
    out = {"baseline": {}, "tests": []}
    h = wait_awake()
    if not h:
        print("mouse tak pernah bangun", flush=True)
        return 1
    try:
        for addr in (0x0000, 0x000A, 0x000C, 0x002C, 0x0040, 0x004C,
                     0x0060, 0x0070, 0x00A9, 0x00B5, 0x00BD):
            try:
                out["baseline"]["%04X" % addr] = read(h, addr, 10).hex()
            except Exception as exc:
                out["baseline"]["%04X" % addr] = "ERR " + str(exc)

        for k, v in out["baseline"].items():
            if str(v).startswith("ERR"):
                print("baseline gagal (%s = %s) — mouse tidur; jalankan lagi" % (k, v), flush=True)
                return 2

        b = bytes.fromhex(out["baseline"]["00B5"][:12])  # 6 byte
        print("00B5 baseline:", b.hex(" "), flush=True)

        # 1) sleep timer 60s -> 1800s
        old = b[2]
        target = 180
        b2 = bytearray(b)
        b2[2:4] = bytes(pair(target))
        rb = write(h, 0x00B5, b2)
        out["tests"].append({"name": "sleep", "addr": "00B5", "old": old,
                             "new": target, "readback": rb.hex()})
        print("sleep ->", target, "readback", rb.hex(" "), flush=True)

        # 2) motion sync 00A9 byte 2 (1 -> 0 -> 1)
        a = bytearray.fromhex(out["baseline"]["00A9"][:20])
        old = a[2]
        a[2:4] = bytes(pair(0))
        rb = write(h, 0x00A9, a)
        out["tests"].append({"name": "motionSync", "addr": "00A9", "old": old,
                             "new": 0, "readback": rb.hex()})
        print("motion -> 0 readback", rb.hex(" "), flush=True)
        write(h, 0x00A9, bytearray.fromhex(out["baseline"]["00A9"][:20]))

        # 3) angle snap 00BD byte 2 (0xFF -> 1 -> 0xFF)
        g = bytearray.fromhex(out["baseline"]["00BD"][:8])
        old = g[2]
        g[2:4] = bytes(pair(1))
        rb = write(h, 0x00BD, g)
        out["tests"].append({"name": "angleSnap", "addr": "00BD", "old": old,
                             "new": 1, "readback": rb.hex()})
        print("angle -> 1 readback", rb.hex(" "), flush=True)
        write(h, 0x00BD, bytearray.fromhex(out["baseline"]["00BD"][:8]))

        # 4) LED effect 004C byte 0 (0x02 -> 0x01 -> 0x02)
        l = bytearray.fromhex(out["baseline"]["004C"][:20])
        old = l[0]
        l[0:2] = bytes(pair(1))
        rb = write(h, 0x004C, l)
        out["tests"].append({"name": "ledEffect", "addr": "004C", "old": old,
                             "new": 1, "readback": rb.hex()})
        print("led -> 1 readback", rb.hex(" "), flush=True)
        write(h, 0x004C, bytearray.fromhex(out["baseline"]["004C"][:20]))

        # 5) active DPI stage 0000 byte 4 (1 -> 0 -> 1)
        s = bytearray.fromhex(out["baseline"]["0000"][:20])
        old = s[4]
        s[4:6] = bytes(pair(0))
        rb = write(h, 0x0000, s)
        out["tests"].append({"name": "activeStage", "addr": "0000", "old": old,
                             "new": 0, "readback": rb.hex()})
        print("stage -> 0 readback", rb.hex(" "), flush=True)
        write(h, 0x0000, bytearray.fromhex(out["baseline"]["0000"][:20]))

        # 6) DPI stage 1 byte 0 (0x09 -> 0x0A -> 0x09)
        d = bytearray.fromhex(out["baseline"]["000C"][:8])
        old = d[0]
        d[0] = 0x0A
        d[3] = (0x55 - d[0] - d[1]) & 0xFF
        rb = write(h, 0x000C, d)
        out["tests"].append({"name": "dpiStage1", "addr": "000C", "old": old,
                             "new": 0x0A, "readback": rb.hex()})
        print("dpi -> 0A readback", rb.hex(" "), flush=True)
        write(h, 0x000C, bytearray.fromhex(out["baseline"]["000C"][:8]))

        # 7) kembalikan sleep ke baseline
        b3 = bytearray(b)
        b3[2:4] = bytes(pair(old_sleep := b[2]))
        rb = write(h, 0x00B5, b3)
        out["tests"].append({"name": "sleepRestore", "addr": "00B5",
                             "readback": rb.hex()})
        print("sleep restore", rb.hex(" "), flush=True)

        path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "mouse_probe.json")
        with open(path, "w") as fh:
            json.dump(out, fh, indent=1)
        print("SELESAI, hasil:", path, flush=True)
        return 0
    finally:
        try:
            K32.CloseHandle(h)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
