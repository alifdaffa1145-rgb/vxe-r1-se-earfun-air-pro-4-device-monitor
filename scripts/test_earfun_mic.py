#!/usr/bin/env python3
"""Uji encoding mic mode EarFun dengan reconnect setelah SPP putus."""
import ctypes
import time
import probe_earbud as pe

k = pe.k32
INVALID = ctypes.c_void_p(-1).value


def open_port(tries=10):
    for i in range(tries):
        h = k.CreateFileW("\\\\.\\COM3", 0x80000000 | 0x40000000,
                          0, None, 3, 0, None)
        if h not in (None, INVALID):
            k.SetCommState(h, pe.make_dcb())
            k.SetCommTimeouts(h, ctypes.byref(pe.CommTimeouts(30, 0, 900, 0, 900)))
            return h
        time.sleep(1.5)
    return None


def query(h, cmd, tries=6):
    for _ in range(tries):
        frames, err = pe.exchange(h, cmd, b"", 1.2)
        if frames and frames[0][2] == (cmd | 0x8000) and len(frames[0][3]) >= 2:
            return frames[0][3][1]
        time.sleep(0.5)
    return None


def send_set(value):
    h = open_port()
    if not h:
        print("  COM3 tidak kembali")
        return
    frames, err = pe.exchange(h, 0x0330, bytes([value]), 1.2)
    print("  set %d -> %s %s" % (value, [(hex(c), p.hex()) for _, _, c, p in frames], err or ""))
    k.CloseHandle(h)


h = open_port()
if not h:
    raise SystemExit("COM3 tidak tersedia")
base = query(h, 0x0331)
print("Baseline mic:", base)
k.CloseHandle(h)
if base is None:
    raise SystemExit("Baseline tidak terbaca")

for test in (1, 2):
    print("\nUJI nilai", test)
    send_set(test)
    time.sleep(3)
    h = open_port()
    if not h:
        print("  gagal reconnect, lanjut")
        continue
    got = query(h, 0x0331)
    print("  readback:", got, "COCOK" if got == test else "BEDA")
    k.CloseHandle(h)

print("\nRESTORE ke", base)
send_set(base)
time.sleep(3)
h = open_port()
if h:
    print("Final mic:", query(h, 0x0331))
    k.CloseHandle(h)
