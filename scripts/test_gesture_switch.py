#!/usr/bin/env python3
"""Verifikasi nyala/mati gestur EarFun (touch lock 0 = aktif, 1 = mati)."""
import ctypes
import time
import probe_earbud as pe

k = pe.k32
INVALID = ctypes.c_void_p(-1).value
h = None
for _ in range(10):
    h = k.CreateFileW("\\\\.\\COM3", 0x80000000 | 0x40000000, 0, None, 3, 0, None)
    if h not in (None, INVALID):
        break
    time.sleep(2)
if h in (None, INVALID):
    raise SystemExit("COM3 tidak ada")
try:
    k.SetCommState(h, pe.make_dcb())
    k.SetCommTimeouts(h, ctypes.byref(pe.CommTimeouts(30, 0, 900, 0, 900)))

    def q():
        f, e = pe.exchange(h, 0x0335, b"", 1.2)
        return f[0][3][1] if f and len(f[0][3]) >= 2 else None

    base = q()
    print("Baseline touch lock:", base, "(0=gestur aktif, 1=gestur mati)")
    for value, label in [(0, "NYALAKAN gestur"), (1, "MATIKAN gestur"), (base, "restore")]:
        f, e = pe.exchange(h, 0x0334, bytes([value]), 1.2)
        time.sleep(0.8)
        got = q()
        print("  %-16s write %d -> read %s %s" % (
            label, value, got, "OK" if got == value else "GAGAL"))
finally:
    k.CloseHandle(h)
