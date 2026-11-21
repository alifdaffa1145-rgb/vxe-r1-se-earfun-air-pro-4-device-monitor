import { useReducer } from 'react'
import { initialState, reducer } from './state'
import Dock from './components/Dock'
import TopNav from './components/TopNav'
import Hero from './components/Hero'
import FilterBar from './components/FilterBar'
import Cards from './components/Cards'
import ViewDots from './components/ViewDots'

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState)

  const setTab = (tab: 'mouse' | 'tws') => dispatch({ type: 'SET_TAB', tab })

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
          <Cards state={state} dispatch={dispatch} />
        </main>
      </div>
      <ViewDots tab={state.tab} onTab={setTab} />
    </div>
  )
}
