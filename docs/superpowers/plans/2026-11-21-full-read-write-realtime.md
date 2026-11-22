# Full Read/Write Realtime — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Semua kontrol di panel Device Monitor membaca dan menulis perangkat fisik (VXE R1 SE+ & EarFun Air Pro 4) secara realtime, dengan rollback otomatis bila write gagal.

**Architecture:** Satu bridge Python (HID `0xFF02` untuk mouse, GAIA/SPP untuk TWS) menyimpan cache per perangkat + lock per perangkat. UI React polling `GET /api/status` tiap 2 detik dan POST hanya key yang ada di allowlist. Setiap write diikuti readback; kegagalan write mengembalikan nilai lama di UI.

**Tech Stack:** Python 3.14 stdlib (ctypes Win32), React + TypeScript + Vite.

**Spec:** `docs/FITUR-LENGKAP.md`, `references/device-protocols.md` (skill windows-peripheral-control).

## Global Constraints

- Python 3.14 + stdlib saja; tanpa pip dependency, admin, atau installer.
- UI Bahasa Indonesia; A4/Word hanya untuk dokumen terpisah.
- Tidak ada `.env`/kredensial di repo.
- Setiap write: baseline → tulis nilai uji → readback → restore → verifikasi restore. Readback, bukan ACK, yang membuktikan.
- Jangan tulis codec/multipoint/EQ kalau belum ada izin pengguna (reboot ~20 detik / write-only).
- Mouse harus bangun (digakakan fisik) sebelum probe; jalankan semua probe dalam satu proses.

## Review Focus

1. Write yang dibalas ACK tapi nilai tak berubah → UI harus revert, bukan menampilkan nilai palsu.
2. Perangkat tidur/offline saat write → pesan error spesifik + rollback, bukan "write gagal" generik.
3. UI memakai state lokal saat bridge offline → tampilan harus menandai data basi/terputus.
4. Polling 2 detik saat perangkat tidur → jangan membaca berulang (backoff), supaya API tetap instan.
5. Realtime TWS: SPP bisa putus sesaat setelah write (terutama mic) → buka ulang port dengan retry.

---

### Task 1: Peta register mouse (read-only)

**Files:**
- Create: `scripts/read_mouse_regs.py` (sudah ada)
- Modify: `scripts/bridge.py`

**Interfaces:**
- Consumes: `bridge.mouse_open()`, `bridge.mouse_io(h, frame)`, `bridge.mouse_frame(cmd, addr, data)`
- Produces: tabel register → payload hex + interpretasi field; fungsi `mouse_read()` mengembalikan field baru.

- [ ] **Step 1: Jalankan `python scripts/read_mouse_regs.py` setelah mouse digerakkan.** Harapan: baris `0000 000A 000C 002C 004C 0060 0070 00A9 00B5 00BD` terisi hex (bukan `ERR`).
- [ ] **Step 2: Catat baseline** tiap register ke `docs/FITUR-LENGKAP.md`.
- [ ] **Step 3: Tambahkan field yang terbukti terbaca** ke `mouse_read()` di `scripts/bridge.py` (mis. `led`, `sleep`, `motionSync`, `angleSnap`, `dpiStages`).
- [ ] **Step 4: Verifikasi** `GET /api/status` memuat field baru; UI menampilkan nilai yang sama dengan probe.
- [ ] **Step 5: Commit** `feat(mouse): baca register konfigurasi tambahan`.

### Task 2: Write reversible DPI stage, LED, motion sync, sleep, angle snap

**Files:**
- Modify: `scripts/bridge.py` (`mouse_write`, allowlist), `scripts/read_mouse_regs.py` (skrip uji)
- Test: `scripts/probe_mouse_write2.py`

**Interfaces:**
- Consumes: `mouse_frame`, `mouse_io`; alamat register dari Task 1.
- Produces: `mouse_write(key, value)` mendukung `dpiStage`, `led`, `motionSync`, `sleep`, `angleSnap`; `TWM_*` tidak berubah.

- [ ] **Step 1: Untuk tiap field, tulis nilai uji berbeda dari baseline, readback, restore.** Contoh DPI stage: `000C` grup stage diubah 400→600→400.
- [ ] **Step 2: Hanya field dengan readback cocok** yang masuk `MOUSE_WRITABLE` di `app/src/App.tsx`.
- [ ] **Step 3: Field yang gagal direstore** dicatat "unavailable" dan UI dinonaktifkan dengan label.
- [ ] **Step 4: Commit** `feat(mouse): write DPI/LED/motion sync/sleep/angle snap`.

### Task 3: Tombol & makro mouse (baca)

**Files:**
- Modify: `scripts/bridge.py` (`mouse_read`), `app/src/components/Cards.tsx`

- [ ] **Step 1: Baca `0060` (tombol) dan cetak pasangan tombol→aksi.**
- [ ] **Step 2: Tambahkan ke `mouse_read()` sebagai `buttons`.**
- [ ] **Step 3: UI menampilkan pemetaan tombol read-only; remap ditulis hanya bila readback membuktikan.**
- [ ] **Step 4: Commit.**

### Task 4: TWS codec & multipoint (butuh izin)

**Files:**
- Modify: `scripts/bridge.py` (`TWS_SET`/`TWS_QUERY`), `app/src/App.tsx` (allowlist)
- Test: `scripts/probe_tws_codec.py`

- [ ] **Step 1: Hanya bila pengguna menyetujui reboot.** Tulis codec uji, tunggu 20 detik, buka ulang COM, readback.
- [ ] **Step 2: Kalau readback cocok, tambahkan `codec` ke allowlist; kalau tidak, label "read-only".**
- [ ] **Step 3: Multipoint sama; catat pemutusan koneksi.
- [ ] **Step 4: Commit.**

### Task 5: Realtime + rollback UI

**Files:**
- Modify: `app/src/App.tsx`, `app/src/state.ts`, `app/src/components/Cards.tsx`, `scripts/bridge.py`

- [ ] **Step 1: Polling 2 detik (selesai).**
- [ ] **Step 2: Write sukses → konfirmasi readback; gagal → rollback + pesan error (selesai).**
- [ ] **Step 3: Hubungkan semua kontrol yang `onChange` no-op ke `dispatch` + allowlist.
- [ ] **Step 4: Verifikasi tiap kontrol di browser: klik → nilai bridge berubah → nilai semula dikembalikan.
- [ ] **Step 5: Commit.**

### Task 6: Build + verifikasi akhir

- [ ] **Step 1: `npm run build` bersih.**
- [ ] **Step 2: Port 8765/4173 LISTENING; GET instan (<100 ms saat cache hangat).**
- [ ] **Step 3: Status koneksi jujur; semua write terverifikasi readback.**
- [ ] **Step 4: Push; verifikasi repo tak punya `.env`.**
