#!/usr/bin/env python3
"""Uji lanjutan konflik EarFun dengan retry + jeda lebih panjang."""
import ctypes
import ctypes.wintypes as wt
import time
import probe_earbud as pe

k32 = pe.k32
INVALID = ctypes.c_void_p(-1).value


def query(h, cmd, tries=4):
    for i in range(tries):
        frames, err = pe.exchange(h, cmd, b"", 1.0)
        if not err and frames:
            for ver, vendor, c, payload in frames:
                if c == (cmd | 0x8000) and len(payload) >= 2 and payload[0] == 0:
                    return payload[1]
        time.sleep(0.25)
    return None


def write(h, cmd, value):
    frames, err = pe.exchange(h, cmd, bytes([value]), 1.0)
    time.sleep(0.5)
    return err


def trial(h, name, qcmd, scmd, test_value):
    base = query(h, qcmd)
    print("\n%s baseline=%r" % (name, base))
    if not isinstance(base, int):
        print("  SKIP")
        return
    err = write(h, scmd, test_value)
    got = query(h, qcmd)
    print("  write %d (%s) -> readback=%r %s" % (
        test_value, err or "ok", got, "COCOK" if got == test_value else "BEDA"))
    write(h, scmd, base)
    again = query(h, qcmd)
    print("  restore -> %r %s" % (again, "OK" if again == base else "GAGAL"))


def main():
    h = k32.CreateFileW("\\\\.\\COM3", 0x80000000 | 0x40000000,
                        0, None, 3, 0, None)
    if h in (None, INVALID):
        print("Gagal buka COM3")
        return 1
    try:
        k32.SetCommState(h, pe.make_dcb())
        k32.SetCommTimeouts(h, ctypes.byref(pe.CommTimeouts(30, 0, 900, 0, 900)))
        print("TERBUKA COM3")
        trial(h, "Noise master", 0x0315, 0x0314, 2)
        trial(h, "ANC sub-mode", 0x033B, 0x033A, 2)
        trial(h, "Ambient sub-mode", 0x033D, 0x033C, 0)
        trial(h, "Mic mode", 0x0331, 0x0330, 1)
        trial(h, "Prompt volume", 0x0339, 0x0338, 2)
        print("\nSTATE AKHIR:")
        for n, c in [("noise", 0x0315), ("anc", 0x033B), ("amb", 0x033D),
                     ("mic", 0x0331), ("prompt", 0x0339), ("game", 0x0313),
                     ("inear", 0x034A), ("touchlock", 0x0335)]:
            print("  %-10s %r" % (n, query(h, c)))
        return 0
    finally:
        k32.CloseHandle(h)


if __name__ == "__main__":
    main()
