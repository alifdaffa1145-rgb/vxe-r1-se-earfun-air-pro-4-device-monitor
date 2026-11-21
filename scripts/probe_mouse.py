#!/usr/bin/env python3
"""Spike read-only: baca baterai VXE R1 SE+ lewat HID vendor collection.

Tidak mengubah setting mouse. Hanya mengirim output report 0x08/0x04
dan membaca input report 17 byte.
"""
import ctypes
import ctypes.wintypes as wt
import sys
import time

hid = ctypes.WinDLL("hid.dll")
setup = ctypes.WinDLL("setupapi.dll")
k32 = ctypes.WinDLL("kernel32.dll", use_last_error=True)


class GUID(ctypes.Structure):
    _fields_ = [("Data1", wt.DWORD), ("Data2", wt.WORD),
                ("Data3", wt.WORD), ("Data4", ctypes.c_ubyte * 8)]


class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("InterfaceClassGuid", GUID),
                ("Flags", wt.DWORD), ("Reserved", ctypes.POINTER(wt.ULONG))]


class SP_DEVICE_INTERFACE_DETAIL_DATA_W(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("DevicePath", wt.WCHAR * 1)]


class HIDP_CAPS(ctypes.Structure):
    _fields_ = [
        ("Usage", wt.USHORT), ("UsagePage", wt.USHORT),
        ("InputReportByteLength", wt.USHORT),
        ("OutputReportByteLength", wt.USHORT),
        ("FeatureReportByteLength", wt.USHORT),
        ("Reserved", wt.USHORT * 17),
        ("NumberLinkCollectionNodes", wt.USHORT),
        ("NumberInputButtonCaps", wt.USHORT),
        ("NumberInputValueCaps", wt.USHORT),
        ("NumberInputDataIndices", wt.USHORT),
        ("NumberOutputButtonCaps", wt.USHORT),
        ("NumberOutputValueCaps", wt.USHORT),
        ("NumberOutputDataIndices", wt.USHORT),
        ("NumberFeatureButtonCaps", wt.USHORT),
        ("NumberFeatureValueCaps", wt.USHORT),
        ("NumberFeatureDataIndices", wt.USHORT),
    ]


class OVERLAPPED(ctypes.Structure):
    _fields_ = [("Internal", ctypes.c_void_p), ("InternalHigh", ctypes.c_void_p),
                ("Offset", wt.DWORD), ("OffsetHigh", wt.DWORD),
                ("hEvent", wt.HANDLE)]


GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x1
FILE_SHARE_WRITE = 0x2
OPEN_EXISTING = 3
FILE_FLAG_OVERLAPPED = 0x40000000
ERROR_IO_PENDING = 997
WAIT_TIMEOUT = 258
DIGCF_PRESENT = 0x2
DIGCF_DEVICEINTERFACE = 0x10
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

hid.HidD_GetHidGuid.argtypes = [ctypes.POINTER(GUID)]
setup.SetupDiGetClassDevsW.argtypes = [ctypes.POINTER(GUID), wt.LPCWSTR,
                                       wt.HANDLE, wt.DWORD]
setup.SetupDiGetClassDevsW.restype = wt.HANDLE
setup.SetupDiEnumDeviceInterfaces.argtypes = [wt.HANDLE, ctypes.c_void_p,
                                               ctypes.POINTER(GUID), wt.DWORD,
                                               ctypes.POINTER(SP_DEVICE_INTERFACE_DATA)]
setup.SetupDiGetDeviceInterfaceDetailW.argtypes = [
    wt.HANDLE, ctypes.POINTER(SP_DEVICE_INTERFACE_DATA), ctypes.c_void_p,
    wt.DWORD, ctypes.POINTER(wt.DWORD), ctypes.c_void_p]
setup.SetupDiDestroyDeviceInfoList.argtypes = [wt.HANDLE]
hid.HidD_GetPreparsedData.argtypes = [wt.HANDLE, ctypes.POINTER(ctypes.c_void_p)]
hid.HidP_GetCaps.argtypes = [ctypes.c_void_p, ctypes.POINTER(HIDP_CAPS)]
hid.HidD_FreePreparsedData.argtypes = [ctypes.c_void_p]
k32.CreateFileW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, ctypes.c_void_p,
                            wt.DWORD, wt.DWORD, wt.HANDLE]
k32.CreateFileW.restype = wt.HANDLE
k32.ReadFile.argtypes = [wt.HANDLE, ctypes.c_void_p, wt.DWORD,
                         ctypes.POINTER(wt.DWORD), ctypes.POINTER(OVERLAPPED)]
k32.WriteFile.argtypes = [wt.HANDLE, ctypes.c_void_p, wt.DWORD,
                          ctypes.POINTER(wt.DWORD), ctypes.POINTER(OVERLAPPED)]
k32.GetOverlappedResult.argtypes = [wt.HANDLE, ctypes.POINTER(OVERLAPPED),
                                    ctypes.POINTER(wt.DWORD), wt.BOOL]
k32.CancelIo.argtypes = [wt.HANDLE]


def interfaces():
    guid = GUID()
    hid.HidD_GetHidGuid(ctypes.byref(guid))
    hdev = setup.SetupDiGetClassDevsW(ctypes.byref(guid), None, None,
                                      DIGCF_PRESENT | DIGCF_DEVICEINTERFACE)
    if hdev in (None, INVALID_HANDLE_VALUE):
        return
    try:
        i = 0
        while True:
            iface = SP_DEVICE_INTERFACE_DATA()
            iface.cbSize = ctypes.sizeof(SP_DEVICE_INTERFACE_DATA)
            if not setup.SetupDiEnumDeviceInterfaces(hdev, None, ctypes.byref(guid),
                                                     i, ctypes.byref(iface)):
                break
            i += 1
            need = wt.DWORD()
            setup.SetupDiGetDeviceInterfaceDetailW(hdev, ctypes.byref(iface),
                                                   None, 0, ctypes.byref(need), None)
            if need.value == 0:
                continue
            buf = ctypes.create_string_buffer(need.value)
            detail = ctypes.cast(buf, ctypes.POINTER(SP_DEVICE_INTERFACE_DETAIL_DATA_W))
            detail.contents.cbSize = ctypes.sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA_W)
            ok = setup.SetupDiGetDeviceInterfaceDetailW(
                hdev, ctypes.byref(iface), buf, need.value,
                ctypes.byref(need), None)
            if ok:
                path = ctypes.wstring_at(ctypes.addressof(detail.contents) +
                                         ctypes.sizeof(wt.DWORD))
                yield path
    finally:
        setup.SetupDiDestroyDeviceInfoList(hdev)


def caps_for(path):
    h = k32.CreateFileW(path, GENERIC_READ | GENERIC_WRITE,
                        FILE_SHARE_READ | FILE_SHARE_WRITE, None,
                        OPEN_EXISTING, FILE_FLAG_OVERLAPPED, None)
    if h in (None, INVALID_HANDLE_VALUE):
        print("  DEBUG CreateFile gagal, err=", ctypes.get_last_error())
        return None, None
    try:
        prep = ctypes.c_void_p()
        if not hid.HidD_GetPreparsedData(h, ctypes.byref(prep)):
            print("  DEBUG GetPreparsedData gagal, err=", ctypes.get_last_error())
            return None, None
        try:
            caps = HIDP_CAPS()
            status = hid.HidP_GetCaps(prep, ctypes.byref(caps))
            print("  DEBUG HidP_GetCaps status=", status, " capsSize=", ctypes.sizeof(caps))
            # HIDP_STATUS_SUCCESS = 0x00110000, bukan 0
            if status & 0x80000000:
                return None, None
            return h, caps
        finally:
            hid.HidD_FreePreparsedData(prep)
    except Exception:
        k32.CloseHandle(h)
        raise


def do_io(h, payload, write, timeout_ms=1000):
    ev = k32.CreateEventW(None, True, False, None)
    ov = OVERLAPPED()
    ov.hEvent = ev
    buf = (ctypes.c_ubyte * len(payload)).from_buffer_copy(payload)
    n = wt.DWORD()
    fn = k32.WriteFile if write else k32.ReadFile
    ok = fn(h, buf, len(payload), ctypes.byref(n), ctypes.byref(ov))
    err = ctypes.get_last_error()
    if not ok and err != ERROR_IO_PENDING:
        k32.CloseHandle(ev)
        return None, "io-start error %d" % err
    r = k32.WaitForSingleObject(ev, timeout_ms)
    if r == WAIT_TIMEOUT:
        k32.CancelIo(h)
        k32.CloseHandle(ev)
        return None, "timeout (mouse possibly asleep)"
    got = wt.DWORD()
    ok = k32.GetOverlappedResult(h, ctypes.byref(ov), ctypes.byref(got), False)
    data = bytes(buf[:got.value]) if ok else None
    k32.CloseHandle(ev)
    return data, None if ok else "GetOverlappedResult failed"


def main():
    targets = []
    for path in interfaces():
        low = path.lower()
        if "vid_3554&pid_f58e" not in low:
            continue
        h, caps = caps_for(path)
        if caps is None:
            print("SKIP  (no caps):", path[:110])
            continue
        print("COL   page=0x%04X usage=0x%04X in=%d out=%d feat=%d  %s" % (
            caps.UsagePage, caps.Usage, caps.InputReportByteLength,
            caps.OutputReportByteLength, caps.FeatureReportByteLength,
            path[:110]))
        if caps.UsagePage == 0xFF02 and caps.InputReportByteLength == 17 \
                and caps.OutputReportByteLength == 17:
            targets.append((path, h))

    if not targets:
        print("RESULT: tidak ada koleksi vendor 0xFF02 17/17 yang cocok")
        return 1

    # Report: 08 04 00...  checksum = 0x4D - cmd
    req = bytes([0x08, 0x04] + [0x00] * 14 + [0x49])
    print("SEND ", req.hex(" "))

    for attempt in range(1, 4):
        for path, h in targets:
            data, err = do_io(h, req, True)
            if err:
                print("WRITE ERROR:", err)
                continue
            data, err = do_io(h, bytes(17), False, 1200)
            if err:
                print("READ  ERROR:", err)
                continue
            print("RECV ", data.hex(" "))
            if len(data) >= 10 and data[0] == 0x08 and data[1] == 0x04:
                pct, charging = data[6], data[7]
                mv = (data[8] << 8) | data[9]
                print("RESULT: battery=%d%% charging=%s voltage=%dmV" % (
                    pct, bool(charging), mv))
                if 0 <= pct <= 100:
                    return 0
                print("RESULT: persentase di luar rentang — framing salah")
        time.sleep(0.4)
    print("RESULT: tidak ada jawaban valid setelah 3 percobaan")
    return 2


if __name__ == "__main__":
    sys.exit(main())
