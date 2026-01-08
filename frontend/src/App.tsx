import { useState } from 'react'
import { ProblemInput } from './components/ProblemInput'
import { HintDialog } from './components/HintDialog'
import { ErrorMessage } from './components/ErrorMessage'
import { SolutionViewer } from './components/SolutionViewer'
import { Dashboard } from './components/Dashboard'
import {
  startSession,
  submitResponse,
  revealSolution,
  completeSession,
  getErrorMessage,
  SolutionStep,
} from './services/sessionApi'
import { HintLayer } from './types/enums'

type AppView = 'main' | 'dashboard'

interface SessionState {
  sessionId: string
  problemText: string
  currentLayer: HintLayer
  hintContent: string
  confusionCount: number
  isDowngrade: boolean
  canReveal: boolean
}

interface SolutionState {
  steps: SolutionStep[]
  finalAnswer: string
  explanation: string | null
}

function App() {
  const [view, setView] = useState<AppView>('main')
  const [session, setSession] = useState<SessionState | null>(null)
  const [solution, setSolution] = useState<SolutionState | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleStartSession = async (problemText: string) => {
    setIsLoading(true)
    setError(null)
    setSolution(null)

    try {
      const response = await startSession(problemText)
      setSession({
        sessionId: response.session_id,
        problemText,
        currentLayer: response.current_layer.toLowerCase() as HintLayer,
        hintContent: response.hint_content,
        confusionCount: 0,
        isDowngrade: false,
        canReveal: false,
      })
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsLoading(false)
    }
  }

  const handleRespond = async (responseText: string) => {
    if (!session) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await submitResponse(session.sessionId, responseText)
      setSession({
        ...session,
        currentLayer: response.current_layer.toLowerCase() as HintLayer,
        hintContent: response.hint_content,
        confusionCount: response.confusion_count ?? 0,
        isDowngrade: response.is_downgrade ?? false,
        canReveal: response.can_reveal_solution,
      })
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsLoading(false)
    }
  }

  const handleReveal = async () => {
    if (!session) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await revealSolution(session.sessionId)
      setSolution({
        steps: response.steps,
        finalAnswer: response.final_answer,
        explanation: response.explanation,
      })
      setSession(null)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsLoading(false)
    }
  }

  const handleComplete = async () => {
    if (!session) return

    setIsLoading(true)
    setError(null)

    try {
      await completeSession(session.sessionId)
      setSession(null)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    setSession(null)
    setSolution(null)
    setError(null)
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#f9fafb',
        padding: '40px 20px',
      }}
    >
      <div
        style={{
          maxWidth: '600px',
          margin: '0 auto',
        }}
      >
        <header style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h1
            style={{
              fontSize: '32px',
              fontWeight: 700,
              color: '#1f2937',
              marginBottom: '8px',
              cursor: 'pointer',
            }}
            onClick={() => setView('main')}
          >
            StepWise
          </h1>
          <p style={{ color: '#6b7280', fontSize: '16px' }}>
            苏格拉底式数学教练 - 引导你一步步思考
          </p>
        </header>

        {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

        {view === 'dashboard' ? (
          <Dashboard onBack={() => setView('main')} />
        ) : solution ? (
          <SolutionViewer
            steps={solution.steps}
            finalAnswer={solution.finalAnswer}
            explanation={solution.explanation}
            onNewProblem={handleCancel}
          />
        ) : !session ? (
          <div
            style={{
              backgroundColor: 'white',
              padding: '32px',
              borderRadius: '12px',
              boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
            }}
          >
            <ProblemInput onSubmit={handleStartSession} isLoading={isLoading} />
            <button
              onClick={() => setView('dashboard')}
              style={{
                width: '100%',
                marginTop: '16px',
                padding: '10px 16px',
                fontSize: '14px',
                color: '#6b7280',
                backgroundColor: '#f3f4f6',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
              }}
            >
              📊 查看学习统计
            </button>
          </div>
        ) : (
          <HintDialog
            problemText={session.problemText}
            currentLayer={session.currentLayer}
            hintContent={session.hintContent}
            onRespond={handleRespond}
            onCancel={handleCancel}
            onReveal={handleReveal}
            onComplete={handleComplete}
            isLoading={isLoading}
            confusionCount={session.confusionCount}
            isDowngrade={session.isDowngrade}
            canReveal={session.canReveal}
          />
        )}

        <footer
          style={{
            marginTop: '40px',
            textAlign: 'center',
            fontSize: '13px',
            color: '#9ca3af',
          }}
        >
          <p>不直接给答案，引导你独立思考 💡</p>
        </footer>
      </div>
    </div>
  )
}

export default App
