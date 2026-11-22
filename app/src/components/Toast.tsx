import { useCallback, useState } from 'react'

export type ToastKind = 'pending' | 'success' | 'danger'
export type ToastItem = { id: number; text: string; kind: ToastKind }

const LIFETIME = 3200
let nextId = 0

/** Toast ringan: muncul, lalu hilang sendiri. Tidak perlu dependency baru. */
export function useToasts() {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const push = useCallback((text: string, kind: ToastKind = 'pending') => {
    const id = ++nextId
    setToasts(t => [...t.slice(-2), { id, text, kind }])
    window.setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), LIFETIME)
    return id
  }, [])

  const update = useCallback((id: number, text: string, kind: ToastKind) => {
    setToasts(t => t.map(x => (x.id === id ? { ...x, text, kind } : x)))
  }, [])

  return { toasts, push, update }
}

export default function ToastHost({ toasts }: { toasts: ToastItem[] }) {
  return (
    <div className="toast-container" role="status" aria-live="polite">
      {toasts.map(t => (
        <div key={t.id} className={`toast ${t.kind}`}>
          <span className="toast-mark" aria-hidden>
            {t.kind === 'success' ? '✓' : t.kind === 'danger' ? '!' : '↻'}
          </span>
          <span>{t.text}</span>
        </div>
      ))}
    </div>
  )
}
