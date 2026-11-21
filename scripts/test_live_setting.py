#!/usr/bin/env python3
"""Uji satu live-setting mouse: baca -> tulis -> readback -> restore -> verify.

Pemakaian: python3 test_live_setting.py <selector_hex> <nilai_uji>
Contoh:    python3 test_live_setting.py 01 00
"""
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
    time.sleep(0.05)
    data, e = do_io(h, bytes(17), False, 1200)
    if e:
        print("  READ ERR", label, e)
        return None
    if (sum(data) & 0xFF) != 0x55:
        print("  CHECKSUM GAGAL", label, " ".join("%02X" % x for x in data))
        return None
    return data


def groups(data):
    """Ambil grup 4 byte dari payload mulai index 6 yang jumlahnya 0x55."""
    out = []
    payload = data[6:16]
    for i in range(0, 10, 4):
        g = payload[i:i + 4]
        if len(g) == 4 and (sum(g) & 0xFF) == 0x55:
            out.append((g[0], g[1], g.hex()))
    return out


def main():
    selector = int(sys.argv[1], 16)
    test = int(sys.argv[2], 16)
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
        print("Mouse tidak merespons (mungkin sleep)")
        return 2

    print("BACA 0070...")
    row = io(h, build(0x08, 0x0070, b"\x00" * 10), "read")
    if row is None:
        return 2
    print("  grup:", groups(row))

    current = next((v for s, v, raw in groups(row) if s == selector), None)
    if current is None:
        print("Selector %02X tidak ada di row" % selector)
        return 3
    print("Selector %02X nilai awal = %d (0x%02X)" % (selector, current, current))

    pair = bytes([selector, test, 0x00, (0x55 - selector - test) & 0xFF])
    print("TULIS", pair.hex(" "), "->", io(h, build(0x07, 0x0070, pair), "write") is not None)
    time.sleep(0.25)
    after = io(h, build(0x08, 0x0070, b"\x00" * 10), "readback")
    if after is None:
        print("readback gagal")
    else:
        print("  grup sesudah:", groups(after))
        got = next((v for s, v, raw in groups(after) if s == selector), None)
        print("  HASIL: %s" % ("COCOK" if got == test else "BEDA (got=%r)" % got))

    restore = bytes([selector, current, 0x00, (0x55 - selector - current) & 0xFF])
    io(h, build(0x07, 0x0070, restore), "restore")
    time.sleep(0.25)
    final = io(h, build(0x08, 0x0070, b"\x00" * 10), "verify")
    print("RESTORE:", groups(final) if final else "gagal")
    return 0


if __name__ == "__main__":
    sys.exit(main())
