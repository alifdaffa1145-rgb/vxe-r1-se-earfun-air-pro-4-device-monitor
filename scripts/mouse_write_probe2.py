#!/usr/bin/env python3
"""Uji ulang write active stage & DPI stage dengan baca ganda (readback ACK-safe).

Jalankan: python mouse_write_probe2.py <output.json>
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bridge  # noqa: E402

K32 = bridge.pm.k32
PM = bridge.pm


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


def read2(h, addr, length=10):
    """Dua bacaan; readback pertama sering berisi ACK."""
    a = read(h, addr, length)
    time.sleep(0.12)
    b = read(h, addr, length)
    return a, b


def write(h, addr, data, settle=0.35):
    bridge.mouse_io(h, bridge.mouse_frame(0x07, addr, bytes(data)))
    time.sleep(settle)


def pair(value):
    return [value & 0xFF, (0x55 - value) & 0xFF]


def wait_awake(limit=900):
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
            stable += 1
            if stable >= 2:
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


def main():
    out = {"baseline": {}, "tests": []}
    h = wait_awake()
    if not h:
        print("mouse tak bangun", flush=True)
        return 1
    try:
        for addr in (0x0000, 0x000C, 0x00A9, 0x00B5, 0x00BD, 0x004C):
            out["baseline"]["%04X" % addr] = read(h, addr, 10).hex()

        b = bytearray(bytes.fromhex(out["baseline"]["00B5"][:12]))
        b[2:4] = bytes(pair(180))
        write(h, 0x00B5, b)
        print("sleep -> 180", read2(h, 0x00B5, 6), flush=True)

        # active stage: 0000 byte 4
        s = bytearray.fromhex(out["baseline"]["0000"][:20])
        old = s[4]
        s[4:6] = bytes(pair(0))
        write(h, 0x0000, s)
        a, b2 = read2(h, 0x0000, 10)
        out["tests"].append({"name": "activeStage", "old": old, "new": 0,
                             "read1": a.hex(), "read2": b2.hex()})
        print("activeStage -> 0:", a.hex(), b2.hex(), flush=True)
        write(h, 0x0000, bytearray.fromhex(out["baseline"]["0000"][:20]))
        print("activeStage restore:", read2(h, 0x0000, 10), flush=True)

        # DPI stage 1: 000C byte 0
        d = bytearray.fromhex(out["baseline"]["000C"][:8])
        old_d = d[0]
        d[0] = 0x0A
        d[3] = (0x55 - d[0] - d[1]) & 0xFF
        write(h, 0x000C, d)
        a, b2 = read2(h, 0x000C, 4)
        out["tests"].append({"name": "dpiStage1", "old": old_d, "new": 0x0A,
                             "read1": a.hex(), "read2": b2.hex()})
        print("dpi -> 0A:", a.hex(), b2.hex(), flush=True)
        write(h, 0x000C, bytearray.fromhex(out["baseline"]["000C"][:8]))
        print("dpi restore:", read2(h, 0x000C, 4), flush=True)

        # angle snap: coba nilai 2
        g = bytearray.fromhex(out["baseline"]["00BD"][:8])
        g[2:4] = bytes(pair(2))
        write(h, 0x00BD, g)
        a, b2 = read2(h, 0x00BD, 4)
        out["tests"].append({"name": "angleSnap2", "new": 2,
                             "read1": a.hex(), "read2": b2.hex()})
        print("angle -> 2:", a.hex(), b2.hex(), flush=True)
        write(h, 0x00BD, bytearray.fromhex(out["baseline"]["00BD"][:8]))
        print("angle restore:", read2(h, 0x00BD, 4), flush=True)

        # sleep restore
        b3 = bytearray(bytes.fromhex(out["baseline"]["00B5"][:12]))
        write(h, 0x00B5, b3)
        print("sleep restore:", read2(h, 0x00B5, 6), flush=True)

        path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "mouse_probe2.json")
        with open(path, "w") as fh:
            json.dump(out, fh, indent=1)
        print("SELESAI:", path, flush=True)
        return 0
    finally:
        try:
            K32.CloseHandle(h)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
