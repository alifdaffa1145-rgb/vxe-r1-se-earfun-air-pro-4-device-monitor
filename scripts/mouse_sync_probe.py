#!/usr/bin/env python3
"""Probe sinkronisasi frame: apakah 1 write -> 1 read selalu sinkron?"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bridge  # noqa: E402
import probe_mouse as pm  # noqa: E402


def hexs(b):
    return " ".join("%02x" % x for x in b)


def addr_of(d):
    if not d or len(d) < 6:
        return "?"
    return "%02x/%04x" % (d[1], (d[4] << 8) | d[5])


def main():
    try:
        bridge.mouse_read()
    except Exception as exc:
        print("bangun gagal:", exc, flush=True)
        return 2
    h = bridge.mouse_open()
    if not h:
        print("mouse hilang", flush=True)
        return 2
    try:
        print("=== 8x request 0000, tanpa flush ===", flush=True)
        for i in range(8):
            f = bridge.mouse_frame(0x08, 0x0000, b"\x00" * 10)
            bridge.mouse_io(h, f, True)
            print("%d -> %s" % (i, addr_of(bridge.mouse_io(h, f, False, 1000, 400))), flush=True)

        print("\n=== flush lalu request 0000 (read 60ms buang sisa) ===", flush=True)
        for i in range(6):
            for _ in range(20):
                d, err = pm.do_io(h, bytes(17), False, 60)
                if err:
                    break
                print("   buang:", addr_of(d), flush=True)
            f = bridge.mouse_frame(0x08, 0x0000, b"\x00" * 10)
            bridge.mouse_io(h, f, True)
            print("%d -> %s" % (i, addr_of(bridge.mouse_io(h, f, False, 1000, 400))), flush=True)
            time.sleep(0.1)

        print("\n=== tulis 0x07 0000, semua frame setelahnya ===", flush=True)
        r = bridge.mouse_io(h, bridge.mouse_frame(0x08, 0x0000, b"\x00" * 10))
        print("read awal:", addr_of(r), flush=True)
        d = bytearray(r[6:16])
        d[4] = 1
        d[5] = (0x55 - 1) & 0xFF
        bridge.mouse_io(h, bridge.mouse_frame(0x07, 0x0000, bytes(d)), True)
        for i in range(6):
            data, err = pm.do_io(h, bytes(17), False, 250)
            print("sisa %d: %s %s" % (i, addr_of(data) if data else "-", err or ""), flush=True)
            if err:
                break
    finally:
        pm.k32.CloseHandle(h)
    return 0


if __name__ == "__main__":
    sys.exit(main())
