#!/usr/bin/env python3
"""Spike read-only: baca status EarFun Air Pro 4 lewat GAIA/SPP di COM3.

Perangkat di PC ini: MAC 705A6F6B3AB1, nama Bluetooth diganti '⊙﹏⊙'.
Hanya mengirim perintah query — tidak mengubah pengaturan earbud.
"""
import ctypes
import ctypes.wintypes as wt
import sys
import time

k32 = ctypes.WinDLL("kernel32.dll", use_last_error=True)

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
PURGE_RXCLEAR = 0x0008
PURGE_TXCLEAR = 0x0004
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

k32.CreateFileW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, ctypes.c_void_p,
                            wt.DWORD, wt.DWORD, wt.HANDLE]
k32.CreateFileW.restype = wt.HANDLE
k32.WriteFile.argtypes = [wt.HANDLE, ctypes.c_void_p, wt.DWORD,
                          ctypes.POINTER(wt.DWORD), ctypes.c_void_p]
k32.ReadFile.argtypes = [wt.HANDLE, ctypes.c_void_p, wt.DWORD,
                         ctypes.POINTER(wt.DWORD), ctypes.c_void_p]
k32.GetCommState.argtypes = [wt.HANDLE, ctypes.c_void_p]
k32.SetCommState.argtypes = [wt.HANDLE, ctypes.c_void_p]
k32.SetCommTimeouts.argtypes = [wt.HANDLE, ctypes.c_void_p]
k32.PurgeComm.argtypes = [wt.HANDLE, wt.DWORD]


class CommTimeouts(ctypes.Structure):
    _fields_ = [("ReadIntervalTimeout", wt.DWORD),
                ("ReadTotalTimeoutMultiplier", wt.DWORD),
                ("ReadTotalTimeoutConstant", wt.DWORD),
                ("WriteTotalTimeoutMultiplier", wt.DWORD),
                ("WriteTotalTimeoutConstant", wt.DWORD)]


def make_dcb():
    buf = ctypes.create_string_buffer(28)
    u32 = ctypes.cast(buf, ctypes.POINTER(wt.DWORD))
    u16 = ctypes.cast(buf, ctypes.POINTER(wt.WORD))
    u8 = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))
    u32[0] = 28        # DCBlength
    u32[1] = 9600      # BaudRate
    u32[2] = 0x0001    # fBinary = 1
    u8[18] = 8         # ByteSize
    u8[19] = 0         # Parity = none
    u8[20] = 1         # StopBits = 1
    return buf


def gaia_frame(cmd, payload=b""):
    # SOP, version 0x04, flags 0x00, vendor 0x000A, cmd big-endian
    return bytes([0xFF, 0x04, 0x00, len(payload), 0x00, 0x0A,
                  (cmd >> 8) & 0xFF, cmd & 0xFF]) + payload


def parse_frames(blob):
    out = []
    i = 0
    while i < len(blob) - 8:
        if blob[i] != 0xFF:
            i += 1
            continue
        ver, flags, n = blob[i + 1], blob[i + 2], blob[i + 3]
        if flags != 0 or n > 255 or i + 8 + n > len(blob):
            i += 1
            continue
        vendor = (blob[i + 4] << 8) | blob[i + 5]
        cmd = (blob[i + 6] << 8) | blob[i + 7]
        if ver not in (0x03, 0x04) or vendor not in (0x000A, 0x001D):
            i += 1
            continue
        out.append((ver, vendor, cmd, blob[i + 8:i + 8 + n]))
        i += 8 + n
    return out


def exchange(h, cmd, payload=b"", wait=1.2):
    k32.PurgeComm(h, PURGE_RXCLEAR | PURGE_TXCLEAR)
    frame = gaia_frame(cmd, payload)
    n = wt.DWORD()
    if not k32.WriteFile(h, frame, len(frame), ctypes.byref(n), None):
        return [], "WriteFile error %d" % ctypes.get_last_error()
    chunks = bytearray()
    end = time.monotonic() + wait
    while time.monotonic() < end:
        buf = (ctypes.c_ubyte * 256)()
        got = wt.DWORD()
        ok = k32.ReadFile(h, buf, 256, ctypes.byref(got), None)
        if ok and got.value:
            chunks.extend(buf[:got.value])
            if parse_frames(chunks):
                break
        else:
            time.sleep(0.04)
    return parse_frames(chunks), None


STATUSES = {
    0x0309: "Firmware",
    0x0306: "Baterai KIRI",
    0x0307: "Baterai KANAN",
    0x0317: "Baterai CASE",
    0x0315: "Mode noise-control",
    0x033B: "Sub-mode ANC",
    0x033D: "Sub-mode Transparency",
    0x0313: "Game mode",
    0x034A: "In-ear detection",
    0x0326: "Multipoint",
    0x032F: "Codec",
}


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "COM3"
    h = k32.CreateFileW("\\\\.\\" + port, GENERIC_READ | GENERIC_WRITE,
                        0, None, OPEN_EXISTING, 0, None)
    if h in (None, INVALID_HANDLE_VALUE):
        print("Gagal buka %s, err=%d" % (port, ctypes.get_last_error()))
        return 1
    try:
        k32.SetCommState(h, make_dcb())
        to = CommTimeouts(30, 0, 900, 0, 900)
        k32.SetCommTimeouts(h, ctypes.byref(to))
        print("TERBUKA:", port)

        for cmd in (0x0309, 0x0306, 0x0307, 0x0317, 0x0315,
                    0x033B, 0x033D, 0x0313, 0x034A, 0x0326, 0x032F):
            frames, err = exchange(h, cmd)
            label = STATUSES.get(cmd, hex(cmd))
            if err:
                print("%-24s ERROR %s" % (label, err))
                continue
            if not frames:
                print("%-24s (tidak ada jawaban)" % label)
                continue
            for ver, vendor, rcmd, payload in frames:
                txt = " ".join("%02X" % b for b in payload)
                extra = ""
                if len(payload) >= 2 and (rcmd & 0x7FFF) in (0x0306, 0x0307, 0x0317):
                    lvl = payload[1]
                    extra = "  -> %s" % ("N/A (sentinel 0xFF)" if lvl == 0xFF
                                         else "%d%%" % lvl if lvl <= 100
                                         else "nilai di luar rentang")
                elif rcmd == 0x8309 and len(payload) > 1:
                    extra = "  -> " + payload[1:].decode("ascii", "replace")
                print("%-24s FF %02X 00 %02X %04X %04X %s%s" % (
                    label, ver, len(payload), vendor, rcmd, txt, extra))
        return 0
    finally:
        k32.CloseHandle(h)


if __name__ == "__main__":
    sys.exit(main())
