#!/usr/bin/env python3
"""Device Monitor tray app — satu proses: bridge + UI server + system tray.

Tanpa dependency pihak ketiga. Dijalankan dengan pythonw.exe (tanpa console).
Klik kiri ikon = buka panel di browser; klik kanan = menu cepat (ANC, gestur, keluar).
"""
import ctypes
import ctypes.wintypes as wt
import json
import os
import sys
import threading
import time
import urllib.request
import webbrowser
from http.server import SimpleHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
if sys.stdout is None:  # pythonw tidak punya console
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")
ROOT = os.path.dirname(HERE)
DIST = os.path.join(ROOT, "app", "dist")
sys.path.insert(0, HERE)

import bridge
from bridge import Handler as BridgeHandler, QuietServer  # noqa: E402

API = "http://127.0.0.1:8765"
PANEL = "http://localhost:4173/"

k32 = ctypes.WinDLL("kernel32.dll", use_last_error=True)
u32 = ctypes.WinDLL("user32.dll", use_last_error=True)
shell32 = ctypes.WinDLL("shell32.dll", use_last_error=True)
gdi = ctypes.WinDLL("gdi32.dll", use_last_error=True)

# ---------- struktur Win32 ----------


class GUID(ctypes.Structure):
    _fields_ = [("Data1", wt.DWORD), ("Data2", wt.WORD),
                ("Data3", wt.WORD), ("Data4", ctypes.c_ubyte * 8)]


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wt.DWORD), ("hWnd", wt.HWND), ("uID", wt.UINT),
        ("uFlags", wt.UINT), ("uCallbackMessage", wt.UINT), ("hIcon", wt.HICON),
        ("szTip", wt.WCHAR * 128), ("dwState", wt.DWORD), ("dwStateMask", wt.DWORD),
        ("szInfo", wt.WCHAR * 256), ("uTimeout", wt.UINT),
        ("szInfoTitle", wt.WCHAR * 64), ("dwInfoFlags", wt.DWORD),
        ("guidItem", GUID), ("hBalloonIcon", wt.HICON),
    ]


class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wt.UINT), ("lpfnWndProc", ctypes.c_void_p),
        ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
        ("hInstance", wt.HINSTANCE), ("hIcon", wt.HICON),
        ("hCursor", wt.HANDLE), ("hbrBackground", wt.HBRUSH),
        ("lpszMenuName", wt.LPCWSTR), ("lpszClassName", wt.LPCWSTR),
    ]


class POINT(ctypes.Structure):
    _fields_ = [("x", wt.LONG), ("y", wt.LONG)]


class MSG(ctypes.Structure):
    _fields_ = [("hwnd", wt.HWND), ("message", wt.UINT),
                ("wParam", wt.WPARAM), ("lParam", wt.LPARAM),
                ("time", wt.DWORD), ("pt", POINT)]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
        ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
        ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG),
        ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD),
    ]


class ICONINFO(ctypes.Structure):
    _fields_ = [("fIcon", wt.BOOL), ("xHotspot", wt.DWORD), ("yHotspot", wt.DWORD),
                ("hbmMask", wt.HBITMAP), ("hbmColor", wt.HBITMAP)]


WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM)

NIM_ADD, NIM_MODIFY, NIM_DELETE = 0, 1, 2
NIF_MESSAGE, NIF_ICON, NIF_TIP, NIF_STATE, NIF_INFO = 1, 2, 4, 8, 16
WM_APP_TRAY, WM_APP_REFRESH = 0x8001, 0x8002
WM_LBUTTONDOWN, WM_LBUTTONDBLCLK = 0x0201, 0x0203
WM_RBUTTONDOWN, WM_CONTEXTMENU, WM_COMMAND = 0x0204, 0x007B, 0x0111
MF_STRING, MF_SEPARATOR, MF_CHECKED, MF_DISABLED = 0, 0x800, 0x8, 0x2
TPM_RIGHTBUTTON = 0x2
HWND_MESSAGE = ctypes.c_void_p(-3)
DC_BRUSH = 18
TRANSPARENT = 1
FW_BOLD = 700

u32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
u32.CreateWindowExW.restype = wt.HWND
u32.CreateWindowExW.argtypes = [wt.DWORD, wt.LPCWSTR, wt.LPCWSTR, wt.DWORD,
                                wt.INT, wt.INT, wt.INT, wt.INT, wt.HWND,
                                wt.HMENU, wt.HINSTANCE, ctypes.c_void_p]
u32.GetMessageW.argtypes = [ctypes.POINTER(MSG), wt.HWND, wt.UINT, wt.UINT]
u32.TrackPopupMenu.argtypes = [wt.HMENU, wt.UINT, ctypes.c_int, ctypes.c_int,
                               wt.INT, wt.HWND, ctypes.c_void_p]
u32.CreatePopupMenu.restype = wt.HMENU
u32.AppendMenuW.argtypes = [wt.HMENU, wt.UINT, ctypes.c_void_p, wt.LPCWSTR]
u32.SendMessageW.restype = ctypes.c_ssize_t
gdi.CreateDIBSection.argtypes = [wt.HDC, ctypes.POINTER(BITMAPINFOHEADER),
                                 wt.UINT, ctypes.POINTER(ctypes.c_void_p),
                                 wt.HANDLE, wt.DWORD]
gdi.CreateDIBSection.restype = wt.HBITMAP
for _fn, _restype in (
    (gdi.GetStockObject, ctypes.c_void_p),
    (gdi.CreateCompatibleDC, ctypes.c_void_p),
    (gdi.CreateBitmap, wt.HBITMAP),
    (gdi.CreateFontW, ctypes.c_void_p),
    (u32.CreateIconIndirect, wt.HICON),
    (u32.DefWindowProcW, ctypes.c_ssize_t),
):
    _fn.restype = _restype

gdi.SelectObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
gdi.SelectObject.restype = ctypes.c_void_p
gdi.SetDCBrushColor.argtypes = [ctypes.c_void_p, wt.DWORD]
gdi.Rectangle.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
                          ctypes.c_int, ctypes.c_int]
gdi.SetBkMode.argtypes = [ctypes.c_void_p, ctypes.c_int]
gdi.SetTextColor.argtypes = [ctypes.c_void_p, wt.DWORD]
gdi.GetTextExtentPoint32W.argtypes = [ctypes.c_void_p, wt.LPCWSTR, ctypes.c_int,
                                      ctypes.POINTER(wt.SIZE)]
gdi.TextOutW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
                         wt.LPCWSTR, ctypes.c_int]
gdi.DeleteDC.argtypes = [ctypes.c_void_p]
gdi.DeleteObject.argtypes = [ctypes.c_void_p]
u32.CreateIconIndirect.argtypes = [ctypes.POINTER(ICONINFO)]
u32.DestroyIcon.argtypes = [ctypes.c_void_p]
u32.DefWindowProcW.argtypes = [ctypes.c_void_p, wt.UINT, wt.WPARAM, wt.LPARAM]
u32.PostMessageW.argtypes = [ctypes.c_void_p, wt.UINT, wt.WPARAM, wt.LPARAM]
u32.SetForegroundWindow.argtypes = [ctypes.c_void_p]
shell32.Shell_NotifyIconW.argtypes = [wt.UINT, ctypes.POINTER(NOTIFYICONDATAW)]

STATUS = {"mouse": {}, "tws": {}, "errors": {}}
STOP = threading.Event()
HWND = None
NID = None
CURRENT_ICON = None
LOW_NOTIFIED = False


# ---------- ikon ----------


def make_icon(text, color):
    hdc = gdi.CreateCompatibleDC(None)
    bmi = BITMAPINFOHEADER()
    bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth, bmi.biHeight = 32, 32
    bmi.biPlanes, bmi.biBitCount = 1, 32
    bits = ctypes.c_void_p()
    hbmp = gdi.CreateDIBSection(hdc, ctypes.byref(bmi), 0,
                                ctypes.byref(bits), None, 0)
    old = gdi.SelectObject(hdc, hbmp)
    gdi.SetDCBrushColor(hdc, color)
    gdi.SelectObject(hdc, ctypes.c_void_p(gdi.GetStockObject(DC_BRUSH)))
    gdi.Rectangle(hdc, 0, 0, 32, 32)

    hfont = gdi.CreateFontW(14 if len(text) > 2 else 17, 0, 0, 0, FW_BOLD,
                            0, 0, 0, 0, 0, 0, 0, 0, "Segoe UI")
    oldfont = gdi.SelectObject(hdc, hfont)
    gdi.SetBkMode(hdc, TRANSPARENT)
    gdi.SetTextColor(hdc, 0xFFFFFF)
    size = wt.SIZE()
    gdi.GetTextExtentPoint32W(hdc, text, len(text), ctypes.byref(size))
    gdi.TextOutW(hdc, (32 - size.cx) // 2, (32 - size.cy) // 2, text, len(text))
    gdi.SelectObject(hdc, oldfont)
    gdi.DeleteObject(hfont)

    if bits.value:
        buf = ctypes.cast(bits, ctypes.POINTER(ctypes.c_ubyte))
        for i in range(3, 32 * 32 * 4, 4):
            buf[i] = 255
    gdi.SelectObject(hdc, old)
    gdi.DeleteDC(hdc)

    mask = gdi.CreateBitmap(32, 32, 1, 1, None)
    info = ICONINFO(True, 0, 0, mask, hbmp)
    hicon = u32.CreateIconIndirect(ctypes.byref(info))
    gdi.DeleteObject(mask)
    gdi.DeleteObject(hbmp)
    return hicon


def icon_for(pct):
    if pct is None:
        return make_icon("?", 0x5A5958)
    if pct >= 50:
        return make_icon(str(pct), 0x36D399)
    if pct >= 20:
        return make_icon(str(pct), 0x24BFFB)
    return make_icon(str(pct), 0x71F8F8)


def refresh_icon():
    global CURRENT_ICON
    pct = STATUS.get("mouse", {}).get("battery")
    h = icon_for(pct)
    NID.hIcon = h
    NID.uFlags = NIF_ICON | NIF_TIP
    tip = "Device Monitor | Mouse %s%% | TWS %s/%s%%" % (
        pct if pct is not None else "?",
        STATUS.get("tws", {}).get("left", "?"),
        STATUS.get("tws", {}).get("right", "?"),
    )
    NID.szTip = tip[:127]
    shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(NID))
    if CURRENT_ICON:
        u32.DestroyIcon(CURRENT_ICON)
    CURRENT_ICON = h


def balloon(title, text):
    NID.uFlags = NIF_INFO
    NID.szInfoTitle = title[:63]
    NID.szInfo = text[:255]
    NID.dwInfoFlags = 2
    shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(NID))


# ---------- aksi ----------


def api_post(device, key, value):
    data = json.dumps({"key": key, "value": value}).encode()
    req = urllib.request.Request(API + "/api/" + device, data=data,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=4) as res:
        return res.read().decode()


def set_noise(mode):
    try:
        api_post("tws", "noiseMode", mode)
        refresh_icon()
    except Exception:
        balloon("Device Monitor", "Gagal mengubah mode noise")


def toggle_gesture():
    cur = STATUS.get("tws", {}).get("gestureLock", True)
    try:
        api_post("tws", "gestureLock", not cur)
        balloon("Device Monitor", "Gestur " + ("dimatikan" if not cur else "dinyalakan"))
    except Exception:
        balloon("Device Monitor", "Gagal mengubah gestur")


def show_menu(hwnd):
    hmenu = u32.CreatePopupMenu()
    u32.AppendMenuW(hmenu, MF_STRING, 1, "Buka Panel")
    u32.AppendMenuW(hmenu, MF_SEPARATOR, 0, None)
    noise = STATUS.get("tws", {}).get("noiseMode", 1)
    u32.AppendMenuW(hmenu, MF_STRING | (MF_CHECKED if noise == 1 else 0), 10, "ANC")
    u32.AppendMenuW(hmenu, MF_STRING | (MF_CHECKED if noise == 2 else 0), 11, "Ambient")
    u32.AppendMenuW(hmenu, MF_STRING | (MF_CHECKED if noise == 0 else 0), 12, "Normal")
    u32.AppendMenuW(hmenu, MF_SEPARATOR, 0, None)
    lock = STATUS.get("tws", {}).get("gestureLock", True)
    u32.AppendMenuW(hmenu, MF_STRING, 20,
                    "Nyalakan gestur" if lock else "Matikan gestur")
    u32.AppendMenuW(hmenu, MF_SEPARATOR, 0, None)
    u32.AppendMenuW(hmenu, MF_STRING, 99, "Keluar")
    pt = POINT()
    u32.GetCursorPos(ctypes.byref(pt))
    u32.SetForegroundWindow(hwnd)
    u32.TrackPopupMenu(hmenu, TPM_RIGHTBUTTON, pt.x, pt.y, 0, hwnd, None)
    u32.PostMessageW(hwnd, 0, 0, 0)
    u32.DestroyMenu(hmenu)


@WNDPROC
def wndproc(hwnd, msg, wparam, lparam):
    if msg == WM_APP_TRAY:
        # lParam notifikasi ikon ISINYA pesan (WM_LBUTTONDOWN dkk.), bukan koordinat
        event = lparam & 0xFFFF
        if event in (WM_LBUTTONDOWN, WM_LBUTTONDBLCLK):
            print("tray: buka panel", flush=True)
            webbrowser.open(PANEL)
        elif event in (WM_RBUTTONDOWN, WM_CONTEXTMENU):
            print("tray: menu", flush=True)
            show_menu(hwnd)
        return 0
    if msg == WM_APP_REFRESH:
        refresh_icon()
        return 0
    if msg == WM_COMMAND:
        cmd = wparam & 0xFFFF
        if cmd == 1:
            webbrowser.open(PANEL)
        elif cmd == 10:
            set_noise(1)
        elif cmd == 11:
            set_noise(2)
        elif cmd == 12:
            set_noise(0)
        elif cmd == 20:
            toggle_gesture()
        elif cmd == 99:
            STOP.set()
            u32.PostQuitMessage(0)
        return 0
    return u32.DefWindowProcW(hwnd, msg, wparam, lparam)


# ---------- background ----------


def poll_loop():
    global LOW_NOTIFIED
    while not STOP.wait(15):
        try:
            bridge.refresh_if_due("mouse", bridge.mouse_read)
            bridge.refresh_if_due("tws", bridge.tws_read)
            STATUS.clear()
            STATUS.update({"mouse": dict(bridge.CACHE["mouse"]), "tws": dict(bridge.CACHE["tws"])})
            u32.PostMessageW(HWND, WM_APP_REFRESH, 0, 0)
            pct = STATUS.get("mouse", {}).get("battery")
            if isinstance(pct, int) and pct <= 20 and not LOW_NOTIFIED:
                balloon("Baterai mouse rendah", f"Mouse tersisa {pct}%")
                LOW_NOTIFIED = True
            elif isinstance(pct, int) and pct > 30:
                LOW_NOTIFIED = False
        except Exception:
            pass


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST, **kwargs)

    def log_message(self, fmt, *args):
        pass


def main():
    global HWND, NID, CURRENT_ICON
    if not os.path.isdir(DIST):
        raise SystemExit("app/dist tidak ada — jalankan npm run build dulu")

    bridge = QuietServer(("127.0.0.1", 8765), BridgeHandler)
    ui = QuietServer(("127.0.0.1", 4173), QuietHandler)
    threading.Thread(target=bridge.serve_forever, daemon=True).start()
    threading.Thread(target=ui.serve_forever, daemon=True).start()

    wc = WNDCLASSW()
    wc.lpfnWndProc = ctypes.cast(wndproc, ctypes.c_void_p)
    wc.hInstance = k32.GetModuleHandleW(None)
    wc.lpszClassName = "DeviceMonitorTray"
    if not u32.RegisterClassW(ctypes.byref(wc)):
        if ctypes.get_last_error() != 1410:  # ERROR_CLASS_ALREADY_EXISTS
            raise SystemExit("RegisterClass gagal")

    HWND = u32.CreateWindowExW(0, "DeviceMonitorTray", "Device Monitor", 0,
                               0, 0, 0, 0, HWND_MESSAGE, None, wc.hInstance, None)

    NID = NOTIFYICONDATAW()
    NID.cbSize = ctypes.sizeof(NID)
    NID.hWnd = HWND
    NID.uID = 1
    NID.uCallbackMessage = WM_APP_TRAY
    CURRENT_ICON = icon_for(None)
    NID.hIcon = CURRENT_ICON
    NID.szTip = "Device Monitor"
    NID.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
    if not shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(NID)):
        raise SystemExit("Shell_NotifyIcon gagal")

    threading.Thread(target=poll_loop, daemon=True).start()
    print("Device Monitor tray aktif", flush=True)
    try:
        msg = MSG()
        while u32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            u32.TranslateMessage(ctypes.byref(msg))
            u32.DispatchMessageW(ctypes.byref(msg))
    finally:
        shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(NID))
        bridge.shutdown()
        ui.shutdown()
        if CURRENT_ICON:
            u32.DestroyIcon(CURRENT_ICON)


if __name__ == "__main__":
    main()
