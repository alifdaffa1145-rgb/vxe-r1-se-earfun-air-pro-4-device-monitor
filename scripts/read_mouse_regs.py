#!/usr/bin/env python3
"""Baca register konfigurasi mouse VXE R1 SE+ (read-only, aman).

Jalankan setelah mouse digerakkan fisik supaya receiver bangun.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bridge  # noqa: E402

REGS = [
    0x0000, 0x000A, 0x000C, 0x002C, 0x004C, 0x0060,
    0x0070, 0x00A9, 0x00B5, 0x00BD,
]


def main():
    h = bridge.mouse_open()
    if not h:
        raise SystemExit("mouse tidak ditemukan / sedang tidur — gerakkan dulu")
    try:
        for addr in REGS:
            try:
                r = bridge.mouse_io(h, bridge.mouse_frame(0x08, addr, b"\x00" * 10))
                print("%04X  %s" % (addr, r.hex(" ")))
            except Exception as exc:
                print("%04X  ERR %s" % (addr, exc))
    finally:
        bridge.pm.k32.CloseHandle(h)


if __name__ == "__main__":
    main()
