#!/usr/bin/env python3
"""Uji langsung perintah codec 0x032E + reboot 0x0308 di perangkat nyata.

Bukan lewat bridge — dipakai untuk memvalidasi hipotesis sebelum
mengubah bridge/UI. Mencatat readback sebelum, sesudah tulis, dan
sesudah reboot. Otomatis mengembalikan ke nilai semula kalau gagal.
"""
import sys
import time

import probe_earbud as pe

TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 8
ORIGINAL = None


def open_port(tries=12):
    for i in range(tries):
        try:
            return pe.k32.CreateFileW("\\\\.\\COM3",
                                      0x80000000 | 0x40000000, 0, None, 3, 0, None)
        except Exception:
            time.sleep(0.5)
    raise SystemExit("COM3 tidak bisa dibuka")


def query(h, cmd):
    frames, err = pe.exchange(h, cmd, b"", 1.5)
    if err:
        raise RuntimeError(err)
    if not frames or len(frames[0][3]) < 2:
        raise RuntimeError("tak ada jawaban untuk 0x%04X" % cmd)
    return frames[0][3][1]


def write(h, cmd, payload, wait=1.5):
    frames, err = pe.exchange(h, cmd, bytes([payload]), wait)
    if err:
        raise RuntimeError(err)
    return len(frames)


def reboot(h):
    try:
        pe.exchange(h, 0x0308, b"", 0.8)
    except Exception as exc:
        print("  reboot exchange:", exc, flush=True)
    pe.k32.CloseHandle(h)
    h = None
    for i in range(90):
        time.sleep(1)
        try:
            h = open_port(tries=1)
            pe.k32.SetCommState(h, pe.make_dcb())
            pe.k32.SetCommTimeouts(h, pe.ctypes.byref(pe.CommTimeouts(30, 0, 900, 0, 900)))
            return h, i + 1
        except Exception:
            h = None
    return None, 90


def main():
    global ORIGINAL
    h = open_port()
    ORIGINAL = query(h, 0x032F)
    print("codec awal:", ORIGINAL, flush=True)
    n = write(h, 0x032E, TARGET)
    print("ACK set 0x032E [%d]: %d frame" % (TARGET, n), flush=True)
    time.sleep(0.6)
    rb = query(h, 0x032F)
    print("readback sebelum reboot:", rb, flush=True)
    h, waited = reboot(h)
    if h is None:
        print("GAGAL: COM3 tidak kembali setelah %d detik" % waited, flush=True)
        return 2
    print("COM3 kembali setelah %d detik" % waited, flush=True)
    final = query(h, 0x032F)
    print("codec setelah reboot:", final, flush=True)
    if final != TARGET:
        print("HIPOTESIS GAGAL — mengembalikan ke", ORIGINAL, flush=True)
        write(h, 0x032E, ORIGINAL)
        time.sleep(0.6)
        h, _ = reboot(h)
        if h:
            print("codec setelah restore:", query(h, 0x032F), flush=True)
            pe.k32.CloseHandle(h)
        return 1
    print("HIPOTESIS BENAR: codec =", final, flush=True)
    pe.k32.CloseHandle(h)
    return 0


if __name__ == "__main__":
    sys.exit(main())
