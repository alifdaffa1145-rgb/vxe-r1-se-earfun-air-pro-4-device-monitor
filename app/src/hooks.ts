import { useEffect, useRef, useState } from 'react'

/** Animasi angka roll-up (ease-out cubic) dengan tabular-nums. */
export function useCountUp(target: number, duration = 600): number {
  const [value, setValue] = useState(0)
  const fromRef = useRef(0)

  useEffect(() => {
    const from = fromRef.current
    if (from === target) {
      setValue(target)
      return
    }
    let timer = 0
    const start = performance.now()
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration)
      const eased = 1 - Math.pow(1 - t, 3)
      setValue(Math.round(from + (target - from) * eased))
      if (t < 1) {
        timer = window.setTimeout(() => tick(performance.now()), 16)
      } else {
        fromRef.current = target
      }
    }
    timer = window.setTimeout(() => tick(performance.now()), 16)
    return () => {
      window.clearTimeout(timer)
      fromRef.current = target
    }
  }, [target, duration])

  return value
}

/** Ikuti pointer untuk cursor spotlight kartu. */
export function useSpotlight<T extends HTMLElement>() {
  const ref = useRef<T | null>(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    let raf = 0
    const onMove = (e: PointerEvent) => {
      const rect = el.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => {
        el.style.setProperty('--mx', `${x}px`)
        el.style.setProperty('--my', `${y}px`)
      })
    }
    el.addEventListener('pointermove', onMove)
    return () => {
      el.removeEventListener('pointermove', onMove)
      cancelAnimationFrame(raf)
    }
  }, [])
  return ref
}
