#!/usr/bin/env python3
"""Uji write EEPROM system row 0x0000 (polling) dengan restore penuh."""
import ctypes
import sys
import time
from probe_mouse import interfaces, caps_for, do_io


def build(cmd, addr, data=b""):
    core = bytes([cmd, 0, (addr >> 8) & 0xFF, addr & 0xFF, len(data)]) + data
    core = core[:15].ljust(15, b"\x00")
    chk = (0x55 - ((0x08 + sum(core)) & 0xFF)) & 0xFF
    return bytes([0x08]) + core + bytes([chk])


def io(h, frame, label):
    _, e = do_io(h, frame, True)
    if e:
        print("  WRITE ERR", label, e)
        return None
    time.sleep(0.06)
    data, e = do_io(h, bytes(17), False, 1200)
    if e:
        print("  READ ERR", label, e)
        return None
    if (sum(data) & 0xFF) != 0x55:
        print("  CHECKSUM GAGAL", label)
        return None
    return data[6:16]


def main():
    h = None
    for path in interfaces():
        if "vid_3554&pid_f58e" not in path.lower():
            continue
        hh, caps = caps_for(path)
        if caps and caps.UsagePage == 0xFF02 and caps.InputReportByteLength == 17 \
                and caps.OutputReportByteLength == 17:
            h = hh
            break
    if not h:
        print("Mouse tidak merespons")
        return 2

    base = io(h, build(0x08, 0x0000, b"\x00" * 10), "read system")
    if not base:
        return 2
    print("BASELINE :", base.hex(" "))

    # polling code 01 = 1000 Hz -> 02 = 500 Hz
    modified = bytes([0x02, 0x53]) + base[2:]
    print("TULIS    :", modified.hex(" "))
    ack = io(h, build(0x07, 0x0000, modified), "write system")
    print("ACK      :", ack.hex(" ") if ack else "GAGAL")
    time.sleep(0.3)
    got = io(h, build(0x08, 0x0000, b"\x00" * 10), "readback")
    print("READBACK :", got.hex(" ") if got else "GAGAL")
    print("HASIL    :", "COCOK" if got == modified else "BEDA")

    print("RESTORE  :", io(h, build(0x07, 0x0000, base), "restore") is not None)
    time.sleep(0.3)
    final = io(h, build(0x08, 0x0000, b"\x00" * 10), "verify")
    print("VERIFY   :", final.hex(" ") if final else "GAGAL",
          "OK" if final == base else "GAGAL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
