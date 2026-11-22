#!/usr/bin/env python3
"""Uji lengkap setelah perbaikan sinkronisasi frame.

Menunggu mouse bangun, lalu menulis -> membaca kembali -> memulihkan
activeStage, motionSync, angleSnap, led, sleep, dan DPI stage.
Hasil: scratch/mouse_uji_lengkap.json
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bridge  # noqa: E402


def wait_ready(limit=900):
    t0 = time.monotonic()
    while time.monotonic() - t0 < limit:
        try:
            return bridge.mouse_read()
        except Exception:
            time.sleep(1.5)
    raise SystemExit("mouse tak bangun")


def main():
    base = wait_ready()
    print("baseline:", json.dumps(base), flush=True)
    tests = [
        ("activeStage", 0, base["activeStage"]),
        ("motionSync", not base["motionSync"], base["motionSync"]),
        ("angleSnap", not base["angleSnap"], base["angleSnap"]),
        ("led", not base["led"], base["led"]),
        ("sleep", 30, base["sleep"]),
        ("dpiStage", [0, base["dpiStages"][0] + 50], [0, base["dpiStages"][0]]),
    ]
    out = {"baseline": base, "tests": [], "ok": True}
    for key, val, back in tests:
        try:
            rb = bridge.mouse_write(key, val)
            rb2 = bridge.mouse_write(key, back)
            good = (rb == val) and (rb2 == back)
            if not good:
                out["ok"] = False
            print("%-12s -> %-12r readback %-12r | <- %-12r readback %-12r %s" % (
                key, val, rb, back, rb2, "OK" if good else "BEDA"), flush=True)
            out["tests"].append({"key": key, "write": val, "readback": rb,
                                 "restore": back, "readback2": rb2, "ok": good})
        except Exception as exc:
            out["ok"] = False
            print("%-12s GAGAL %s" % (key, exc), flush=True)
            out["tests"].append({"key": key, "error": str(exc)})
            wait_ready()
    after = wait_ready()
    out["after"] = after
    out["identical"] = after == base
    print("after:", json.dumps(after), flush=True)
    print("SEMUA OK:", out["ok"], "| IDENTIK BASELINE:", out["identical"], flush=True)
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.expanduser("~"), "AppData", "Local", "hermes", "cache", "scratch",
        "mouse_uji_lengkap.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    print("TERSIMPAN:", path, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
