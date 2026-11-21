import type { Tab } from '../state'

function MouseIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <rect x="7" y="3" width="10" height="18" rx="5" />
      <path d="M12 7v3" />
    </svg>
  )
}

function BudsIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
      <path d="M7 4a3 3 0 0 1 3 3v4a2 2 0 0 1-4 0V7a3 3 0 0 1 1-3Z" />
      <path d="M17 4a3 3 0 0 0-3 3v4a2 2 0 0 0 4 0V7a3 3 0 0 0-1-3Z" />
      <path d="M7 16v2M17 16v2" />
    </svg>
  )
}

const ITEMS: { id: Tab; label: string; icon: JSX.Element }[] = [
  { id: 'mouse', label: 'Mouse', icon: <MouseIcon /> },
  { id: 'tws', label: 'TWS', icon: <BudsIcon /> },
]

export default function Dock({ tab, onTab }: { tab: Tab; onTab: (t: Tab) => void }) {
  return (
    <nav className="dock" aria-label="Navigasi utama">
      <span
        className="dock-glider"
        style={{ transform: `translateY(calc(8px + ${ITEMS.findIndex(i => i.id === tab)} * 44px))` }}
      />
      {ITEMS.map(item => (
        <button
          key={item.id}
          className={tab === item.id ? 'dock-btn on' : 'dock-btn'}
          onClick={() => onTab(item.id)}
          title={item.label}
          aria-label={item.label}
          aria-pressed={tab === item.id}
        >
          {item.icon}
        </button>
      ))}
    </nav>
  )
}
