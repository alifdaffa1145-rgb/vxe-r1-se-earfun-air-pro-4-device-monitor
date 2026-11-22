#!/usr/bin/env python3
"""Uji mouse_io match=True untuk request battery (cmd 0x04)."""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bridge  # noqa: E402
import probe_mouse as pm  # noqa: E402


def hexs(b):
    return " ".join("%02x" % x for x in b) if b else "-"


def main():
    h = bridge.mouse_open()
    print("handle:", h, flush=True)
    if not h:
        return 2
    try:
        req = bytes([0x08, 0x04] + [0x00] * 14 + [0x49])
        for i in range(4):
            print("--- percobaan", i, flush=True)
            _, err = pm.do_io(h, req, True, 1000)
            print("  write err:", err, flush=True)
            time.sleep(0.04)
            data, err = pm.do_io(h, bytes(17), False, 1500)
            print("  read err:", err, "data:", hexs(data), flush=True)
            if data:
                print("  cmd=%02x addr=%04x sum=%02x" % (
                    data[1], (data[4] << 8) | data[5], sum(data) & 0xFF), flush=True)
            try:
                r = bridge.mouse_io(h, req, True, 1000, 700, match=True)
                print("  mouse_io OK:", hexs(r), flush=True)
            except Exception as exc:
                print("  mouse_io GAGAL:", exc, flush=True)
            time.sleep(0.5)
    finally:
        pm.k32.CloseHandle(h)
    return 0


if __name__ == "__main__":
    sys.exit(main())
