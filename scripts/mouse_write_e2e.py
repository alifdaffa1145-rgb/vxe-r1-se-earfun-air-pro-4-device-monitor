#!/usr/bin/env python3
"""Uji end-to-end write mouse baru lewat bridge (tulis -> readback -> restore)."""
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
    dpi0 = base["dpiStages"][0]
    tests = [
        ("activeStage", 0, base["activeStage"]),
        ("motionSync", not base["motionSync"], base["motionSync"]),
        ("angleSnap", not base["angleSnap"], base["angleSnap"]),
        ("led", not base["led"], base["led"]),
        ("sleep", 30, base["sleep"]),
        ("dpiStage", [0, dpi0 + 50], [0, dpi0]),
    ]
    out = {"baseline": base, "tests": []}
    for key, val, back in tests:
        try:
            rb = bridge.mouse_write(key, val)
            print("%-12s -> %r readback %r" % (key, val, rb), flush=True)
            rb2 = bridge.mouse_write(key, back)
            print("%-12s <- %r readback %r" % (key, back, rb2), flush=True)
            out["tests"].append({"key": key, "write": val, "readback": rb,
                                 "restore": back, "readback2": rb2})
        except Exception as exc:
            print("%-12s GAGAL %s" % (key, exc), flush=True)
            out["tests"].append({"key": key, "error": str(exc)})
            wait_ready()
    after = wait_ready()
    out["after"] = after
    out["identical"] = after == base
    print("after:", json.dumps(after), flush=True)
    print("IDENTIK BASELINE:", out["identical"], flush=True)
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "mouse_e2e.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
