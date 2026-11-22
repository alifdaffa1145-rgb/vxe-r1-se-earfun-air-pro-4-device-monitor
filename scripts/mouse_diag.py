#!/usr/bin/env python3
"""Diagnosa deteksi mouse: interface ada? handle bisa dibuka? battery terbaca?"""
import ctypes
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bridge  # noqa: E402
import probe_mouse as pm  # noqa: E402


def hexs(b):
    return " ".join("%02x" % x for x in b)


def main():
    print("=== interface mouse vid_3554&pid_f58e ===", flush=True)
    found = False
    for path in pm.interfaces():
        low = path.lower()
        if "vid_3554&pid_f58e" not in low:
            continue
        found = True
        print("PATH", path, flush=True)
        h = None
        try:
            h, caps = pm.caps_for(path)
        except Exception as exc:
            print("  caps_for error:", exc, flush=True)
        if not h:
            print("  HANDLE GAGAL", flush=True)
            continue
        print("  page=0x%04X usage=0x%04X in=%d out=%d feat=%d" % (
            caps.UsagePage, caps.Usage, caps.InputReportByteLength,
            caps.OutputReportByteLength, caps.FeatureReportByteLength), flush=True)
        if caps.UsagePage == 0xFF02 and caps.InputReportByteLength == 17 \
                and caps.OutputReportByteLength == 17:
            req = bytes([0x08, 0x04] + [0x00] * 14 + [0x49])
            for attempt in range(1, 6):
                d, err = pm.do_io(h, req, True, 1000)
                if err:
                    print("  tulis err:", err, flush=True)
                    time.sleep(0.3)
                    continue
                d, err = pm.do_io(h, bytes(17), False, 1200)
                if err:
                    print("  baca err:", err, flush=True)
                    time.sleep(0.3)
                    continue
                print("  RECV", hexs(d), flush=True)
                if d[0] == 0x08 and d[1] == 0x04 and len(d) >= 10:
                    print("  BATTERY=%d%% charging=%s mv=%d" % (
                        d[6], bool(d[7]), (d[8] << 8) | d[9]), flush=True)
                    break
                time.sleep(0.3)
        pm.k32.CloseHandle(h)
    if not found:
        print("TIDAK ADA interface mouse vid_3554&pid_f58e", flush=True)
    print("=== mouse_open bridge ===", flush=True)
    h = bridge.mouse_open()
    print("handle:", h, flush=True)
    if h:
        pm.k32.CloseHandle(h)
    try:
        print("mouse_read:", bridge.mouse_read(), flush=True)
    except Exception as exc:
        print("mouse_read GAGAL:", exc, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
