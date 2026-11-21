#!/usr/bin/env python3
"""Baca peta gestur EarFun (0x030B) dan uji tulis satu gestur + restore."""
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

    frames, err = pe.exchange(h, 0x030B, b"", 1.5)
    print("RAW:", [(hex(c), p.hex()) for _, _, c, p in frames], err or "")
    if not frames or frames[0][2] != 0x830B:
        raise SystemExit("Gestur tidak merespons")
    p = frames[0][3]
    print("PANJANG:", len(p))
    if len(p) < 17:
        raise SystemExit("Payload pendek")
    names = ["single L", "single R", "double L", "double R",
             "triple L", "triple R", "long L", "long R"]
    vals = [p[1 + 2 * i] for i in range(8)]
    for name, v in zip(names, vals):
        print("  %-10s = %d (0x%02X)" % (name, v, v))

    # Uji: right single (indeks 1) -> aksi 16 (none), lalu restore
    original = vals[1]
    print("\nUJI tulis right single -> 16")
    payload = bytes([0x00, 0x00, 0x01, 16])
    frames, err = pe.exchange(h, 0x030A, payload, 1.2)
    print("  set:", [(hex(c), q.hex()) for _, _, c, q in frames], err or "")
    time.sleep(0.6)
    frames, err = pe.exchange(h, 0x030B, b"", 1.5)
    if frames and frames[0][2] == 0x830B and len(frames[0][3]) >= 17:
        got = frames[0][3][3]
        print("  readback right single =", got, "COCOK" if got == 16 else "BEDA")
    else:
        print("  readback gagal")
    print("RESTORE ->", original)
    payload = bytes([0x00, 0x00, 0x01, original])
    pe.exchange(h, 0x030A, payload, 1.2)
    time.sleep(0.6)
    frames, err = pe.exchange(h, 0x030B, b"", 1.5)
    if frames and frames[0][2] == 0x830B and len(frames[0][3]) >= 17:
        print("  final right single =", frames[0][3][3])
finally:
    k.CloseHandle(h)
