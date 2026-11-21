#!/usr/bin/env python3
"""Verifikasi protokol konfigurasi 0xFF02 mouse VXE R1 SE+.

Frame 17 byte: 08 <cmd> <status> <addr_hi> <addr_lo> <len> <data...> <checksum>
Jumlah ke-17 byte == 0x55 (mod 256). Read cmd=0x08, write cmd=0x07.
Jalankan tanpa argumen = baca saja. Tambah --write = uji tulis+readback+restore.
"""
import sys
import time
from probe_mouse import interfaces, caps_for, do_io

REGS = {
    "system": 0x0000,
    "lod": 0x000A,
    "dpi": 0x000C,
    "colors": 0x002C,
    "led": 0x004C,
    "live": 0x0070,
    "advanced": 0x00A9,
    "sensor": 0x00B5,
    "angle": 0x00BD,
    "buttons": 0x0060,
}


def build(cmd, addr, data=b"", status=0):
    length = len(data)
    core = bytes([cmd, status, (addr >> 8) & 0xFF, addr & 0xFF, length]) + data
    core = core[:15].ljust(15, b"\x00")
    checksum = (0x55 - ((0x08 + sum(core)) & 0xFF)) & 0xFF
    frame = bytes([0x08]) + core + bytes([checksum])
    assert len(frame) == 17 and (sum(frame) & 0xFF) == 0x55
    return frame


def hx(b):
    return " ".join("%02X" % x for x in b)


def open_target():
    for path in interfaces():
        low = path.lower()
        if "vid_3554&pid_f58e" not in low:
            continue
        h, caps = caps_for(path)
        if caps and caps.UsagePage == 0xFF02 and caps.InputReportByteLength == 17 \
                and caps.OutputReportByteLength == 17:
            return h, path
    return None, None


def transact(h, frame, label):
    out, err = do_io(h, frame, True)
    if err:
        print("  WRITE ERR", label, err)
        return None
    time.sleep(0.04)
    inp, err = do_io(h, bytes(17), False, 1200)
    if err:
        print("  READ ERR ", label, err)
        return None
    ok = (sum(inp) & 0xFF) == 0x55
    print("  %-10s TX %s" % (label, hx(frame)))
    print("  %-10s RX %s  checksum=%s" % ("", hx(inp), "OK" if ok else "GAGAL"))
    return inp if ok else None


def main():
    do_write = "--write" in sys.argv
    h, path = open_target()
    if not h:
        print("Tidak find koleksi 0xFF02 17/17")
        return 1
    print("Koleksi:", path[:100])

    baseline = {}
    for name, addr in REGS.items():
        print("\nREAD", name, hex(addr))
        r = transact(h, build(0x08, addr, b"\x00" * 10), name)
        if r:
            baseline[name] = r

    if not do_write:
        print("\nMode baca-saja. Tidak ada perubahan.")
        return 0

    # Uji tulis live-setting LOD: selector 0x03, nilai 1 -> 2 -> 1
    # Baris live = [selector, value, 0x00, (0x55-value)&0xff]
    print("\n=== UJI TULIS: LOD live-setting selector 0x03 ===")
    for value in (2, 1):
        pair = bytes([0x03, value, 0x00, (0x55 - 0x03 - value) & 0xFF])
        print("Tulis nilai", value)
        r = transact(h, build(0x07, 0x0070, pair), "write LOD")
        time.sleep(0.15)
        transact(h, build(0x08, 0x0070, b"\x00" * 10), "readback")
    print("\nSelesai; nilai akhir dikembalikan ke 1.")

    # Uji tulis live-setting debounce: selector 0x02, nilai 8 -> 9 -> 8
    print("\n=== UJI TULIS: debounce selector 0x02 ===")
    for value in (9, 8):
        pair = bytes([0x02, value, 0x00, (0x55 - 0x02 - value) & 0xFF])
        print("Tulis nilai", value)
        transact(h, build(0x07, 0x0070, pair), "write debounce")
        time.sleep(0.15)
        transact(h, build(0x08, 0x0070, b"\x00" * 10), "readback")
    print("\nSelesai; nilai akhir dikembalikan ke 8.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
