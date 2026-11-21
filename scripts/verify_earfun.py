#!/usr/bin/env python3
"""Verifikasi end-to-end konflik protokol EarFun Air Pro 4 di COM3.

Untuk setiap perintah: baca baseline -> tulis nilai uji -> baca balik ->
kembalikan ke baseline -> baca lagi. Tidak menyentuh factory reset, codec,
multipoint, atau find-device (berisiko reboot / suara keras).
"""
import ctypes
import ctypes.wintypes as wt
import sys
import time
import probe_earbud as pe

k32 = pe.k32
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
INVALID = ctypes.c_void_p(-1).value


def val(frames):
    for ver, vendor, cmd, payload in frames:
        if len(payload) >= 2 and payload[0] == 0x00:
            return payload[1]
    if frames:
        return ("RAW", frames[0][2], frames[0][3].hex())
    return None


def query(h, cmd, wait=1.0):
    frames, err = pe.exchange(h, cmd, b"", wait)
    if err:
        return "ERR " + err
    return val(frames)


def write(h, cmd, value, wait=0.9):
    frames, err = pe.exchange(h, cmd, bytes([value]), wait)
    if err:
        return "ERR " + err
    return val(frames)


def trial(h, name, qcmd, scmd, test_value):
    base = query(h, qcmd)
    print("\n%s: baseline=%r" % (name, base))
    if base is None or isinstance(base, str) or not isinstance(base, int):
        print("  SKIP (baseline tidak bisa dibaca)")
        return
    print("  tulis %d -> ack/rx=%r" % (test_value, write(h, scmd, test_value)))
    time.sleep(0.15)
    got = query(h, qcmd)
    print("  readback=%r %s" % (got, "COCOK" if got == test_value else "BEDA"))
    print("  restore %d -> %r" % (base, write(h, scmd, base)))
    time.sleep(0.15)
    again = query(h, qcmd)
    print("  verify restore=%r %s" % (again, "OK" if again == base else "GAGAL"))


def main():
    h = k32.CreateFileW("\\\\.\\COM3", GENERIC_READ | GENERIC_WRITE,
                        0, None, OPEN_EXISTING, 0, None)
    if h in (None, INVALID):
        print("Gagal buka COM3, err=%d" % ctypes.get_last_error())
        return 1
    try:
        k32.SetCommState(h, pe.make_dcb())
        k32.SetCommTimeouts(h, ctypes.byref(pe.CommTimeouts(30, 0, 900, 0, 900)))
        print("TERBUKA COM3")

        print("\n=== QUERY KONFLIK (tanpa menulis) ===")
        for name, cmd in [
            ("Firmware", 0x0309), ("Codec", 0x032F), ("Mode audio", 0x034D),
            ("Auto power-off", 0x0348), ("Find device", 0x0333),
            ("Touch lock", 0x0335), ("Gesture", 0x030B),
            ("Noise master", 0x0315), ("ANC sub", 0x033B),
            ("Ambient sub", 0x033D), ("Game", 0x0313), ("In-ear", 0x034A),
            ("Prompt vol", 0x0339), ("Mic", 0x0331), ("Multipoint", 0x0326),
        ]:
            print("  %-16s cmd %04X -> %r" % (name, cmd, query(h, cmd)))

        frames, err = pe.exchange(h, 0x0E02, b"", 1.0)
        print("  EQ query 0E02 ->", err or [(hex(c), p.hex()) for _, _, c, p in frames])

        if "--write" not in sys.argv:
            print("\nMode baca-saja.")
            return 0

        print("\n=== UJI TULIS + READBACK + RESTORE ===")
        trial(h, "Noise master", 0x0315, 0x0314, 2)
        trial(h, "Game mode", 0x0313, 0x0312, 1)
        trial(h, "In-ear detection", 0x034A, 0x0349, 1)
        trial(h, "Touch lock", 0x0335, 0x0334, 0)
        trial(h, "Mic mode", 0x0331, 0x0330, 1)
        trial(h, "Prompt volume", 0x0339, 0x0338, 2)
        trial(h, "ANC sub-mode", 0x033B, 0x033A, 2)
        trial(h, "Ambient sub-mode", 0x033D, 0x033C, 1)

        # Pastikan mode noise kembali ke baseline awal (ANC)
        print("\nFinal noise master ->", query(h, 0x0315))
        return 0
    finally:
        k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main())
