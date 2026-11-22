import { useEffect, useState, type ReactNode } from 'react'
import type { Action, AppState, Filter, MouseState, TwsState } from '../state'
import {
  ANC_SUBS,
  AMB_SUBS,
  CODECS,
  EQ_FREQS,
  EQ_PRESETS,
  GESTURE_ACTIONS,
  GESTURES,
} from '../state'
import { useSpotlight, useCountUp } from '../hooks'
import Icon, { type IconName } from './Icon'

type Dispatch = (a: Action) => void

/* ---------- kontrol kecil ---------- */

function Segmented<T extends string | number>({
  options,
  value,
  onChange,
}: {
  options: { value: T; label: string }[]
  value: T
  onChange: (v: T) => void
}) {
  return (
    <div className="seg">
      {options.map(o => (
        <button
          key={String(o.value)}
          className={o.value === value ? 'seg-btn on' : 'seg-btn'}
          onClick={() => onChange(o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}

function Chips<T extends string | number>({
  options,
  value,
  onChange,
  disabled = false,
}: {
  options: { value: T; label: string }[]
  value: T
  onChange: (v: T) => void
  disabled?: boolean
}) {
  return (
    <div className="chips">
      {options.map(o => (
        <button
          key={String(o.value)}
          className={o.value === value ? 'chip on' : 'chip'}
          disabled={disabled}
          onClick={() => onChange(o.value)}
        >
          {o.label}
        </button>
      ))}
    </div>
  )
}

function Toggle({
  checked,
  onChange,
  label,
  disabled = false,
}: {
  checked: boolean
  onChange: (v: boolean) => void
  label: string
  disabled?: boolean
}) {
  return (
    <button className={checked ? 'tog on' : 'tog'} disabled={disabled} onClick={() => onChange(!checked)}>
      <span className="sw" />
      <span>{label}</span>
    </button>
  )
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="field">
      <span className="micro-label">{label}</span>
      {children}
    </div>
  )
}

/* ---------- shell kartu ---------- */

function Card({
  arche,
  cat,
  title,
  icon,
  children,
  delay = 0,
}: {
  arche: 'A' | 'B' | 'C' | 'D'
  cat: Filter
  title: string
  icon: IconName
  children: ReactNode
  delay?: number
}) {
  const ref = useSpotlight<HTMLDivElement>()
  return (
    <div
      ref={ref}
      className={`bento arche-${arche}`}
      data-cat={cat}
      style={delay ? { animationDelay: `${delay}ms` } : undefined}
    >
      <div className="card-head">
        <span className="card-icon" aria-hidden>
          <Icon name={icon} />
        </span>
        <h3>{title}</h3>
      </div>
      {children}
    </div>
  )
}

/* ---------- Mouse ---------- */

function MouseBattery({ mouse }: { mouse: MouseState }) {
  const shown = useCountUp(mouse.battery, 700)
  return (
    <Card arche="A" cat="baterai" title="Baterai Mouse" icon="battery">
      <div className="big-metric">
        <span className="big-num">{shown}</span>
        <sup>%</sup>
        <span className={mouse.charging ? 'badge on' : 'badge'}>
          {mouse.charging ? 'Mengisi daya' : 'Tidak mengisi'}
        </span>
      </div>
      <div className="bar">
        <span style={{ width: `${mouse.battery}%` }} />
      </div>
      <div className="meta-row">
        <span>{mouse.mv} mV</span>
        <span>HID 0xFF02</span>
        <span>checksum 0x55</span>
      </div>
    </Card>
  )
}

function MousePerf({ mouse, dispatch }: { mouse: MouseState; dispatch: Dispatch }) {
  return (
    <Card arche="C" cat="performa" title="Performa & Sensor" icon="sensor">
      <Field label="DPI stage">
        <div className="dpi-grid">
          {mouse.dpiStages.map((dpi, i) => (
            <div className="dpi-cell" key={i}>
              <button
                className={i === mouse.activeStage ? 'dpi on' : 'dpi'}
                onClick={() => dispatch({ type: 'MOUSE', patch: { activeStage: i } })}
              >
                <strong>{dpi}</strong>
                <small>Stage {i + 1}</small>
              </button>
              <input
                type="number"
                className="dpi-input"
                min={100}
                max={18000}
                step={50}
                value={dpi}
                onChange={e =>
                  dispatch({ type: 'DPI_STAGE', index: i, dpi: Number(e.target.value) })
                }
              />
            </div>
          ))}
        </div>
      </Field>
      <Field label="Polling rate">
        <Segmented
          options={[
            { value: 250, label: '250' },
            { value: 500, label: '500' },
            { value: 1000, label: '1000' },
          ]}
          value={mouse.polling}
          onChange={v => dispatch({ type: 'MOUSE', patch: { polling: v } })}
        />
      </Field>
      <Field label="Lift-off distance">
        <Segmented
          options={[
            { value: 1, label: '1 mm' },
            { value: 2, label: '2 mm' },
          ]}
          value={mouse.lod}
          onChange={v => dispatch({ type: 'MOUSE', patch: { lod: v } })}
        />
      </Field>
      <Field label={`Debounce · ${mouse.debounce} ms`}>
        <input
          type="range"
          min={1}
          max={20}
          value={mouse.debounce}
          onChange={e => dispatch({ type: 'MOUSE', patch: { debounce: Number(e.target.value) } })}
        />
      </Field>
      <div className="tog-row">
        <Toggle
          label="Motion sync"
          checked={mouse.motionSync}
          onChange={v => dispatch({ type: 'MOUSE', patch: { motionSync: v } })}
        />
        <Toggle
          label="Angle snapping"
          checked={mouse.angleSnap}
          onChange={v => dispatch({ type: 'MOUSE', patch: { angleSnap: v } })}
        />
        <Toggle
          label="LED DPI"
          checked={mouse.led}
          onChange={v => dispatch({ type: 'MOUSE', patch: { led: v } })}
        />
      </div>
      <Field label="Sleep timer">
        <Segmented
          options={[
            { value: 30, label: '30 dtk' },
            { value: 60, label: '60 dtk' },
            { value: 300, label: '5 mnt' },
            { value: 1800, label: '30 mnt' },
          ]}
          value={mouse.sleep}
          onChange={v => dispatch({ type: 'MOUSE', patch: { sleep: v } })}
        />
      </Field>
    </Card>
  )
}

function MouseData() {
  const rows = [
    ['Sensor', 'PixArt PAW3395 SE'],
    ['DPI', 'klaim 10–18000 · grid 200–18000'],
    ['Kecepatan', '400 IPS / 40 G'],
    ['Switch', 'Huano Blue Glow V2'],
    ['Berat', 'klaim 55 g · timbangan 58,1 g'],
    ['Baterai', '520 mAh · klaim 70–75 jam'],
    ['Konektivitas', '2.4G / BT 5.4 / USB-C'],
  ]
  return (
    <Card arche="D" cat="performa" title="Spesifikasi & Profil" icon="data">
      <table className="data-table">
        <tbody>
          {rows.map(([k, v]) => (
            <tr key={k}>
              <td>{k}</td>
              <td>{v}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="meta-row">
        <span>Profil onboard: 4 bank</span>
        <span>Makro: 12 slot</span>
      </div>
    </Card>
  )
}

/* ---------- TWS ---------- */

function TwsBattery({ tws }: { tws: TwsState }) {
  const shownL = useCountUp(tws.left ?? 0, 700)
  const shownR = useCountUp(tws.right ?? 0, 700)
  const rows: { label: string; value: number | null }[] = [
    { label: 'Kiri', value: tws.left },
    { label: 'Kanan', value: tws.right },
    { label: 'Case', value: tws.caseBat },
  ]
  return (
    <Card arche="A" cat="baterai" title="Baterai EarFun" icon="battery">
      <div className="big-metric">
        <span className="big-num">{shownL}</span>
        <sup>%</sup>
        <span className="badge">kiri</span>
        <span className="big-num alt">{shownR}</span>
        <sup>%</sup>
        <span className="badge">kanan</span>
      </div>
      {rows.map(r => (
        <div className="bar-row" key={r.label}>
          <span className="bar-label">{r.label}</span>
          <div className="bar">
            <span style={{ width: `${r.value ?? 0}%` }} />
          </div>
          <span className="bar-val">{r.value === null ? '—' : `${r.value}%`}</span>
        </div>
      ))}
      <div className="meta-row">
        <span>Firmware TW600 v0.4.1</span>
        <span>GAIA / SPP</span>
      </div>
    </Card>
  )
}

function TwsAudio({ tws, dispatch }: { tws: TwsState; dispatch: Dispatch }) {
  return (
    <Card arche="C" cat="audio" title="Mode & Suara" icon="sliders">
      <Field label="Noise control">
        <Segmented
          options={[
            { value: 0, label: 'Normal' },
            { value: 1, label: 'ANC' },
            { value: 2, label: 'Ambient' },
          ]}
          value={tws.noiseMode}
          onChange={v => dispatch({ type: 'TWS', patch: { noiseMode: v } })}
        />
      </Field>
      <Field label="Sub-mode ANC">
        <Chips
          options={ANC_SUBS.map((label, i) => ({ value: i, label }))}
          value={tws.ancSub}
          onChange={v => dispatch({ type: 'TWS', patch: { ancSub: v } })}
        />
      </Field>
      <Field label="Sub-mode Ambient">
        <Chips
          options={AMB_SUBS.map((label, i) => ({ value: i, label }))}
          value={tws.ambSub}
          onChange={v => dispatch({ type: 'TWS', patch: { ambSub: v } })}
        />
      </Field>
      <Field label="Gestur sentuh">
        <Segmented
          options={[
            { value: 0, label: 'Nyalakan gestur' },
            { value: 1, label: 'Matikan gestur' },
          ]}
          value={tws.gestureLock ? 1 : 0}
          onChange={v => dispatch({ type: 'TWS', patch: { gestureLock: v === 1 } })}
        />
        <small className="hint">
          {tws.gestureLock ? 'Mati / terkunci (0335 = 1)' : 'Aktif (0335 = 0)'}
        </small>
      </Field>
      <div className="tog-row">
        <Toggle
          label="Game mode"
          checked={tws.game}
          onChange={v => dispatch({ type: 'TWS', patch: { game: v } })}
        />
        <Toggle
          label="In-ear detection"
          checked={tws.inEar}
          onChange={v => dispatch({ type: 'TWS', patch: { inEar: v } })}
        />
      </div>
      <Field label="Mode mikrofon">
        <Segmented
          options={[
            { value: 0, label: 'Auto' },
            { value: 1, label: 'Kiri' },
            { value: 2, label: 'Kanan' },
          ]}
          value={tws.mic}
          onChange={v => dispatch({ type: 'TWS', patch: { mic: v } })}
        />
      </Field>
      <Field label={`Volume prompt · ${tws.prompt}`}>
        <input
          type="range"
          min={0}
          max={4}
          value={tws.prompt}
          onChange={e => dispatch({ type: 'TWS', patch: { prompt: Number(e.target.value) } })}
        />
      </Field>
      <Field label="Cari earbud">
        <Segmented
          options={[
            { value: 0, label: 'Mati' },
            { value: 1, label: 'Kiri' },
            { value: 2, label: 'Kanan' },
            { value: 3, label: 'Keduanya' },
          ]}
          value={tws.findDevice}
          onChange={v => dispatch({ type: 'TWS', patch: { findDevice: v } })}
        />
        <small className="hint">Memainkan suara keras</small>
      </Field>
    </Card>
  )
}

function TwsConnect({
  tws,
  dispatch,
  pending,
}: {
  tws: TwsState
  dispatch: Dispatch
  pending: boolean
}) {
  const [confirmTarget, setConfirmTarget] = useState<number | null>(null)

  useEffect(() => {
    if (confirmTarget === null) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setConfirmTarget(null)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [confirmTarget])

  const targetLabel =
    confirmTarget === null
      ? ''
      : CODECS.find(c => c.value === confirmTarget)?.label ?? String(confirmTarget)

  return (
    <>
      <Card arche="C" cat="koneksi" title="Konektivitas" icon="link">
        <Field label="Codec audio">
          <Chips
            options={CODECS.map(c => ({ value: c.value, label: c.label }))}
            value={tws.codec}
            disabled={pending}
            onChange={v => {
              if (v !== tws.codec) setConfirmTarget(v)
            }}
          />
          <small className="hint">
            LDAC tidak bisa dipakai bersama multipoint. Perubahan memicu restart ±20 detik.
          </small>
          {pending && <span className="card-state">Menerapkan ke earbud…</span>}
        </Field>
        <div className="tog-row">
          <Toggle label="Multipoint" checked={tws.multipoint} onChange={() => {}} disabled />
          <small className="hint">Belum bisa diubah dari PC.</small>
        </div>
        <Field label="Perangkat terpasang">
          <div className="host-list">
            <span>PC ini · terhubung</span>
            <span>Telepon · tersimpan</span>
          </div>
        </Field>
      </Card>

      {confirmTarget !== null && (
        <div className="modal-backdrop" onClick={() => setConfirmTarget(null)}>
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="codec-dialog-title"
            onClick={e => e.stopPropagation()}
          >
            <span className="modal-eyebrow">Perubahan perangkat</span>
            <h2 id="codec-dialog-title">Ganti codec ke {targetLabel}?</h2>
            <p>
              Earbud akan restart sekitar 20 detik dan koneksi SPP putus sementara.
              Pengaturan lain tetap tersimpan.
            </p>
            <div className="modal-actions">
              <button className="btn ghost" onClick={() => setConfirmTarget(null)}>
                Batal
              </button>
              <button
                className="btn primary"
                onClick={() => {
                  dispatch({ type: 'TWS', patch: { codec: confirmTarget } })
                  setConfirmTarget(null)
                }}
              >
                Ganti codec
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

function TwsGesture({ tws, dispatch }: { tws: TwsState; dispatch: Dispatch }) {
  return (
    <Card arche="D" cat="audio" title="Matriks Gestur" icon="gesture">
      <div className="gesture-grid">
        {GESTURES.map((g, i) => (
          <div className="gesture-cell" key={`${g.type}-${g.side}`}>
            <span className="micro-label">
              {g.label} {g.side}
            </span>
            <div className="chips wrap">
              {GESTURE_ACTIONS.map(a => (
                <button
                  key={a.value}
                  className={tws.gestures[i] === a.value ? 'chip on' : 'chip'}
                  onClick={() =>
                    dispatch({
                      type: 'GESTURE',
                      actions: tws.gestures.map((v, idx) => (idx === i ? a.value : v)),
                    })
                  }
                >
                  {a.label}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      <small className="hint">030B = 33 byte · 16 pasangan [jenis, aksi] · ditulis via 030A</small>
    </Card>
  )
}

function TwsEq({ tws, dispatch }: { tws: TwsState; dispatch: Dispatch }) {
  return (
    <Card arche="C" cat="audio" title="Equalizer 10 Band" icon="equalizer">
      <div className="eq-presets">
        {Object.keys(EQ_PRESETS).map(name => (
          <button
            key={name}
            className={tws.eqPreset === name ? 'chip on' : 'chip'}
            onClick={() => dispatch({ type: 'TWS', patch: { eq: EQ_PRESETS[name], eqPreset: name } })}
          >
            {name}
          </button>
        ))}
      </div>
      <div className="eq-banks">
        {tws.eq.map((v, i) => (
          <div className="eq-band" key={i}>
            <span className="micro-label">{EQ_FREQS[i]}</span>
            <input
              type="range"
              min={-10}
              max={10}
              value={v}
              onChange={e => dispatch({ type: 'EQ', index: i, value: Number(e.target.value) })}
            />
            <span className="eq-val">{v > 0 ? `+${v}` : v}</span>
          </div>
        ))}
      </div>
      <small className="hint">Write-only 0E01 · tidak bisa di-readback</small>
    </Card>
  )
}

/* ---------- susunan ---------- */

export default function Cards({
  state,
  dispatch,
  pending,
}: {
  state: AppState
  dispatch: Dispatch
  pending: Record<string, boolean>
}) {
  const { tab, filter, mouse, tws } = state
  const visible = (cat: Filter) => filter === 'semua' || filter === cat

  const mouseCards = (
    <>
      {visible('baterai') && <MouseBattery mouse={mouse} />}
      {visible('performa') && <MousePerf mouse={mouse} dispatch={dispatch} />}
      {visible('performa') && <MouseData />}
    </>
  )

  const twsCards = (
    <>
      {visible('baterai') && <TwsBattery tws={tws} />}
      {visible('audio') && <TwsAudio tws={tws} dispatch={dispatch} />}
      {visible('audio') && <TwsEq tws={tws} dispatch={dispatch} />}
      {visible('audio') && <TwsGesture tws={tws} dispatch={dispatch} />}
      {visible('koneksi') && (
        <TwsConnect tws={tws} dispatch={dispatch} pending={!!pending['tws.codec']} />
      )}
    </>
  )

  return <div className="bento-grid" key={tab}>{tab === 'mouse' ? mouseCards : twsCards}</div>
}
