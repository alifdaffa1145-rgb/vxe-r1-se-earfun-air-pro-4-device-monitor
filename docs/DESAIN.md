# Desain: Tray Monitor Baterai & Mode Perangkat (VXE R1 SE+ + EarFun Air Pro 4)

Tanggal: 2026-11-21
Status: **menunggu persetujuan** (spike selesai, belum ada kode aplikasi final)

## 1. Intent & mengapa

Pengguna tidak bisa melihat persentase baterai mouse gaming 2.4G-nya, tidak bisa melihat baterai kiri/kanan earbudnya, dan harus membuka HP untuk mengubah mode suara. Windows menyembunyikan data ini karena mouse memakai HID vendor-defined dan EarFun tidak punya aplikasi PC. Tujuannya: satu tempat di PC untuk melihat dan mengubah hal-hal yang dipakai sehari-hari, tanpa HP, tanpa software vendor.

## 2. Hasil spike (bukti, bukan asumsi)

| Perangkat | Cara baca | Hasil nyata di PC ini |
|---|---|---|
| VXE R1 SE+ | HID output report `08 04 … 49` pada koleksi `VID_3554&PID_F58E` usage page `0xFF02`, 17/17 byte | `80%`, `4011 mV`, charging = true. Checksum respons `0x3C` valid |
| EarFun Air Pro 4 | GAIA v3 over SPP di `COM3` (MAC `705A6F6B3AB1`, nama Bluetooth sudah diganti `⊙﹏⊙`) | Firmware `TW600-3091_20250919_v0.4.1`; kiri 40%, kanan 50%, case `0xFF` (tidak di case); mode noise 1, ANC sub 3, transparency sub 1, game 0 |

Nama perangkat di Windows tidak bisa dipakai sebagai identitas: sudah diganti pengguna. Identitas harus memakai VID/PID untuk mouse dan MAC + UUID GAIA `eb04`–`eb07` untuk earbud.

## 3. Goals

- Satu ikon system tray yang menampilkan angka baterai mouse; tooltip dan panel berisi semua data.
- Panel terbuka dengan satu klik; berisi baterai mouse (%, mV, charging), baterai L/R/case, dan tombol mode.
- Mode yang tersedia: Normal/ANC/Transparency, sub-mode ANC, sub-mode Transparency, Game mode, In-ear detection, EQ preset 10-band.
- Hotkey global untuk cycle mode dan toggle game mode.
- Auto-start saat login, tidak meminta admin, tidak ada installer.
- Tetap jalan kalau earbud sedang tidak terhubung (tampilkan "N/A", jangan error).

## 4. Non-goals / batas v1

- Tidak mengubah firmware, tidak firmware update.
- Tidak menyimpan preset EQ di earbud (perangkat tidak bisa membaca EQ — write-only). Preset disimpan lokal dan ditulis ulang saat dibuka.
- Tidak mengimplementasikan multipoint / codec / find-device / factory reset di v1. Multipoint butuh reboot earbud dan konflik dengan LDAC — terlalu berisiko untuk dipakai sebagai "akses cepat".
- Tidak menggantikan EarFun Audio app untuk pairing awal.

## 5. Anti-goals (yang bikin gagal)

- Angka baterai yang terlihat meyakinkan tetapi bersumber dari byte yang salah / tanpa validasi checksum.
- Aplikasi yang macet saat mouse tidur atau dongle re-enumerasi setelah sleep.
- Menampilkan `255%` dari sentinel `0xFF` case.
- Mengira mode berhasil berubah hanya karena perintah dikirim; perlu dicek dengan query ulang.

## 6. Constraint

- Python 3.14.5 di PC, **stdlib saja** (`ctypes`, `tkinter`, `winreg`) — tidak ada pip dependency, tidak ada admin, tidak ada driver.
- Windows 11 build 26100.3194.
- Port COM earbud tidak固定: harus di-resolve dari registry `BTHENUM` memakai MAC, bukan hardcode COM3.
- Koleksi HID mouse harus di-resolve ulang setiap kali (path berubah setelah resume).
- SPP COM port dipakai bersama perangkat lain di PC ini (ada 7 port Bluetooth) — jangan asumsur COM3 selalu EarFun.

## 7. Pendekatan yang dipertimbangkan

1. **Pasang tool existing** (EarKit untuk earbud + HaloBattery/mouse-battery-tray untuk mouse). Risiko paling rendah, tapi dua ikon tray, UI bukan Bahasa Indonesia, dan tidak bisa menyesuaikan info yang ditampilkan. Ditolak.
2. **Satu aplikasi tray terpadu (dipilih).** Satu ikon, satu panel, Bahasa Indonesia, logika dibangun di atas protokol yang sudah terbukti oleh spike. Risiko sedang, tapi sesuai kebutapan dan bisa diverifikasi langsung di PC ini.
3. **Spike saja.** Sudah dilakukan — berhasil untuk dua perangkat, jadi tidak ada lagi ketidakpastian teknis.

## 8. Rencana implementasi (keputusan saya, bukan keputusan pengguna)

- Bahasa: Python 3.14, file `.pyw` (tanpa console), dijalankan dari `C:\Hermes\Output\device-monitor\app\`.
- Tray: `Shell_NotifyIcon` via ctypes; ikon digambar dengan GDI (angka + warna: hijau ≥50, kuning ≥20, merah <20).
- Panel: jendela `tkinter` tanpa border, theme gelap, diposisikan di atas taskbar dekat ikon tray.
- Polling: mouse tiap 15 detik, earbud tiap 10 detik. Baca ulang path HID dan COM setiap kali.
- Mouse: kirim `08 04 … 49`, terima 17 byte, validasi checksum `0x55 − sum(16 byte)`, parse byte 6/7/8-9. Kalau tidak jawab → status "mouse mungkin tidur", jangan tampilkan angka lama sebagai angka segar.
- Earbud: frame GAIA `FF 04 00 N 00 0A <cmd> [payload]`; parse respons `FF 03 … 83xx`; `0xFF` → "N/A".
- Perintah tulis:
  - Noise mode: set `0x0314 [0=Off|1=ANC|2=Ambient]`, query `0x0315`
  - ANC sub-mode: set `0x033A [0..4]`, query `0x033B`
  - Transparency sub-mode: set `0x033C [0=Default|1=Natural]`, query `0x033D`
  - Game mode: set `0x0312 [0|1]`, query `0x0313`
  - In-ear detection: set `0x0349 [0=aktif|1=mati]`, query `0x034A`
  - EQ 10 band: tulis `0x0E01` (vendor `0x001D`) untuk 10 band, preset disimpan lokal
- Setiap perubahan mode diverifikasi dengan query ulang setelah 200–400 ms.
- Auto-start: shortcut `.lnk` di `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`.
- Hotkey: `Ctrl+Alt+N` cycle noise mode, `Ctrl+Alt+G` toggle game mode.

## 9. Yang masih perlu diputuskan saat implementasi

- Daftar preset EQ yang dipakai (bisa mulai dari 3 preset netral/bass/vocal, atau pengguna punya angka favorit dari app EarFun).
- Apakah notifikasi baterai rendah perlu toast atau cukup warna ikon + balloon tray.

## 10. Cara verifikasi nanti

1. Jalankan `app/tray.pyw`, screenshot tray + panel.
2. Bandingkan angka mouse dengan `probe_mouse.py` — harus sama.
3. Bandingkan angka earbud dengan `probe_earbud.py` dan Settings › Bluetooth — kiri harus 40% pada saat spike.
4. Tekan tombol ANC → Ambient, lalu jalankan `probe_earbud.py` lagi → query `0x0315` harus berubah.
5. Cabut dongle / matikan earbud → aplikasi harus menampilkan N/A, tidak crash.
