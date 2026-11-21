import { useCountUp } from '../hooks'

const SEGMENTS = 8

export default function Ring({ value, label }: { value: number; label: string }) {
  const shown = useCountUp(value, 520)
  const size = 84
  const stroke = 8
  const r = (size - stroke) / 2 - 2
  const c = 2 * Math.PI * r
  const seg = c / SEGMENTS
  const active = Math.round((shown / 100) * SEGMENTS)

  return (
    <div className="ring">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden>
        {Array.from({ length: SEGMENTS }).map((_, i) => (
          <circle
            key={i}
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            strokeWidth={stroke}
            strokeLinecap="round"
            className={i < active ? 'ring-seg on' : 'ring-seg'}
            strokeDasharray={`${Math.max(0, seg - 4)} ${c - seg + 4}`}
            transform={`rotate(${i * (360 / SEGMENTS) - 90} ${size / 2} ${size / 2})`}
          />
        ))}
      </svg>
      <div className="ring-center">
        <span className="ring-value">{shown}</span>
        <span className="ring-unit">%</span>
      </div>
      <span className="ring-label">{label}</span>
    </div>
  )
}
