import { HintLayer, SessionStatus } from '../types/enums'

interface HintContent {
  layer: HintLayer
  content: string
  sequence: number
}

interface SessionState {
  sessionId: string | null
  problemId: string | null
  currentLayer: HintLayer
  status: SessionStatus
  hints: HintContent[]
  confusionCount: number
}

const STORAGE_KEY = 'stepwise_session'

const initialState: SessionState = {
  sessionId: null,
  problemId: null,
  currentLayer: HintLayer.CONCEPT,
  status: SessionStatus.ACTIVE,
  hints: [],
  confusionCount: 0,
}

function loadFromStorage(): SessionState {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      return JSON.parse(stored)
    }
  } catch {
    console.error('Failed to load session from storage')
  }
  return initialState
}

function saveToStorage(state: SessionState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    console.error('Failed to save session to storage')
  }
}

class SessionStore {
  private state: SessionState
  private listeners: Set<(state: SessionState) => void> = new Set()

  constructor() {
    this.state = loadFromStorage()
  }

  getState(): SessionState {
    return this.state
  }

  subscribe(listener: (state: SessionState) => void): () => void {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  private notify(): void {
    this.listeners.forEach((listener) => listener(this.state))
  }

  private setState(updates: Partial<SessionState>): void {
    this.state = { ...this.state, ...updates }
    saveToStorage(this.state)
    this.notify()
  }

  startSession(sessionId: string, problemId: string, firstHint: HintContent): void {
    this.setState({
      sessionId,
      problemId,
      currentLayer: HintLayer.CONCEPT,
      status: SessionStatus.ACTIVE,
      hints: [firstHint],
      confusionCount: 0,
    })
  }

  addHint(hint: HintContent): void {
    this.setState({
      hints: [...this.state.hints, hint],
      currentLayer: hint.layer,
    })
  }

  incrementConfusion(): void {
    this.setState({
      confusionCount: this.state.confusionCount + 1,
    })
  }

  resetConfusion(): void {
    this.setState({
      confusionCount: 0,
    })
  }

  advanceLayer(newLayer: HintLayer): void {
    this.setState({
      currentLayer: newLayer,
      confusionCount: 0,
    })
  }

  completeSession(status: SessionStatus.COMPLETED | SessionStatus.REVEALED): void {
    this.setState({
      status,
      currentLayer: status === SessionStatus.COMPLETED ? HintLayer.COMPLETED : HintLayer.REVEALED,
    })
  }

  clearSession(): void {
    this.setState(initialState)
    localStorage.removeItem(STORAGE_KEY)
  }

  hasActiveSession(): boolean {
    return this.state.sessionId !== null && this.state.status === SessionStatus.ACTIVE
  }
}

export const sessionStore = new SessionStore()
export type { SessionState, HintContent }
