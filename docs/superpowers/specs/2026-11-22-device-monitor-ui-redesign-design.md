# Device Monitor — desain ulang panel (2026-11-22)

## Intent
Panel Device Monitor dipakai untuk mengubah pengaturan mouse VXE R1 SE+ dan TWS EarFun Air Pro 4 secara langsung dari PC. Versi saat ini berfungsi secara teknis tetapi tampil sebagai prototipe: emoji sebagai ikon, teks teknis 10–11 px, blob glow dekoratif, density tidak konsisten, dan konfirmasi codec memakai dialog browser bawaan yang mudah terlewat. Tujuannya: panel yang terasa seperti utilitas hardware komersial yang dipercaya, tanpa mengubah protokol perangkat yang sudah terverifikasi.

## Goals
- Arah visual: **konsol instrumen gelap** dengan satu aksen amber; information density **seimbang**.
- Hierarki jelas: identitas perangkat → status koneksi → metrik utama → kontrol → detail teknis.
- Setiap aksi yang mengubah perangkat memberi feedback: menunggu, berhasil, gagal, dan revert bila gagal.
- Konfirmasi aksi berisiko (codec/multipoint) tampil sebagai panel dalam aplikasi, bukan `window.confirm`.
- Tetap responsif down to 360 px, fokus keyboard terlihat, `prefers-reduced-motion` dihormati.

## Non-goals / anti-goals
- Mengubah logika bridge, register mouse, atau perintah GAIA yang sudah terverifikasi.
- Menambah fitur baru (EQ preset, multipoint write, find-device) — multipoint tetap dinonaktifkan karena konflik dengan LDAC.
- Tampilan "gaming RGB" dengan banyak glow, gradient, atau animasi dekoratif.
- Teks spesifikasi teknis sebagai konten utama; detail dipindah ke sekunder/tertlapis.

## Constraints
- Stack existing: React 19 + Vite + TypeScript, tanpa dependency UI baru.
- Aset harus offline-friendly: tidak bergantung pada Google Fonts/CDN.
- Perangkat bisa tidur (mouse) atau restart (TWS); UI tidak boleh menampilkan angka tanpa status yang jelas.
- Perubahan codec memutus SPP ±20 detik, jadi konfirmasi wajib sebelum perintah dikirim.

## Approaches
1. **Konsol instrumen gelap + amber** (dipilih). Satu aksen, angka telemetri monospaced, panel datar berborder 1 px, ikon SVG, grid 8 px. Paling cocok untuk utilitas hardware dan menyembunyikan kompleksitas tanpa kehilangan data.
2. **Panel studio terang + biru.** Lebih tenang, tetapi kontras dengan identitas perangkat gaming dan membutuhkan revisi warna status yang lebih besar.
3. **Telemetri performa gelap + sian.** Dekat dengan perangkat lunak gaming, tetapi berisiko tampak seperti template RGB dan mendorong density padat yang ditolak pengguna.

## Keputusan desain
- **Warna:** base `#0E1116`, panel `#151A21`, panel naik `#1B222B`, border `#28313B`, teks `#E7ECF2`, sekunder `#95A2B0`, amber `#F2A93B`, sukses `#46B85C`, bahaya `#E5534B`.
- **Tipografi:** satu keluarga sans (`Inter`/`Segoe UI`/system-ui) untuk seluruh UI; monosistem (`JetBrains Mono`/`Cascadia Mono`/`ui-monospace`) hanya untuk angka telemetri, alamat register, dan nilai DPI. Tanpa ALL-CAPS dekoratif.
- **Layout:** shell dua kolom — rail ikon 56 px di kiri, area kerja di kanan. Header perangkat, ringkasan status, baris filter, lalu grid kartu 1/2/3 kolom sesuai lebar. Semua konten rata kiri; angka metrik rata kiri dengan unit lebih kecil.
- **Komponen:** kartu punya header (ikon SVG + judul + kategori kecil), isi kontrol, dan footer opsional berupa catatan teknis berukuran 12 px. Chip/segmen/toggle memakai target minimal 32 px dengan jarak 8 px.
- **Feedback:** status koneksi di header; badge "Menerapkan…" saat POST berjalan; toast/error inline bila gagal; readback dari perangkat mengganti nilai UI. Untuk codec, klik membuka panel konfirmasi dengan konsekuensi (restart ±20 dtk, SPP putus) dan tombol "Ganti codec"/"Batal".
- **Ikon:** hapus emoji di `Card.icon`; gunakan satu komponen `Icon` berbasis SVG (battery, sensor, signal, gear, waves, link, gesture, sliders, file).
- **Motion:** satu entrance halus untuk shell, transisi 140–220 ms untuk perubahan status, tanpa animasi bernapas. `prefers-reduced-motion` mematikan transisi.

## Implementasi
- `styles.css` ditulis ulang sebagai sistem token + komponen; tidak ada patch bertumpuk pada variabel lama.
- `Cards.tsx`: `Card.icon` diganti `Icon` SVG; konfirmasi codec dipindah ke state lokal; multiplex toggle tetap disabled dengan penjelasan.
- `App.tsx`: hapus elemen glow; sambungkan status "menerapkan" ke komponen kartu; toast/error tetap di barkah.
- `Hero.tsx`, `TopNav.tsx`, `FilterBar.tsx`: disederhanakan menjadi header instrumen; tombol non-fungsional dihapus.
- `index.html`: judul tanpa emoji.

## Verifikasi
- `npm run build` sukses.
- Browser: buka `http://localhost:4173/`, periksa tab Mouse/TWS, filter, chip codec, modal konfirmasi, dan status perangkat; screenshot disimpan di `img/`.
- Perangkat: API `POST /api/tws codec` 8↔19 dengan readback dan persistensi ≥30 detik; mouse write test tetap `SEMUA OK: True`.
- `git push` ke `origin/feat/warm-glass-interactive-ui`.
