#!/usr/bin/env python3
"""Uji stabilitas prompt volume EarFun: query berulang + uji tulis restore."""
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

    print("=== QUERY 0339 x6 ===")
    seen = []
    for i in range(6):
        frames, err = pe.exchange(h, 0x0339, b"", 1.2)
        raw = [(hex(c), p.hex()) for _, _, c, p in frames]
        print("  %d: %s %s" % (i + 1, raw, err or ""))
        if frames and frames[0][2] == 0x8339 and len(frames[0][3]) >= 2:
            seen.append(frames[0][3][1])
        time.sleep(0.5)
    print("  nilai:", seen)

    if not seen:
        print("HASIL: prompt volume TIDAK merespons -> dilewati")
    else:
        base = seen[-1]
        print("Baseline:", base)
        pair = bytes([base])
        frames, err = pe.exchange(h, 0x0338, pair, 1.2)
        print("Tulis %d ->" % base, [(hex(c), p.hex()) for _, _, c, p in frames], err or "")
        time.sleep(0.6)
        frames, err = pe.exchange(h, 0x0339, b"", 1.2)
        print("Readback:", [(hex(c), p.hex()) for _, _, c, p in frames], err or "")
finally:
    k.CloseHandle(h)
