import type { Tab, MouseState, TwsState } from '../state'
import { useCountUp } from '../hooks'
import Ring from './Ring'

function Kpi({ label, value, unit }: { label: string; value: number; unit: string }) {
  const v = useCountUp(value, 600)
  return (
    <div className="kpi">
      <span className="kpi-label">{label}</span>
      <span className="kpi-value">
        {v}
        <sup>{unit}</sup>
      </span>
    </div>
  )
}

const TITLES: Record<Tab, string[]> = {
  mouse: ['VXE R1 SE+', 'Mouse Gaming Tri-Mode'],
  tws: ['EarFun Air Pro 4', 'TWS ANC · TW600'],
}

export default function Hero({ tab, mouse, tws }: { tab: Tab; mouse: MouseState; tws: TwsState }) {
  const avg =
    tab === 'mouse'
      ? mouse.battery
      : Math.round((((tws.left ?? 0) + (tws.right ?? 0)) / 2) || 0)

  return (
    <section className="hero">
      <div className="hero-title" key={tab}>
        {TITLES[tab].map(line => (
          <h1 key={line}>{line}</h1>
        ))}
      </div>
      <Ring value={avg} label="Rata-rata baterai" />
      <div className="hero-kpis">
        <Kpi label="Baterai mouse" value={mouse.battery} unit="%" />
        <Kpi label="Kiri" value={tws.left ?? 0} unit="%" />
        <Kpi label="Kanan" value={tws.right ?? 0} unit="%" />
        <Kpi label="Polling" value={mouse.polling} unit="Hz" />
      </div>
    </section>
  )
}
