export interface BridgeStatus {
  mouse: Record<string, unknown>
  tws: Record<string, unknown>
  errors: { mouse: string | null; tws: string | null }
  connected: { mouse: boolean; tws: boolean }
}

const BASE =
  typeof localStorage !== 'undefined'
    ? localStorage.getItem('device-bridge-url') || 'http://127.0.0.1:8765'
    : 'http://127.0.0.1:8765'

export async function getStatus(): Promise<BridgeStatus> {
  const res = await fetch(`${BASE}/api/status`, { cache: 'no-store' })
  if (!res.ok) throw new Error(`bridge ${res.status}`)
  return (await res.json()) as BridgeStatus
}

export async function setDevice(
  device: 'mouse' | 'tws',
  key: string,
  value: unknown,
): Promise<unknown> {
  const res = await fetch(`${BASE}/api/${device}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key, value }),
  })
  const body = (await res.json()) as { ok?: boolean; readback?: unknown; error?: string }
  if (!res.ok || body.error) throw new Error(body.error || `bridge ${res.status}`)
  return body.readback
}
