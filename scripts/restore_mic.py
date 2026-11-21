#!/usr/bin/env python3
import ctypes
import time
import probe_earbud as pe

k = pe.k32
INVALID = ctypes.c_void_p(-1).value
for attempt in range(8):
    h = k.CreateFileW("\\\\.\\COM3", 0x80000000 | 0x40000000, 0, None, 3, 0, None)
    if h not in (None, INVALID):
        k.SetCommState(h, pe.make_dcb())
        k.SetCommTimeouts(h, ctypes.byref(pe.CommTimeouts(30, 0, 900, 0, 900)))
        print("buka COM3 berhasil, attempt", attempt)
        print("mic write 0 ->", pe.exchange(h, 0x0330, bytes([0]), 1.0))
        k.CloseHandle(h)
        break
    print("COM3 belum tersedia, attempt", attempt)
    time.sleep(2)
else:
    raise SystemExit("COM3 tidak kembali")

time.sleep(3)
for attempt in range(6):
    h = k.CreateFileW("\\\\.\\COM3", 0x80000000 | 0x40000000, 0, None, 3, 0, None)
    if h not in (None, INVALID):
        k.SetCommState(h, pe.make_dcb())
        k.SetCommTimeouts(h, ctypes.byref(pe.CommTimeouts(30, 0, 900, 0, 900)))
        frames, err = pe.exchange(h, 0x0331, b"", 1.0)
        print("mic final:", frames[0][3].hex() if frames else "N/A", err or "")
        k.CloseHandle(h)
        if frames:
            break
    time.sleep(1)
