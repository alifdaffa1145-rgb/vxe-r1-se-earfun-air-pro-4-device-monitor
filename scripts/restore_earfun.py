#!/usr/bin/env python3
"""Kembalikan state yang berubah selama uji dan cek akhir."""
import ctypes
import time
import probe_earbud as pe

k32 = pe.k32
h = k32.CreateFileW("\\\\.\\COM3", 0x80000000 | 0x40000000, 0, None, 3, 0, None)
if h == ctypes.c_void_p(-1).value:
    raise SystemExit("Gagal buka COM3")
try:
    k32.SetCommState(h, pe.make_dcb())
    k32.SetCommTimeouts(h, ctypes.byref(pe.CommTimeouts(30, 0, 900, 0, 900)))
    print("RESTORE noise master -> 1")
    pe.exchange(h, 0x0314, bytes([1]), 1.0)
    time.sleep(1.0)
    for i in range(5):
        frames, err = pe.exchange(h, 0x0315, b"", 1.0)
        if frames:
            print("  noise =", frames[0][3].hex())
            break
        time.sleep(0.5)
    print("CEK AKHIR:")
    for name, cmd in [("noise", 0x0315), ("anc", 0x033B), ("amb", 0x033D),
                      ("game", 0x0313), ("inear", 0x034A), ("mic", 0x0331),
                      ("prompt", 0x0339), ("touch", 0x0335), ("codec", 0x032F)]:
        frames, err = pe.exchange(h, cmd, b"", 1.0)
        v = frames[0][3].hex() if frames else "N/A"
        print("  %-7s %s" % (name, v))
        time.sleep(0.2)
finally:
    k32.CloseHandle(h)
