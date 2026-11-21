#!/usr/bin/env python3
"""Spike helper: decode nama perangkat Bluetooth dari registry + daftar COM."""
import winreg

print("=== Nama perangkat BTHPORT ===")
try:
    k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                       r"SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Devices")
    i = 0
    while True:
        try:
            mac = winreg.EnumKey(k, i)
        except OSError:
            break
        i += 1
        try:
            d = winreg.OpenKey(k, mac)
            raw, _ = winreg.QueryValueEx(d, "Name")
            # Name disimpan sebagai string UTF-8 biasa, bukan UTF-16
            name = raw.decode("utf-8", "replace").rstrip("\x00")
            winreg.CloseKey(d)
        except OSError:
            name = ""
        print("%s  %s" % (mac, name))
    winreg.CloseKey(k)
except OSError as e:
    print("registry error:", e)

print("=== Port COM ===")
try:
    k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
    i = 0
    while True:
        try:
            _, val, _ = winreg.EnumValue(k, i)
        except OSError:
            break
        print(val)
        i += 1
    winreg.CloseKey(k)
except OSError as e:
    print("registry error:", e)
