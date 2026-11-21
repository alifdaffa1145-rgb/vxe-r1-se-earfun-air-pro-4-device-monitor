# UI Design System, Adaptive Card & Full Animation Specification (`prompt.md`)

## 1. Objective & Role
Act as a Senior UI/UX Engineer, Motion Designer, and Frontend Architect. Refactor and implement the application user interface strictly following the **Warm Dark Glassmorphism & Monochromatic Cream Bento** design system specified below, engineered as a **fully interactive, fluidly animated experience**.
- **Visual Strictness:** Every color token, glass blur, specular border, radius, typography scale, and cream-on-charcoal contrast rule must strictly follow this specification.
- **Structural & Card Adaptation:** Do **not** force static placeholder widgets from the visual reference if they do not match the existing mockup. Adapt the Bento grid proportions, card count, and internal card widgets to faithfully represent **100% of the features already present in the repository's existing mockup**, styled using the **Card Archetypes** in Section 6.
- **Full Interactivity & Motion:** Every navigation item, filter pill, Bento card, chart bar, selection matrix, and toggle control must be genuinely interactive (not static) with physics-based micro-interactions, layout transitions, and staggered entrance animations running at 60fps.

---

## 2. Core Aesthetic Direction
- **Visual Style:** Warm Dark Glassmorphism with tactile frosted surfaces, soft ambient lighting, and high-contrast off-white/cream active states.
- **Atmosphere:** Calm, executive, tactile, and alive—avoiding harsh pure blacks (`#000000`) or saturated neon colors.
- **Surface Hierarchy:** Depth is achieved through layered translucent warm-charcoal panels (`backdrop-filter: blur`), thin `1px` specular borders, subtle cursor-reactive glass highlights, and smooth material inversion (translucent dark glass vs. solid warm cream) to denote active focus.

---

## 3. Color Palette & Design Tokens

```css
:root {
  /* Ambient Canvas Background */
  --bg-ambient-base: #24211E;
  --bg-ambient-glow-warm: rgba(196, 179, 158, 0.22);
  --bg-ambient-glow-deep: #1B1917;

  /* Glass & Card Surfaces */
  --surface-window-glass: rgba(46, 43, 40, 0.72);
  --surface-card-primary: rgba(255, 255, 255, 0.06);
  --surface-card-hover: rgba(255, 255, 255, 0.09);
  --surface-card-nested: rgba(255, 255, 255, 0.09);
  --surface-dock-glass: rgba(255, 255, 255, 0.14);
  --surface-pill-inactive: rgba(255, 255, 255, 0.04);

  /* High-Contrast Active & Inverted Surfaces */
  --surface-cream-solid: #F7F5EE;
  --surface-cream-hover: #EFECE2;
  --surface-cream-muted: rgba(247, 245, 238, 0.18);

  /* Typography Colors */
  --text-on-dark-primary: #F7F5EE;
  --text-on-dark-secondary: #B5B0A8;
  --text-on-dark-muted: #8A857E;
  --text-on-cream-primary: #1E1C1A;
  --text-on-cream-secondary: #5C5852;

  /* Borders & Hairlines */
  --border-window-specular: rgba(247, 245, 238, 0.22);
  --border-card-subtle: rgba(247, 245, 238, 0.12);
  --border-card-hover: rgba(247, 245, 238, 0.26);
  --border-pill-outline: rgba(247, 245, 238, 0.32);
  --border-on-cream: rgba(30, 28, 26, 0.25);

  /* Blur & Elevation */
  --blur-window: blur(28px);
  --blur-card: blur(16px);
  --shadow-window: 0 32px 64px -16px rgba(15, 13, 11, 0.65);
  --shadow-card-hover: 0 16px 36px -12px rgba(10, 9, 8, 0.45);

  /* Radii */
  --radius-window: 32px;
  --radius-card-lg: 24px;
  --radius-card-md: 18px;
  --radius-badge: 12px;
  --radius-pill: 9999px;

  /* Motion & Physics Tokens */
  --ease-spring-snappy: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-spring-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  --duration-fast: 160ms;
  --duration-normal: 280ms;
  --duration-slow: 520ms;
}
```

---

## 4. Typography & Hierarchy
- **Font Family:** Clean geometric sans-serif (`'Plus Jakarta Sans'`, `'Inter'`, or `'SF Pro Display'`, sans-serif).
- **Tabular Numerals:** Enable `font-variant-numeric: tabular-nums` on all metrics, timers, counters, bitrates, and animated numbers to prevent layout jitter during count-up transitions.
- **Scale & Weight:**
  - **Hero Page Title (2-line stacked):** `32px–36px`, `font-weight: 600`, `line-height: 1.15`, `letter-spacing: -0.02em`, color `--text-on-dark-primary`.
  - **Primary KPI / Hero Numbers:** `36px–44px`, `font-weight: 400`, `letter-spacing: -0.03em`. Always pair with a smaller **superscript unit/symbol** (`14px–16px`, `vertical-align: super`, `margin-left: 2px`).
  - **Card Titles:** `15px–16px`, `font-weight: 600`.
  - **Micro Labels (positioned ABOVE values):** `11px–12px`, `font-weight: 400`, color `--text-on-dark-secondary`.
  - **Pill & Navigation Text:** `12px–13px`, `font-weight: 500`.

---

## 5. Spatial Layout & Outer Shell Architecture

### A. Viewport & Ambient Backdrop
- Full-viewport centered canvas (`min-height: 100vh`) featuring a warm dark radial gradient (`--bg-ambient-base`) with soft diffused beige/cream light leaks at the bottom-left and top-right corners that subtly breathe/drift (`14s ease-in-out infinite alternate`) behind the frosted glass panels.

### B. Floating Vertical Action Dock (Left Outside Main Frame)
- Positioned detached to the left of the main application window (`gap: 16px`).
- Vertical capsule container (`width: 52px`, `border-radius: var(--radius-pill)`, `background: var(--surface-dock-glass)`, `backdrop-filter: var(--blur-card)`, `border: 1px solid var(--border-window-specular)`, `padding: 8px`).
- Contains primary navigation icon buttons (`36px × 36px`) mapped from the mockup's main sections. Clicking an icon smoothly glides the active circular indicator (`rgba(247, 245, 238, 0.25)` or `--surface-cream-solid`) to the selected route and switches the active view.

### C. Main Application Glass Container
- Centered rounded container (`max-width: 1280px`, `width: 92%`, `border-radius: var(--radius-window)`, `background: var(--surface-window-glass)`, `backdrop-filter: var(--blur-window)`, `border: 1px solid var(--border-window-specular)`, `box-shadow: var(--shadow-window)`, `padding: 28px 32px`).
- **Bottom Pagination / View Dots:** Centered `16px` below the main window frame—interactive circular dots (`8px`), active dot morphs into an elongated pill (`width: 20px`) in `--surface-cream-solid`, inactive dots in `rgba(255,255,255,0.25)`.

---

## 6. Global Chrome & Adaptive Bento Card System

### 6.1 Top Navigation Header
1. **Left — Brand Monogram:** Minimal geometric logo mark (`24px`, `--text-on-dark-primary`) matching the existing app identity, with subtle hover rotation/scale.
2. **Center — Horizontal Pill Nav:** Inline list of primary tabs from the mockup (`gap: 8px`).
   - *Inactive state:* Transparent background, `--text-on-dark-secondary`, `padding: 8px 16px`.
   - *Active state:* Solid `--surface-cream-solid` sliding pill indicator (`border-radius: var(--radius-pill)`), `--text-on-cream-primary`, `font-weight: 600`.
3. **Right — User / Status Capsule:** Interactive outlined pill container (`border: 1px solid var(--border-pill-outline)`, `border-radius: var(--radius-pill)`, `padding: 4px 6px 4px 4px`) with circular avatar/icon (`34px`), 2-line primary & secondary label, and circular utility button (`32px`) that opens a popover/drawer or triggers its mockup action on click.

### 6.2 Hero Title & KPI Summary Strip
- Horizontal flex/grid row (`margin-top: 24px`, `align-items: center`, `justify-content: space-between`):
  1. **Left:** 2-line stacked Display Title derived from the active view in the mockup (animates via smooth vertical clip/fade when switching tabs).
  2. **Center-Left:** **Animated Segmented Circular Progress Ring (`84px × 84px`)** with thick rounded stroke segments (`8px` width) in `--surface-cream-solid` (active progress) and `--surface-cream-muted` (remaining), animating `stroke-dashoffset` smoothly on load and state updates, with animated percentage/metric text in the center.
  3. **Right (Borderless Metric Group):** Spacious stat blocks (`gap: 36px`) displaying key metrics from the mockup—each with a top micro-label (`11px` muted) directly above an animated large numeral (`38px` regular) with a superscript unit/symbol.

### 6.3 Filter Pill Bar & Quick Actions
- Horizontal row (`margin-top: 24px`, `justify-content: space-between`):
  - **Left Group:** Interactive row of outlined capsule filter/category pills (`border: 1px solid var(--border-pill-outline)`, `border-radius: var(--radius-pill)`, `padding: 7px 16px`, `font-size: 12px`). Clicking any pill immediately filters/highlights matching Bento cards and transitions the active pill to solid `--surface-cream-solid` with `--text-on-cream-primary`. Optional trailing circular `+` button (`34px × 34px`, solid cream, `90deg` icon rotation on hover).
  - **Right Group:** Circular solid `--surface-cream-solid` icon buttons (`34px × 34px`, `gap: 8px`) mapped to secondary quick actions in the mockup.

---

### 6.4 Adaptive Bento Grid & Card Archetypes (CRITICAL)
Construct the main workspace (`margin-top: 20px`, `gap: 20px`) as an **asymmetric Bento grid** (e.g., `68% / 32%` split or multi-row asymmetric grid) sized and structured specifically around the **features in the existing mockup**. Every feature card in the mockup must be built using one of the following **4 Card Archetypes**:

#### Archetype A: Master Interactive Feature Card (Primary Focus Module)
- **Container:** `border-radius: var(--radius-card-lg)`, `background: var(--surface-card-primary)`, `border: 1px solid var(--border-card-subtle)`, `padding: 22px`.
- **Top Header:**
  - Left: 40px rounded icon tile (18px radius) + Card Title `15–16px / 600`.
  - Right: status badge (11px, radius badge) or contextual meta.
- **Primary Zone:** one dominant animated element (e.g. battery ring, big numeral roll-up, or master toggle row).
- **Interactive Sub-widgets:** nested controls (segmented buttons, chips, toggles, sliders) using Archetype C styling at reduced padding.
- **Cursor Spotlight:** a `::before` radial highlight (`rgba(247,245,238,0.10)`, 240px) following the pointer with `--mx/--my` custom properties, clipped to the card radius.
- **States:** `idle` → `hover` (border `--border-card-hover`, shadow `--shadow-card-hover`, `translateY(-2px)`) → `active/focus` (solid cream inversion) → `disabled` (`opacity: .45`, no pointer).

#### Archetype B: Compact Metric / Status Card
- **Container:** `border-radius: var(--radius-card-md)`, `background: var(--surface-card-primary)`, `border: 1px solid var(--border-card-subtle)`, `padding: 16px 18px`.
- **Layout:** micro label (`11px`, `--text-on-dark-secondary`) directly above a large animated numeral (`30–34px`, `font-weight: 400`, tabular-nums) with superscript unit; optional mini progress bar/sparkline under the number.
- **Use:** secondary metrics, per-device battery levels, connection/status readouts.

#### Archetype C: Control & Selection Matrix Card
- **Container:** same surface as B but `padding: 18px`.
- **Widgets:** segmented control row, filter chips, toggle rows (switch), steppers, and the EQ slider bank.
- **Active rule:** selected control = solid `--surface-cream-solid`, `--text-on-cream-primary`, `font-weight: 600`; unselected = `--surface-pill-inactive` with `--text-on-dark-secondary`.
- **Feedback:** press scale `0.96`, spring back on release; toggle knob travel `14px` with `--ease-spring-bounce`.

#### Archetype D: Data / List / Log Card
- **Container:** `border-radius: var(--radius-card-md)`, `background: var(--surface-card-primary)`, `border: 1px solid var(--border-card-subtle)`, `padding: 16px 18px`.
- **Content:** dense tables, specification lists, gesture matrix, logs, and scrollable regions (`max-height` + thin custom scrollbar).
- **Rules:** tabular numerals for values; status markers reuse the legend (verified / readable / needs test / risky / unavailable); zebra-free, hairline row separators `rgba(247,245,238,0.08)`.

---

## 7. Animation Choreography

### 7.1 Global Motion Rules
- Animate **only** `transform`, `opacity`, `filter`, `stroke-dashoffset`, and `backdrop-filter` opacity; never animate layout properties.
- All springs use `--ease-spring-snappy` (`cubic-bezier(0.22,1,0.36,1)`) unless a bounce is explicitly required.
- Target `60fps`; cap simultaneous animated nodes at ~24; set `will-change: transform, opacity` only on the animated node.

### 7.2 Ambient Breathing Backdrop
- Two radial light leaks (bottom-left `#C4B39E`, top-right cream) drift on `14s ease-in-out infinite alternate`, `opacity 0.16 ↔ 0.24`, `scale 1 ↔ 1.06`.

### 7.3 Staggered Window Entrance
- On mount: window `opacity 0 → 1`, `translateY(14px) → 0`, `scale 0.985 → 1`, `520ms` spring, `delay 0`.
- Dock, header, hero, filter bar, and cards stagger in `40ms` increments after the window, each `280ms`, `translateY(10px) → 0` + fade.

### 7.4 Interactive Left Floating Dock
- Click: active circular indicator glides to the target icon (`transform: translateY(...)`, `280ms` spring), view content cross-fades (`opacity` + `translateX(6px)`).
- Icon press: `scale 0.9` → spring back.

### 7.5 Top Pill Navigation Header
- Cream pill glider is an absolutely positioned element that animates `left`/`width` to the active tab (`280ms` spring) instead of re-mounting.
- Title under it cross-fades with a vertical clip (`clip-path: inset(0 0 100% 0) → inset(0 0 0 0)`).

### 7.6 Hero Title + Segmented Ring + Numeric Roll-Up
- Title: 2-line stacked; on view change, old title clips up/fades, new title clips down/fades (`280ms`).
- Segmented ring: 8 segments, `stroke-dashoffset` animates on load and on metric change (`520ms`), center percentage counts up with `requestAnimationFrame` easing.
- KPI numerals roll up from `0` to value (`600ms`, ease-out) with tabular-nums; units stay fixed.

### 7.7 Filter Pill Bar
- Active pill slides (`transform`) between pills; pill background inverts to cream.
- Filtering: matching cards `scale 0.98 → 1` + fade; non-matching collapse with `grid-template-rows`/`opacity` transition (FLIP-style) rather than abrupt display toggle.

### 7.8 Bento Card Interactions
- Hover: border `--border-card-hover`, shadow `--shadow-card-hover`, `translateY(-2px)`, spotlight follows cursor.
- Press: `scale 0.985`.
- Enter on filter change: `stagger 30ms` by index, `translateY(8px) → 0` + fade.

### 7.9 Dark Glass ↔ Solid Cream Inversion
- Active controls invert material: background `rgba(255,255,255,0.06) → #F7F5EE`, text `#F7F5EE → #1E1C1A`, border to `--border-on-cream`; transition `280ms` snappy on `background-color`, `color`, `border-color`.
- The inversion must be driven by application state (same state as the real device setting), not hover-only.

### 7.10 Reduced Motion & Performance
- `@media (prefers-reduced-motion: reduce)`: disable ambient drift, roll-ups, and stagger; keep instant state changes.
- Pause heavy animation when the tab is hidden (`visibilitychange`); throttle pointer handlers with `requestAnimationFrame`.

---

## 8. Mockup Feature → Archetype / Interaction Mapping (all `[FILL]` resolved)

Every feature present in `html/mockup-panel-v3.html` is mapped below. No feature is dropped.

### 8.1 Global Chrome
| Elemen mockup | Archetype | Interaksi | Animasi | State / Handler |
|---|---|---|---|---|
| Tab utama Mouse / TWS | Top Pill Nav | klik tab, glider cream berpindah | 7.5 | `activeTab` |
| Dock kiri (nav ikon) | Dock | klik ikon, indikator meluncur | 7.4 | `activeView` |
| Hero title per tab | Hero | ganti teks per tab | 7.6 | `activeTab` |
| Segmented progress ring | Hero | animasi dashoffset + angka | 7.6 | `batteryAvg` |
| KPI strip (mouse %, kiri %, kanan %) | Hero | roll-up numeral | 7.6 | `mouse`, `left`, `right` |
| Filter pill bar | Filter | pilih filter, kartu menyusut/muncul | 7.7 | `filter` |
| View dots bawah | Pagination | klik dot, pill memanjang | 7.4 | `page` |

### 8.2 Mouse Tab
| Fitur mockup | Archetype | Widget | Interaksi | Animasi | Cmd / State |
|---|---|---|---|---|---|
| Baterai mouse (%, mV, charging) | A | ring + big numeral | hover spotlight | 7.6, 7.8 | `0xFF02` cmd `0x04` |
| DPI stage 1–4 | C | 4 kartu pilih | klik stage, aktif cream | 7.8, 7.9 | EEPROM `000C` |
| Polling rate | C | segmented 250/500/1000 | klik, write + readback | 7.9 | EEPROM `0000` pair |
| LOD | C | segmented 1 mm / 2 mm | klik | 7.9 | live `0070` sel `03` |
| Debounce | C | stepper/slider 1–20 ms | geser | 7.9 | live `0070` sel `02` |
| Motion sync | C | toggle | klik | 7.9 | `00A9` |
| Angle snapping | C | toggle | klik | 7.9 | `00BD` |
| Sleep timer | C | segmented 30–1800 dtk | klik | 7.9 | `00A9` |
| LED DPI | C | toggle + warna | klik | 7.9 | `002C`/`004C` |
| Remap tombol | D | tabel tombol | pilih aksi | 7.8 | EEPROM `0060–0074` |
| Makro / profil | D | list + slot | pilih slot | 7.8 | `0300` / COMPX |
| Spesifikasi | D | tabel statis | scroll | 7.3 | — |

### 8.3 TWS Tab
| Fitur mockup | Archetype | Widget | Interaksi | Animasi | Cmd / State |
|---|---|---|---|---|---|
| Baterai kiri/kanan/case | A | 3 bar + numeral | hover spotlight | 7.6, 7.8 | `0306/0307/0317` |
| Noise master (Normal/ANC/Ambient) | C | segmented | klik, write + readback | 7.9 | `0314`/`0315` |
| Sub-mode ANC (5 opsi) | C | chips | klik | 7.9 | `033A`/`033B` |
| Sub-mode Ambient (2 opsi) | C | chips | klik | 7.9 | `033C`/`033D` |
| Game mode | C | toggle | klik | 7.9 | `0312`/`0313` |
| In-ear detection | C | toggle | klik | 7.9 | `0349`/`034A` |
| Nyalakan / matikan gestur | C | 2 tombol + status | klik | 7.9 | `0334`/`0335` |
| Codec (5 opsi) | C | chips | klik (dengan konfirmasi reboot) | 7.9 | `032E`/`032F` |
| Multipoint | C | toggle | klik (konfirmasi) | 7.9 | `0327`/`0326` |
| Perangkat terpasang | D | list | klik connect/disconnect | 7.8 | `032C/0329/032A` |
| Mode mikrofon (auto/L/R) | C | segmented | klik | 7.9 | `0330`/`0331` |
| Volume prompt | C | slider 0–4 | geser | 7.9 | `0338`/`0339` |
| Cari earbud | C | tombol 0/1/2/3 | klik (peringatan) | 7.9 | `0332`/`0333` |
| Matriks gestur (16 pasang) | D | matriks 8×2 | pilih aksi per gestur | 7.8 | `030A`/`030B` |
| EQ 10 band | C | 10 slider + preset | geser, pilih preset | 7.9 | `0E01` (vendor `001D`) |
| Preset EQ (Netral/Bass/Vokal/Custom) | C | 4 tombol | klik | 7.9 | `0E01` |
| Auto power-off | D | baris status | — | — | `0348` (tidak tersedia) |

### 8.4 Persistence & Safety
- Every control writes the real device command only after its state flips; on failure the control reverts with a `shake` micro-animation (`translateX ±4px`, `160ms`) and a status badge change.
- Values that cannot be read back (EQ curve) are never auto-written; the UI shows them as client-side presets only.
- Destructive actions (factory reset, codec/multipoint) require an explicit confirmation step before any command is sent.