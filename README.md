# VXE R1 SE+ & EarFun Air Pro 4 — Device Monitor

Panel UI (warm dark glassmorphism + monochromatic cream bento) untuk memantau dan
mengontrol mouse **VXE R1 SE+** dan earbud **EarFun Air Pro 4** dari PC.

## Isi repo

- `app/` — aplikasi web (Vite + React + TypeScript). UI fully interactive + full animation.
- `html/mockup-panel-v3.html` — mockup statis acuan fitur.
- `docs/UI.md` — design system, card archetypes, animation choreography, dan pemetaan fitur.
- `docs/FITUR-LENGKAP.md` — dossier fitur perangkat + hasil verifikasi protokol.
- `scripts/` — skrip probe/verifikasi protokol (Python, stdlib saja).

## Menjalankan

```bash
cd app
npm install
npm run dev      # development
npm run build    # typecheck + production build
npm run preview  # sajikan hasil build
```

## Menjalankan dengan perangkat fisik

Jalankan bridge Python (stdlib, tanpa dependency) lalu UI:

```bash
python scripts/bridge.py          # http://127.0.0.1:8765
cd app && npm run dev             # UI otomatis poll /api/status tiap 5 detik
```

UI menulis hanya untuk perintah aman: mouse `polling`, `lod`, `debounce`; TWS
`noiseMode`, `ancSub`, `ambSub`, `game`, `inEar`, `gestureLock`, `mic`, `prompt`,
dan `eq`. Codec/multipoint sengaja tidak ditulis otomatis karena memicu reboot.

## Status integrasi perangkat

UI terhubung ke perangkat fisik lewat bridge HTTP lokal (`scripts/bridge.py`).
Data perangkat di-poll tiap 5 detik; kontrol aman langsung menulis ke HID/GAIA
dengan readback. Codec/multipoint/EQ-write berisiko tetap dibatasi (lihat `docs/UI.md`
Section 8 dan `docs/FITUR-LENGKAP.md`).

## Protokol yang sudah terverifikasi

- Mouse: HID `0xFF02`, baca/tulis register, checksum `0x55`, live-setting `0x0070`,
  EEPROM `0x0000` (polling) — semua dengan write → readback → restore.
- EarFun: GAIA v3 over RFCOMM SPP, vendor `0x000A` (EQ `0x001D`), battery
  `0306/0307/0317`, noise `0314/0315`, sub-mode `033A/033B/033C/033D`, game
  `0312/0313`, in-ear `0349/034A`, touch lock `0334/0335`, mic `0330/0331`,
  gestur `030A/030B`, codec `032E/032F`.
