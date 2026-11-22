#!/usr/bin/env python3
"""Uji fitur ganti codec TWS (LDAC) lewat bridge.

Sebelum perbaikan: POST /api/tws codec ditolak (500) -> MERAH.
Sesudah perbaikan: codec tertulis, earbud reboot ~20 dtk,
readback GET /api/status harus 8 (LDAC) -> HIJAU.

Pemakaian:
  python3 tws_codec_probe.py            # uji ke LDAC (8)
  python3 tws_codec_probe.py 19         # kembalikan ke Lossless (19)
"""
import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8765"


def get_status():
    last = None
    for _ in range(5):
        try:
            with urllib.request.urlopen(BASE + "/api/status", timeout=25) as r:
                return json.load(r)
        except Exception as exc:
            last = exc
            time.sleep(1)
    raise last


def post_codec(value):
    data = json.dumps({"key": "codec", "value": value}).encode()
    req = urllib.request.Request(BASE + "/api/tws", data=data,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read() or b"{}")


def main():
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    before = get_status()
    print("SEBELUM: codec=%r connected=%r errors=%r" % (
        before["tws"].get("codec"), before["connected"], before["errors"]), flush=True)
    code, body = post_codec(target)
    print("POST codec=%d -> HTTP %d %s" % (target, code, json.dumps(body)), flush=True)
    if code != 200:
        print("HASIL: MERAH — bridge menolak penulisan codec", flush=True)
        return 1
    deadline = time.monotonic() + 75
    last = None
    while time.monotonic() < deadline:
        time.sleep(2)
        try:
            s = get_status()
            last = s["tws"].get("codec")
            if last == target:
                print("HASIL: HIJAU — codec perangkat = %r setelah reboot" % last, flush=True)
                return 0
        except Exception as exc:
            last = "error: %s" % exc
        print("  menunggu reboot... codec=%r" % last, flush=True)
    print("HASIL: MERAH — timeout, codec akhir = %r (harus %d)" % (last, target), flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
