import { useEffect, useRef, useState } from 'react'
import type { Tab } from '../state'

const TABS: { id: Tab; label: string }[] = [
  { id: 'mouse', label: 'Mouse' },
  { id: 'tws', label: 'TWS' },
]

export default function TopNav({ tab, onTab }: { tab: Tab; onTab: (t: Tab) => void }) {
  const refs = useRef<Array<HTMLButtonElement | null>>([])
  const [glide, setGlide] = useState({ left: 0, width: 0 })

  useEffect(() => {
    const i = TABS.findIndex(t => t.id === tab)
    const el = refs.current[i]
    if (!el) return
    setGlide({ left: el.offsetLeft, width: el.offsetWidth })
  }, [tab])

  return (
    <header className="topnav">
      <span className="brand" aria-hidden>
        DM
      </span>
      <div className="topnav-pills">
        <span className="pill-glider" style={{ left: glide.left, width: glide.width }} />
        {TABS.map((t, i) => (
          <button
            key={t.id}
            ref={el => {
              refs.current[i] = el
            }}
            className={tab === t.id ? 'pill on' : 'pill'}
            onClick={() => onTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="status-capsule">
        <span className="avatar">DF</span>
        <span className="status-text">
          <strong>Terhubung</strong>
          <small>2 perangkat</small>
        </span>
        <button className="status-btn" title="Setelan" aria-label="Setelan">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="3" />
            <path d="M12 3v3M12 18v3M3 12h3M18 12h3" />
          </svg>
        </button>
      </div>
    </header>
  )
}
