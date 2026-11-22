#!/usr/bin/env python3
"""Menunggu mouse bangun lalu menyimpan baseline register (read-only).

Jalankan di background; gerakkan mouse fisik agar receiver bangun.
Output: <output> berisi hex payload tiap register.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bridge  # noqa: E402

REGS = [0x0000, 0x000A, 0x000C, 0x002C, 0x0040, 0x004C,
        0x0060, 0x0070, 0x00A9, 0x00B5, 0x00BD, 0x00C0]


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "mouse_baseline.json")
    while True:
        h = bridge.mouse_open()
        if not h:
            print("mouse belum bangun...", flush=True)
            time.sleep(1.5)
            continue
        try:
            data = {}
            for addr in REGS:
                r = bridge.mouse_io(h, bridge.mouse_frame(0x08, addr, b"\x00" * 10))
                data["%04X" % addr] = r.hex()
            with open(out_path, "w") as fh:
                json.dump(data, fh, indent=1)
            print("BASELINE TERSIMPAN:", out_path, flush=True)
            for k, v in data.items():
                print(" ", k, v, flush=True)
            return 0
        except Exception as exc:
            print("belum bangun:", exc, flush=True)
            time.sleep(1.5)
        finally:
            try:
                bridge.pm.k32.CloseHandle(h)
            except Exception:
                pass


if __name__ == "__main__":
    sys.exit(main())
