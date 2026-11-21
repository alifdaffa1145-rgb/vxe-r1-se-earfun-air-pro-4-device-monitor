import type { Tab } from '../state'

const DOTS: { id: Tab; label: string }[] = [
  { id: 'mouse', label: 'Mouse' },
  { id: 'tws', label: 'TWS' },
]

export default function ViewDots({ tab, onTab }: { tab: Tab; onTab: (t: Tab) => void }) {
  return (
    <div className="view-dots">
      {DOTS.map(d => (
        <button
          key={d.id}
          className={tab === d.id ? 'dot on' : 'dot'}
          onClick={() => onTab(d.id)}
          title={d.label}
          aria-label={d.label}
        />
      ))}
    </div>
  )
}
