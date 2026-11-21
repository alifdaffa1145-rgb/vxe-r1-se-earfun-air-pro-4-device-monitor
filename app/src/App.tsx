import { useEffect, useReducer, useRef, useState } from 'react'
import { initialState, reducer, type Action, type MouseState, type TwsState } from './state'
import { getStatus, setDevice } from './api'
import Dock from './components/Dock'
import TopNav from './components/TopNav'
import Hero from './components/Hero'
import FilterBar from './components/FilterBar'
import Cards from './components/Cards'
import ViewDots from './components/ViewDots'

const MOUSE_WRITABLE = ['polling', 'lod', 'debounce']
const TWS_WRITABLE = [
  'noiseMode',
  'ancSub',
  'ambSub',
  'game',
  'inEar',
  'gestureLock',
  'mic',
  'prompt',
]

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState)
  const [errors, setErrors] = useState<{ mouse: string | null; tws: string | null }>({
    mouse: null,
    tws: null,
  })
  const timers = useRef<Record<string, number>>({})

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const s = await getStatus()
        if (!alive) return
        setErrors(s.errors)
        if (s.mouse && Object.keys(s.mouse).length) {
          dispatch({ type: 'MOUSE', patch: s.mouse as Partial<MouseState> })
        }
        if (s.tws && Object.keys(s.tws).length) {
          dispatch({ type: 'TWS', patch: s.tws as Partial<TwsState> })
        }
      } catch {
        if (alive) setErrors({ mouse: 'bridge offline', tws: 'bridge offline' })
      }
    }
    void load()
    const id = window.setInterval(load, 5000)
    return () => {
      alive = false
      window.clearInterval(id)
      Object.values(timers.current).forEach(t => window.clearTimeout(t))
    }
  }, [])

  const send = (device: 'mouse' | 'tws', key: string, value: unknown) => {
    const id = `${device}.${key}`
    window.clearTimeout(timers.current[id])
    timers.current[id] = window.setTimeout(() => {
      void setDevice(device, key, value).catch(() =>
        setErrors(e => ({ ...e, [device]: 'write gagal' })),
      )
    }, 220)
  }

  const bridgeDispatch = (action: Action) => {
    dispatch(action)
    if (action.type === 'MOUSE') {
      Object.entries(action.patch).forEach(([k, v]) => {
        if (MOUSE_WRITABLE.includes(k)) send('mouse', k, v)
      })
    } else if (action.type === 'TWS') {
      Object.entries(action.patch).forEach(([k, v]) => {
        if (TWS_WRITABLE.includes(k)) send('tws', k, v)
      })
    } else if (action.type === 'EQ') {
      const eq = state.tws.eq.slice()
      eq[action.index] = action.value
      send('tws', 'eq', eq)
    }
  }

  const setTab = (tab: 'mouse' | 'tws') => dispatch({ type: 'SET_TAB', tab })
  const problem = errors.mouse || errors.tws

  return (
    <div className="ambient">
      <span className="glow glow-bl" />
      <span className="glow glow-tr" />
      <div className="shell">
        <Dock tab={state.tab} onTab={setTab} />
        <main className="window">
          <TopNav tab={state.tab} onTab={setTab} />
          <Hero tab={state.tab} mouse={state.mouse} tws={state.tws} />
          <FilterBar
            filter={state.filter}
            onFilter={f => dispatch({ type: 'SET_FILTER', filter: f })}
          />
          <Cards state={state} dispatch={bridgeDispatch} />
          {problem && (
            <p className="bridge-status">
              {errors.mouse && `Mouse: ${errors.mouse}. `}
              {errors.tws && `TWS: ${errors.tws}.`}
            </p>
          )}
        </main>
      </div>
      <ViewDots tab={state.tab} onTab={setTab} />
    </div>
  )
}
