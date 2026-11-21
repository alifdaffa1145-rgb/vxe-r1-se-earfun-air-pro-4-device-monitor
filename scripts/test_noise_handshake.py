#!/usr/bin/env python3
"""Coba handshake firmware dulu sebelum write noise mode."""
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

    fw, e = pe.exchange(h, 0x0309, b"", 1.2)
    print("handshake firmware:", [(hex(c), p[:8].hex()) for _, _, c, p in fw], e or "")
    time.sleep(0.3)
    for v in (1,):
        f, e = pe.exchange(h, 0x0314, bytes([v]), 1.2)
        print("write", v, [(hex(c), p.hex()) for _, _, c, p in f], e or "")
        time.sleep(1.0)
        f, e = pe.exchange(h, 0x0315, b"", 1.2)
        print("noise:", [(hex(c), p.hex()) for _, _, c, p in f], e or "")
finally:
    k.CloseHandle(h)
