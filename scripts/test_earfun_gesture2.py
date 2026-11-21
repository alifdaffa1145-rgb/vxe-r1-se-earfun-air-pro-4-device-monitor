#!/usr/bin/env python3
"""Baca/restore/puji gestur dengan parsing 33-byte yang benar."""
import ctypes
import time
import probe_earbud as pe

k = pe.k32
INVALID = ctypes.c_void_p(-1).value
h = k.CreateFileW("\\\\.\\COM3", 0x80000000 | 0x40000000, 0, None, 3, 0, None)
if h in (None, INVALID):
    raise SystemExit("COM3 tidak tersedia")
try:
    k.SetCommState(h, pe.make_dcb())
    k.SetCommTimeouts(h, ctypes.byref(pe.CommTimeouts(30, 0, 900, 0, 900)))

    def read():
        for _ in range(4):
            f, e = pe.exchange(h, 0x030B, b"", 1.5)
            if f and f[0][2] == 0x830B and len(f[0][3]) >= 33:
                return f[0][3]
            time.sleep(0.4)
        return None

    def pairs(p):
        return [(p[i], p[i + 1]) for i in range(1, 33, 2)]

    def set_right_single(action):
        payload = bytes([0x00, 0x00, 0x01, action])
        f, e = pe.exchange(h, 0x030A, payload, 1.2)
        time.sleep(0.7)
        return e

    p = read()
    print("SEKARANG:", pairs(p) if p else "GAGAL")
    if not p:
        raise SystemExit("tidak bisa baca")

    # Nilai asli dari sebelum uji sebelumnya: pasangan ke-2 (right single) = (01, 02)
    original = 2
    current = pairs(p)[1][1]
    if current != original:
        print("Restore right single", current, "->", original)
        print("  ", set_right_single(original))
        p = read()
        print("SESUDAH RESTORE:", pairs(p) if p else "GAGAL")

    print("\nUJI tulis right single -> 16")
    set_right_single(16)
    p = read()
    got = pairs(p)[1][1] if p else None
    print("  readback =", got, "COCOK" if got == 16 else "BEDA")

    print("\nRESTORE ->", original)
    set_right_single(original)
    p = read()
    print("  final =", pairs(p)[1][1] if p else "GAGAL")
    print("PAYLOAD AKHIR:", p.hex() if p else "")
finally:
    k.CloseHandle(h)
