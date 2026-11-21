# Dossier Fitur — VXE R1 SE+ & EarFun Air Pro 4

Tanggal pengumpulan: 2026-11-21. Sumber: dokumen protokol WaveTune, EarKit, EncoDeck, Gadgetbridge, PairFree, OpenMouse/@openmouse/protocol, OpenVXE, atk-control, atkctl, manual produk, dan review. Status bukti: **teruji** (terbukti di PC ini), **hardware-tested** (diuji pihak ketiga), **source-derived** (dari kode implementasi), **review-only** (klaim review/pemasaran).

## 1. EarFun Air Pro 4 (firmware TW600-3091_20250919_v0.4.1)

Identitas: GAIA v3 over RFCOMM/SPP, vendor `0x000A` (EQ memakai `0x001D`). Frame request `FF 04 00 N 00 0A <cmd> [payload]`, respons `FF 03 ... 83xx`.

### 1.1 Terbukti di PC ini (spike 2026-11-21)

| Fitur | Query | Hasil |
|---|---|---|
| Firmware | `0x0309` | `TW600-3091_20250919_v0.4.1` |
| Baterai kiri | `0x0306` | 40% |
| Baterai kanan | `0x0307` | 50% |
| Baterai case | `0x0317` | `0xFF` = tidak tersedia (earbud di luar case) |
| Noise control | `0x0315` | 1 = ANC |
| Sub-mode ANC | `0x033B` | 3 = Balanced ANC |
| Sub-mode Ambient | `0x033D` | 1 = Natural |
| Game mode | `0x0313` | 0 = off |
| In-ear detection | `0x034A` | 0 = aktif |
| Multipoint | `0x0326` | 0 = off |
| Codec | `0x032F` | `0x13` = aptX Adaptive Lossless |

### 1.2 Bisa dibaca/ditulis dari PC

| Fitur | Query | Set | Opsi | Status |
|---|---|---|---|---|
| Noise master | `0x0315` | `0x0314 [m]` | 0 off, 1 ANC, 2 Ambient | query teruji; set source-derived |
| ANC sub-mode | `0x033B` | `0x033A [m]` | 0 AI Ear, 1 Wind, 2 Strong, 3 Balanced, 4 AI Environment | query teruji; set belum diuji |
| Ambient sub-mode | `0x033D` | `0x033C [m]` | 0 Default, 1 Natural | query teruji; set belum diuji |
| Game mode | `0x0313` | `0x0312 [0/1]` | off/on | query teruji |
| In-ear detection | `0x034A` | `0x0349 [v]` | 0 aktif, 1 nonaktif (EncoDeck pakai bitmask 0/15) | query teruji; encoding konflik |
| Multipoint | `0x0326` | `0x0327 [0/1]` + reboot `0x0308` | off/on | **berisiko**: reboot, konflik mutlak dengan LDAC |
| Codec | `0x032F` | `0x032E [c]` + reboot `0x0308` | 0 Stable, 1 aptX, 3 aptX Adaptive, 8 LDAC, 0x13 Lossless | **berisiko**: reboot; encoding index vs bitmask konflik |
| Status mode audio | `0x034D` | — | 0x03 aptX, 0x02 Stable/LDAC, 0 idle | source-derived |
| Advanced audio | `0x034C` | `0x034B [0/1]` | 0 Fast Pair, 1 LE Audio | tidak terverifikasi |
| Prompt volume | `0x0339` | `0x0338 [0..4]` | 0 maks, 4 mati (wire dibalik slider) | source-derived |
| Find device | `0x0333` | `0x0332 [0..3]` | 0 mati, 1 kiri, 2 kanan, 3 dua-duanya | source-derived; encoding konflik |
| Mic mode | `0x0331` | `0x0330 [0..2]` | 0 auto, 1 kiri, 2 kanan | source-derived |
| Touch lock | `0x0335` | `0x0334 [0/1]` | 0 aktif, 1 terkunci | source-derived; encoding konflik |
| Gesture | `0x030B` | `0x030A [4 byte]` | gesture 01 single / 02 double / 03 triple / 11 long; aksi 16 none, 1 play, 2 vol+, 3 vol-, 4 prev, 5 next, 6 asisten, 7 game, 8 noise cycle, 9/10/11 sub-cycle, 13 redial | source-derived |
| Auto power-off | `0x0348` | `0x0347 [v]` | never, 5/10/30/60/120 mnt (nilai never 0 vs 0xFF konflik) | source-derived |
| Paired host | `0x032C` | connect `0x0329`, disconnect `0x032A` | — | source-derived; tidak ada forget |
| EQ 10 band | `0x0E02` ditolak | `0x0E01` (vendor `0x001D`) | 31.5/63/125/250/500/1k/2k/4k/8k/16k Hz, ±6 dB, gain_raw=val*36 | **write-only**, ACK `0x0F81 [01]` |
| Reboot | — | `0x0308 []` | — | SPP putus ~20 dtk saat reboot |

### 1.3 Tidak bisa / tidak boleh dari PC

- Hearing test "My Sound Profile" — murni di HP, hasilnya kurva 10 band.
- Nama preset EQ — firmware tidak punya preset manager; `0x0E02` → `0x0F82 NOT_SUPPORTED`.
- Bahasa prompt suara — voice pack lewat kanal update `0x00007034`, bukan GAIA SPP.
- Firmware update/OTA — kanal khusus vendor.
- Status pakai fisik (wear) dan status charging — `0x034A` hanya toggle setting; baterai TW600 hanya status+persen.
- Factory reset `0x0036` — destruktif, dilarang.
- Spatial audio, bass enhancement, manner mode, game EQ, DAC, L/R balance, Auracast, AI translation, volume limit — milik model/frame EF lain, bukan TW600.
- Ganti nama perangkat — tidak ada command ID yang bisa dipercaya.

### 1.4 Konflik yang belum terselesaikan

- Codec: WaveTune pakai index (0/1/3/8/0x13); PairFree/EncoDeck pakai bitmask (1/2/8/16).
- EQ: `gain_raw=val*36` vs `freq*3, gain*60, Q*4096`; master gain `FF 98` vs `FE 98`.
- ANC/transparency sub-mode: peta WaveTune vs PairFree/EncoDeck berbeda.
- Touch lock: 0/1 vs 0/1/2/3. Find device: 0..3 vs bitmask.
- Auto power-off "never": 0 vs `0xFF`.
- Set perintah (kecuali baterai/query/EQ write) belum diuji hardware di PC ini.

## 2. VXE R1 SE+ / ATK Dragonfly R1 SE+ (dongle `3554:F58E`)

### 2.1 Spesifikasi

| Fitur | Nilai | Status |
|---|---|---|
| Sensor | PixArt PAW3395 SE | fakta |
| DPI | klaim 10–18000 step 10; grid nyata 200–18000 (step 50 sampai 10000, step 100 setelahnya), 235 kode valid | klaim vs source-derived |
| DPI stage pabrik | 4 stage: 400 / 800 / 1600 / 3200; unit ini terbaca 950/1650/1200/2950 | faktur+klaim |
| Polling 2.4G | 250/500/1000 Hz di live setting; EEPROM kode 08=125 … 40=8000 | source-derived |
| Polling kabel | hingga 1000 Hz | klaim |
| Polling Bluetooth | tidak ditemukan | — |
| LOD | 1 mm / 2 mm (kode 1/2); unit ini terbaca kode 1 | source-derived |
| IPS / akselerasi | 400 IPS / 40 G | fakta (klaim 650/50 di sumber lain) |
| Switch | Huano Blue Glow / Translucent V2 | fakta |
| Encoder | FSWITCH E10 | fakta |
| Latensi klik | 1,19 ms kabel / 1,95 ms wireless (database pihak ke-3) | klaim |
| Berat | klaim 55 g, timbangan reviewer 58,1 g | fakta+klaim |
| Baterai | 520 mAh, klaim 70–75 jam @1000 Hz | fakta+klaim |
| Konektivitas | tri-mode 2.4G / BT 5.4 / USB-C | fakta |
| Tombol | 5 menurut manual, 6 record EEPROM (kiri, kanan, tengah, back, forward, DPI) | konflik |
| RGB | **tidak ada RGB** | fakta |
| LED indikator DPI | warna stage merah/hijau/biru/ungu; unit ini terbaca LED off | source-derived |
| Profil | 4 bank onboard | source-derived |
| Makro | 12 slot (384 byte/slot) | source-derived |

### 2.2 Bisa dikontrol dari PC

| Fitur | Cara | Status |
|---|---|---|
| Baterai (%, mV, charging) | HID output report `08 04 … 49`, koleksi `0xFF02:0x0002`, checksum `0x55-sum(16)` | **terbukti di PC ini** |
| DPI stage | EEPROM `0x000c`, 4 byte/stage; HID cmd `0x07`/`0x08` | read solid, write experimental |
| Polling rate | live-settings `0x0070` selector `0x0b` | read solid, write experimental |
| LOD | `0x0070` selector `0x03`, EEPROM `0x000a` | read solid, write experimental |
| Debounce | `0x00a9` / `0x0070` selector `0x02`; unit ini 8 ms | read solid, write experimental |
| Motion sync | advanced `0x00a9`; unit ini ON | read solid |
| Ripple control | `0x00a9` | peta ada, belum dibaca di unit ini |
| Angle snapping | `0x00bd`; unit ini off | read solid |
| Straight-line correction | `0x00a9` | peta ada, belum dibaca |
| Sleep timer | `0x00a9`; unit ini 60 dtk | read solid |
| Sensor performance mode | `0x00b5` (Basic/Competitive/Competitive MAX/13K) | terverifikasi di model lain |
| Warna LED DPI | `0x002c`, efek/brightness/speed `0x004c` | read solid |
| Remap tombol | EEPROM `0x0060–0x0074` | source-derived |
| Makro | slot `0x0300` | source-derived |
| Profil | COMPX `0x0a`/`0x0e`/`0x0f` | source-derived |
| Firmware update | bootloader `0xFFB1`/`0xFFB3` | source-derived, tidak diuji |

### 2.3 Catatan

- Bluetooth **tidak** mengekspos koleksi konfigurasi; semua setting lewat dongle 2.4G.
- Dua framing lain di keluarga vendor (BitMouse `0xFF05`, COMPX `0xFF04`) belum terbukti berlaku untuk `3554:F58E`.
- CID/MID tidak konsisten: 2,31 (atk-control & katalog) vs 2,32 (products.ts).
- atk-control 0.9.2 bisa membaca semua register di R1 SE+ tetapi write masih experimental; OpenVXE mengklaim live-write.

## 3. Sumber

- https://github.com/onlymash/WaveTune/blob/master/docs/api/EARFUN_BLUETOOTH_API.md
- https://github.com/ChuiFeng-wind/EarKit · https://github.com/TIANLI0/EncoDeck/tree/f893e15
- https://codeberg.org/Freeyourgadget/Gadgetbridge · https://gadgetbridge.org/gadgets/headphones/earfun/
- https://github.com/Omega-Destroyer/PairFree/blob/main/docs/earfun/PROTOCOL.md
- https://github.com/ivancacic/vxe-battery-tray/blob/main/PROTOCOL.md
- https://github.com/BuSd777/OpenVXE · https://github.com/HeyOkay/HaloBattery/blob/main/docs/protocols.md
- https://github.com/NasirA1991/atk-control/blob/main/docs/PROTOCOL.md · https://github.com/cobanov/atkctl/blob/main/docs/PROTOCOL.md
- https://github.com/OpenMouse-Project/mouse-protocol/blob/main/src/atk/index.ts
- https://manuals.plus/asin/B0FN7K443F · https://www.amazon.com/dp/B0FN7H1M99

## 4. Hasil uji end-to-end 2026-11-21 (pembaruan konflik)

Semua nilai uji dikembalikan ke semula. Skrip: `scripts/probe_mouse.py`, `verify_mouse.py`, `probe_earbud.py`, `verify_earfun.py`, `verify_earfun2.py`.

### Mouse — protokol 0xFF02 terbukti
- Frame baca: `08 08 00 <hi> <lo> 0A 00… <checksum>`; frame tulis: `08 07 00 <hi> <lo> <len> <data…> <checksum>`. Jumlah 17 byte = `0x55 mod 256`.
- 10 register (`0000`, `000A`, `000C`, `002C`, `004C`, `0070`, `00A9`, `00B5`, `00BD`, `0060`) terbaca dengan checksum valid.
- `0000`: pair `01 54` = polling 1000 Hz, pair `04 51` = 4 stage, pair `01 54` = stage aktif 1.
- Live-setting group 4 byte berjumlah `0x55`: `[selector, value, 0x00, 0x55-selector-value]`. Ini **mengoreksi** rumus lama `(0x55-value)`.
- Bukti tulis: debounce selector `02` ditulis `09` → readback `02 09 00 4A`; ditulis `08` → readback `02 08 00 4B`; dikembalikan 8.
- LOD selector `03` terbaca `03 01 00 51` = level 1 / 1 mm.
- Kesimpulan: sisi tulis **tidak lagi experimental** untuk row live-settings `0x0070` pada dongle `3554:F58E`. Register EEPROM lain belum diuji tulis.

### EarFun — konflik terselesaikan
- Noise master `0314`/`0315`: `1 → 2 → 1`, readback cocok.
- ANC sub `033A`/`033B`: `3 → 2 → 3`, readback cocok. Peta WaveTune (0 AI Ear, 1 Wind, 2 Strong, 3 Balanced, 4 AI Env) **terpakai**.
- Ambient sub `033C`/`033D`: `1 → 0 → 1`, readback cocok.
- Game `0312`/`0313`: `0 → 1 → 0`, readback cocok.
- In-ear `0349`/`034A`: `0 → 1 → 0`, readback cocok → encoding **0/1**, bukan bitmask 0/15.
- Touch lock `0334`/`0335`: `1 → 0 → 1`, readback cocok → encoding **0/1**, bukan bitmask 0/1/2/3.
- Codec: nilai aktif `0x13` dan mode audio `034D = 3` (keluarga aptX) → **index 19 = Lossless**, bukan bitmask. Tulis tidak diuji karena memicu reboot; interpretasi aman untuk tampilan.
- EQ: query `0E02` dijawab `8E02 01` = NOT_SUPPORTED → write-only terkonfirmasi. Konflik gain (`val*36` vs `gain*60`) **masih terbuka**, sengaja tidak diuji agar EQ pengguna tidak berubah.
- Mic `0330`/`0331`: write menyebabkan SPP putus beberapa detik; setelah reconnect nilai terbaca 0 (dikembalikan). Encoding 0/1/2 tidak diuji lebih lanjut.
- Auto power-off `0348`: tidak merespons di TW600 → dianggap tidak tersedia.
- Prompt volume `0339`: pembacaan tidak stabil → masih source-derived.
- Find device `0332`: tidak diuji (memainkan suara keras).

State akhir terverifikasi: noise 1 · ANC 3 · Ambient 1 · game 0 · in-ear 0 · touch 1 · mic 0 · codec 0x13.

## 5. Putaran konflik lanjutan (satu per satu, 2026-11-21)

### Mouse
- Angle snap: selector `01` **tidak ada** di live row `0x0070` (yang ada hanya grup debounce `02`). Menambah entri baru tidak bisa dibatalkan, jadi dilewati tanpa perubahan.
- Polling: `0000` baseline `01 54 04 51 01 54 00 55 00 55` ditulis `02 53 …` = **500 Hz**, readback cocok, lalu dikembalikan persis ke `01 54`. Write EEPROM di luar `0x0070` dengan demikian **terbukti**.
- Polling >1000 Hz: tidak diuji. Receiver ini 1K; kode 2000/4000/8000 berisiko membuat HID tidak merespons.
- Bluetooth configuration: dilewati, tidak ada collection konfigurasi di link BT.
- DPI 10–18000 vs 200–18000: dilewati. Stage 1–2 terbaca 400/800 dari `000C`, sesuai manual; klaim pemasaran tidak bisa dibuktikan lewat write tanpa mengubah DPI secara tidak aman.

### EarFun
- Prompt volume `0339`: 6 kali query berturut-turut menghasilkan `8339 00 00` semua → **stabil**, nilai 0. Ketidakstabilan sebelumnya karena SPP belum pulih setelah uji lain.
- Mic `0330`/`0331`: ditulis `1` → readback 1, ditulis `2` → readback 2, dikembalikan `0` → final 0. Encoding **0/1/2 terkonfirmasi**. Set mic memutus SPP beberapa detik; perlu reconnect sebelum query.
- Gestur `030B`: payload ternyata **33 byte**, bukan 17: 1 byte status + 16 pasangan `[jenis_gesture, aksi]`. Pasangan pertama: `(01,03)` kiri single=volume down, `(01,02)` kanan single=volume up, `(02,01)` double=play/pause, `(03,04)`/`(03,05)` triple=prev/next, `(11,08)` long=noise toggle. Write `030A` dengan payload `[00,00,01,16]` → readback aksi kanan-single 16, lalu dikembalikan ke 2. **Peta terkonfirmasi**, payload akhir `000103010202010201030403051108110804000400050005000606060613041304`.
- Catatan koreksi: uji gestur pertama salah parsing (mengira 17 byte dan mengambil byte jenis sebagai aksi) sehingga kanan-single sempat berubah ke 1; sudah dikembalikan ke nilai asli 2 dan diverifikasi.

### Konflik yang sengaja tidak diuji
- EQ gain `val*36` vs `gain*60`: `0E02` ditolak, kurva tidak bisa dibaca → menulis akan menimpa EQ pengguna.
- Codec/multipoint writes: memicu reboot ~20 dtk dan SPP putus; interpretasi index sudah cukup untuk tampilan.
- Find device `0332`: memainkan suara keras.
- Factory reset `0036`: destruktif.

State akhir putaran lanjutan: mouse polling 1000 Hz · debounce 8 · LOD 1 · EarFun mic 0 · prompt 0 · gesture kanan-single 2 · noise 1 · ANC 3 · Ambient 1 · game 0 · in-ear 0 · touch 1.

**Catatan restore noise:** sempat terbaca `0` (Normal) setelah putaran konflik dan set `0x0314 [1]` tidak langsung merespons. Setelah koneksi SPP stabil, diagnosis ulang menunjukkan `0x0315 = 0001` (ANC) tanpa perubahan kode, jadi state baseline pulih. Pembacaan ulang terakhir: noise 1 · ANC 3 · Ambient 1 · game 0 · in-ear 0 · touch 1 · mic 0 · codec 0x13.

**Kontrol nyala/mati gestur:** touch lock `0335`/`0334` — `0` = gestur aktif, `1` = gestur mati/terkunci. Status saat ini `1` (mati). Diuji write `0` → read `0`, write `1` → read `1`, lalu dikembalikan ke `1`. Mockup menyediakan tombol eksplisit "Nyalakan gestur" / "Matikan gestur" di tab TWS → Mode &amp; Suara.
