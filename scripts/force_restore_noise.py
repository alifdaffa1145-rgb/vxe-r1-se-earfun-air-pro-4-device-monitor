#!/usr/bin/env python3
import ctypes
import time
import probe_earbud as pe

k = pe.k32
INVALID = ctypes.c_void_p(-1).value
h = None
for attempt in range(10):
    h = k.CreateFileW("\\\\.\\COM3", 0x80000000 | 0x40000000, 0, None, 3, 0, None)
    if h not in (None, INVALID):
        break
    time.sleep(2)
if h in (None, INVALID):
    raise SystemExit("COM3 tidak kembali")
try:
    k.SetCommState(h, pe.make_dcb())
    k.SetCommTimeouts(h, ctypes.byref(pe.CommTimeouts(30, 0, 900, 0, 900)))
    for attempt in range(6):
        f, e = pe.exchange(h, 0x0314, bytes([1]), 1.2)
        print("write 1 attempt", attempt, [(hex(c), p.hex()) for _, _, c, p in f], e or "")
        time.sleep(0.8)
        f, e = pe.exchange(h, 0x0315, b"", 1.2)
        v = f[0][3].hex() if f else "N/A"
        print("  noise =", v)
        if f and f[0][3][1] == 1:
            print("BERHASIL")
            break
finally:
    k.CloseHandle(h)
