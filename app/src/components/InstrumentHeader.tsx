import type { Filter, MouseState, Tab, TwsState } from '../state'
import { useCountUp } from '../hooks'
import Ring from './Ring'

interface InstrumentHeaderProps {
  tab: Tab
  mouse: MouseState
  tws: TwsState
  connected: { mouse: boolean; tws: boolean }
  filter: Filter
  onFilter: (f: Filter) => void
}

const DEVICE_TITLES: Record<Tab, { name: string; sub: string }> = {
  mouse: { name: 'VXE R1 SE+', sub: 'Mouse Gaming Tri-Mode' },
  tws: { name: 'EarFun Air Pro 4', sub: 'TWS ANC · TW600' },
}

const FILTERS: { id: Filter; label: string }[] = [
  { id: 'semua', label: 'Semua' },
  { id: 'baterai', label: 'Baterai' },
  { id: 'performa', label: 'Performa' },
  { id: 'audio', label: 'Audio' },
  { id: 'koneksi', label: 'Koneksi' },
]

export default function InstrumentHeader({
  tab,
  mouse,
  tws,
  connected,
  filter,
  onFilter,
}: InstrumentHeaderProps) {
  const dev = DEVICE_TITLES[tab]
  const online = connected.mouse || connected.tws
  const avgBattery =
    tab === 'mouse'
      ? mouse.battery
      : Math.round((((tws.left ?? 0) + (tws.right ?? 0)) / 2) || 0)

  const shownBattery = useCountUp(avgBattery, 700)

  return (
    <div className="instrument-header">
      <div className="device-header">
        <div className="device-identity">
          <div className="device-icon" aria-hidden>
            <span className="mono">{tab === 'mouse' ? 'M' : 'E'}</span>
          </div>
          <div className="device-info">
            <h2>{dev.name}</h2>
            <p>{dev.sub}</p>
          </div>
        </div>
        <div className="connection-status">
          <span className={`status-indicator ${online ? 'online' : 'offline'}`} />
          <span className={`status-text ${online ? 'online' : 'offline'}`}>
            {online ? 'Terhubung' : 'Terputus'}
          </span>
        </div>
      </div>

      <div className="status-summary">
        <Ring value={avgBattery} label="Baterai" />
        <div className="stat">
          <span className="stat-label">Baterai</span>
          <span className={`stat-value ${tab === 'mouse' ? 'accent' : 'success'}`}>
            {shownBattery}%
          </span>
        </div>
        {tab === 'mouse' && (
          <div className="stat">
            <span className="stat-label">Polling</span>
            <span className="stat-value accent">{mouse.polling} Hz</span>
          </div>
        )}
        {tab === 'tws' && (
          <>
            <div className="stat">
              <span className="stat-label">Kiri</span>
              <span className="stat-value success">{tws.left ?? 0}%</span>
            </div>
            <div className="stat">
              <span className="stat-label">Kanan</span>
              <span className="stat-value success">{tws.right ?? 0}%</span>
            </div>
          </>
        )}
      </div>

      <div className="filter-bar">
        <div className="filter-pills">
          {FILTERS.map(f => (
            <button
              key={f.id}
              className={filter === f.id ? 'filter-pill on' : 'filter-pill'}
              onClick={() => onFilter(f.id)}
            >
              {f.label}
            </button>
          ))}
        </div>
        <div className="filter-actions">
          <button className="action-btn" title="Muat ulang" aria-label="Muat ulang">
            ↻
          </button>
        </div>
      </div>
    </div>
  )
}
