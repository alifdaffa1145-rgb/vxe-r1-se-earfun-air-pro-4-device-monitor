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

## Status integrasi perangkat

UI sepenuhnya state-driven dan kontrolnya memakai state yang sama dengan perintah
protokol asli (peta command ada di `docs/UI.md` Section 8). Saat ini data perangkat
bernilai contoh yang diambil dari hasil probe nyata; jembatan ke perangkat fisik
(HID mouse / GAIA earbud) belum dihubungkan ke bundle web.

## Protokol yang sudah terverifikasi

- Mouse: HID `0xFF02`, baca/tulis register, checksum `0x55`, live-setting `0x0070`,
  EEPROM `0x0000` (polling) — semua dengan write → readback → restore.
- EarFun: GAIA v3 over RFCOMM SPP, vendor `0x000A` (EQ `0x001D`), battery
  `0306/0307/0317`, noise `0314/0315`, sub-mode `033A/033B/033C/033D`, game
  `0312/0313`, in-ear `0349/034A`, touch lock `0334/0335`, mic `0330/0331`,
  gestur `030A/030B`, codec `032E/032F`.
