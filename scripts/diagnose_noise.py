#!/usr/bin/env python3
"""Diagnosis write noise mode: raw frame vs exchange, cek state lengkap."""
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
    k.SetCommTimeouts(h, ctypes.byref(pe.CommTimeouts(30, 0, 1200, 0, 1200)))

    def q(cmd, label):
        f, e = pe.exchange(h, cmd, b"", 1.5)
        print("  %-14s %s %s" % (label, [(hex(c), p.hex()) for _, _, c, p in f], e or ""))
        return f

    print("STATE SEBELUM:")
    for cmd, label in [(0x0309, "firmware"), (0x0306, "baterai L"),
                       (0x0307, "baterai R"), (0x0317, "case"),
                       (0x0315, "noise"), (0x033B, "anc sub"),
                       (0x033D, "amb sub"), (0x034D, "audio mode"),
                       (0x0335, "touch lock")]:
        q(cmd, label)

    print("\nUJI RAW WRITE (tanpa purge) 0x0314 [1]:")
    frame = pe.gaia_frame(0x0314, bytes([1]))
    print("  frame:", frame.hex(" "))
    n = ctypes.c_ulong()
    ok = k.WriteFile(h, frame, len(frame), ctypes.byref(n), None)
    print("  WriteFile:", bool(ok), "err", ctypes.get_last_error())
    time.sleep(1.0)
    q(0x0315, "noise sesudah")

    print("\nUJI SET SUB dulu 0x033A [3], lalu master 0x0314 [1]:")
    pe.exchange(h, 0x033A, bytes([3]), 1.2)
    time.sleep(0.4)
    pe.exchange(h, 0x0314, bytes([1]), 1.2)
    time.sleep(1.0)
    q(0x0315, "noise sesudah 2")
finally:
    k.CloseHandle(h)
