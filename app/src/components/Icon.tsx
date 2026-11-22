import type { ReactNode } from 'react'

export type IconName =
  | 'battery'
  | 'sensor'
  | 'data'
  | 'signal'
  | 'sliders'
  | 'link'
  | 'gesture'
  | 'equalizer'

const PATHS: Record<IconName, ReactNode> = {
  battery: (
    <>
      <rect x="3" y="7" width="16" height="10" rx="2" />
      <path d="M21 10v4" />
      <path d="M6.5 12h5" />
    </>
  ),
  sensor: (
    <>
      <circle cx="12" cy="12" r="5.5" />
      <circle cx="12" cy="12" r="1.6" />
      <path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3" />
    </>
  ),
  data: (
    <>
      <path d="M5 4h14v16H5z" />
      <path d="M8 9h8M8 13h8M8 17h5" />
    </>
  ),
  signal: (
    <>
      <path d="M4 17a8 8 0 0 1 16 0" />
      <path d="M7 17a5 5 0 0 1 10 0" />
      <circle cx="12" cy="17" r="1.2" />
    </>
  ),
  sliders: (
    <>
      <path d="M4 7h16M4 12h16M4 17h16" />
      <circle cx="9" cy="7" r="2" />
      <circle cx="15" cy="12" r="2" />
      <circle cx="8" cy="17" r="2" />
    </>
  ),
  link: (
    <>
      <path d="M10 13a4 4 0 0 0 5.7 0l2.6-2.6a4 4 0 0 0-5.7-5.7L11 6.3" />
      <path d="M14 11a4 4 0 0 0-5.7 0l-2.6 2.6a4 4 0 1 0 5.7 5.7l1.6-1.6" />
    </>
  ),
  gesture: (
    <>
      <path d="M9 11V5.5a1.5 1.5 0 0 1 3 0V11" />
      <path d="M12 11V7.5a1.5 1.5 0 0 1 3 0V12" />
      <path d="M15 12v-2a1.5 1.5 0 0 1 3 0v6a6 6 0 0 1-6 6h-1a6 6 0 0 1-5-2.7l-2.3-3.4a1.6 1.6 0 0 1 2.5-2L9 15" />
    </>
  ),
  equalizer: (
    <>
      <path d="M5 20V11M10 20V5M15 20v-7M20 20V8" />
    </>
  ),
}

export default function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {PATHS[name]}
    </svg>
  )
}
