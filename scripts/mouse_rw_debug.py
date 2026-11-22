#!/usr/bin/env python3
"""Dump frame mentah untuk mendiagnosis write activeStage/sleep/dpiStage."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bridge  # noqa: E402
import probe_mouse as pm  # noqa: E402


def hexs(b):
    return " ".join("%02x" % x for x in b)


def wait_ready(limit=900):
    t0 = time.monotonic()
    while time.monotonic() - t0 < limit:
        try:
            return bridge.mouse_read()
        except Exception:
            time.sleep(1.5)
    raise SystemExit("mouse tak bangun")


def main():
    base = wait_ready()
    print("baseline:", json.dumps(base), flush=True)
    h = bridge.mouse_open()
    if not h:
        raise SystemExit("mouse hilang")

    def raw(addr, data=b"\x00" * 4, label=""):
        r = bridge.mouse_io(h, bridge.mouse_frame(0x08, addr, data))
        print("READ  %04X %-10s %s" % (addr, label, hexs(r)), flush=True)
        return r

    def wr(addr, data, label=""):
        bridge.mouse_io(h, bridge.mouse_frame(0x07, addr, data), True)
        print("WRITE %04X %-10s %s" % (addr, label, hexs(data)), flush=True)

    try:
        print("\n=== 000C DPI stage 0 ===", flush=True)
        raw(0x000C, b"\x00" * 4, "sebelum")
        wr(0x000C, bytes([10, 10, 0, (0x55 - 20) & 0xFF]), "dpi500")
        time.sleep(0.2)
        raw(0x000C, b"\x00" * 4, "0.2s")
        time.sleep(1.0)
        raw(0x000C, b"\x00" * 4, "1.2s")
        wr(0x000C, bytes([9, 9, 0, (0x55 - 18) & 0xFF]), "dpi450")
        time.sleep(0.2)
        raw(0x000C, b"\x00" * 4, "0.2s")
        time.sleep(1.0)
        raw(0x000C, b"\x00" * 4, "1.2s")

        print("\n=== 0000 activeStage ===", flush=True)
        r = raw(0x0000, b"\x00" * 10, "sebelum")
        d = bytearray(r[6:16])
        d[4] = 1
        d[5] = (0x55 - 1) & 0xFF
        wr(0x0000, bytes(d), "stage1")
        time.sleep(0.2)
        raw(0x0000, b"\x00" * 10, "0.2s")
        time.sleep(1.0)
        raw(0x0000, b"\x00" * 10, "1.2s")
        d[4] = 0
        d[5] = 0x55
        wr(0x0000, bytes(d), "stage0")
        time.sleep(0.2)
        raw(0x0000, b"\x00" * 10, "0.2s")
        time.sleep(1.0)
        raw(0x0000, b"\x00" * 10, "1.2s")

        print("\n=== 00B5 sleep ===", flush=True)
        r = raw(0x00B5, b"\x00" * 6, "sebelum")
        d = bytearray(r[6:12])
        d[2] = 6
        d[3] = (0x55 - 6) & 0xFF
        wr(0x00B5, bytes(d), "sleep60")
        time.sleep(0.2)
        raw(0x00B5, b"\x00" * 6, "0.2s")
        time.sleep(1.0)
        raw(0x00B5, b"\x00" * 6, "1.2s")
        d[2] = 3
        d[3] = (0x55 - 3) & 0xFF
        wr(0x00B5, bytes(d), "sleep30")
        time.sleep(0.2)
        raw(0x00B5, b"\x00" * 6, "0.2s")
        time.sleep(1.0)
        raw(0x00B5, b"\x00" * 6, "1.2s")
        d[2] = 6
        d[3] = (0x55 - 6) & 0xFF
        wr(0x00B5, bytes(d), "sleep60-akhir")
        time.sleep(0.2)
        raw(0x00B5, b"\x00" * 6, "0.2s")
    finally:
        pm.k32.CloseHandle(h)
    after = wait_ready()
    print("\nafter:", json.dumps(after), flush=True)
    print("IDENTIK:", after == base, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
