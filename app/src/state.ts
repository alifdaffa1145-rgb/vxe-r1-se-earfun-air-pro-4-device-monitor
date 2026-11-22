export type Tab = 'mouse' | 'tws'
export type Filter = 'semua' | 'baterai' | 'performa' | 'audio' | 'koneksi'

export interface MouseState {
  battery: number
  mv: number
  charging: boolean
  dpiStages: number[]
  activeStage: number
  polling: number
  lod: number
  debounce: number
  motionSync: boolean
  angleSnap: boolean
  sleep: number
  led: boolean
  profile: number
}

export interface TwsState {
  left: number | null
  right: number | null
  caseBat: number | null
  noiseMode: number
  ancSub: number
  ambSub: number
  game: boolean
  inEar: boolean
  gestureLock: boolean
  codec: number
  multipoint: boolean
  mic: number
  prompt: number
  eq: number[]
  eqPreset: string
  gestures: number[]
  findDevice: number
}

export interface ConnectedState {
  mouse: boolean
  tws: boolean
}

export interface AppState {
  tab: Tab
  filter: Filter
  mouse: MouseState
  tws: TwsState
  connected: ConnectedState
}

export type Action =
  | { type: 'SET_TAB'; tab: Tab }
  | { type: 'SET_FILTER'; filter: Filter }
  | { type: 'MOUSE'; patch: Partial<MouseState> }
  | { type: 'TWS'; patch: Partial<TwsState> }
  | { type: 'EQ'; index: number; value: number }
  | { type: 'GESTURE'; actions: number[] }
  | { type: 'SET_CONNECTED'; connected: ConnectedState }

// Nilai awal diambil dari hasil probe nyata PC (2026-11-21).
export const initialState: AppState = {
  tab: 'mouse',
  filter: 'semua',
  mouse: {
    battery: 100,
    mv: 4272,
    charging: false,
    dpiStages: [400, 800, 1600, 3200],
    activeStage: 1,
    polling: 1000,
    lod: 1,
    debounce: 8,
    motionSync: true,
    angleSnap: false,
    sleep: 60,
    led: false,
    profile: 0,
  },
  tws: {
    left: 20,
    right: 30,
    caseBat: null,
    noiseMode: 1,
    ancSub: 3,
    ambSub: 1,
    game: false,
    inEar: false,
    gestureLock: true,
    codec: 19,
    multipoint: false,
    mic: 0,
    prompt: 0,
    eq: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    eqPreset: 'netral',
    gestures: [3, 2, 1, 1, 4, 5, 8, 8],
    findDevice: 0,
  },
  connected: { mouse: false, tws: false },
}

export function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_TAB':
      return { ...state, tab: action.tab, filter: 'semua' }
    case 'SET_FILTER':
      return { ...state, filter: action.filter }
    case 'MOUSE':
      return { ...state, mouse: { ...state.mouse, ...action.patch } }
    case 'TWS':
      return { ...state, tws: { ...state.tws, ...action.patch } }
    case 'EQ': {
      const eq = state.tws.eq.slice()
      eq[action.index] = action.value
      return { ...state, tws: { ...state.tws, eq, eqPreset: 'adat' } }
    }
    case 'GESTURE':
      return { ...state, tws: { ...state.tws, gestures: action.actions.slice() } }
    case 'SET_CONNECTED':
      return { ...state, connected: action.connected }
    default:
      return state
  }
}

export const FILTERS: { id: Filter; label: string }[] = [
  { id: 'semua', label: 'Semua' },
  { id: 'baterai', label: 'Baterai' },
  { id: 'performa', label: 'Performa' },
  { id: 'audio', label: 'Audio' },
  { id: 'koneksi', label: 'Koneksi' },
]

export const ANC_SUBS = [
  'AI Ear Adaptive',
  'Wind Noise',
  'Strong ANC',
  'Balanced ANC',
  'AI Environment',
]

export const AMB_SUBS = ['Default', 'Natural']

export const CODECS = [
  { value: 0, label: 'Stable' },
  { value: 1, label: 'aptX' },
  { value: 3, label: 'aptX Adaptive' },
  { value: 8, label: 'LDAC' },
  { value: 19, label: 'Lossless' },
]

export const EQ_FREQS = ['31.5', '63', '125', '250', '500', '1k', '2k', '4k', '8k', '16k']

export const EQ_PRESETS: Record<string, number[]> = {
  netral: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  bass: [8, 7, 5, 3, 1, 0, 0, 0, 0, 0],
  vokal: [0, 1, 2, 4, 6, 5, 3, 2, 1, 0],
}

export const GESTURES: { type: number; label: string; side: 'L' | 'R' }[] = [
  { type: 1, label: 'Single', side: 'L' },
  { type: 1, label: 'Single', side: 'R' },
  { type: 2, label: 'Double', side: 'L' },
  { type: 2, label: 'Double', side: 'R' },
  { type: 3, label: 'Triple', side: 'L' },
  { type: 3, label: 'Triple', side: 'R' },
  { type: 17, label: 'Long', side: 'L' },
  { type: 17, label: 'Long', side: 'R' },
]

export const GESTURE_ACTIONS = [
  { value: 16, label: 'Nonaktif' },
  { value: 1, label: 'Play / Jeda' },
  { value: 2, label: 'Volume +' },
  { value: 3, label: 'Volume −' },
  { value: 4, label: 'Sebelumnya' },
  { value: 5, label: 'Berikutnya' },
  { value: 6, label: 'Asisten' },
  { value: 7, label: 'Game mode' },
  { value: 8, label: 'Ganti noise' },
  { value: 13, label: 'Redial' },
]
