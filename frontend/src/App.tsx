import { useState, useEffect, useCallback } from 'react'
import { ProblemInput } from './components/ProblemInput'
import { HintDialog } from './components/HintDialog'
import { ErrorMessage } from './components/ErrorMessage'
import { SuccessMessage } from './components/SuccessMessage'
import { SolutionViewer } from './components/SolutionViewer'
import { Dashboard } from './components/Dashboard'
import { FeedbackDashboard } from './components/FeedbackDashboard'
import { GradeSelector, GradeLevel } from './components/GradeSelector'
import { SubscriptionBanner } from './components/SubscriptionBanner'
import { UpgradeModal } from './components/UpgradeModal'
import { FeedbackModal } from './components/FeedbackModal'
import { OnboardingModal, OnboardingData } from './components/OnboardingModal'
import { BetaGateModal } from './components/BetaGateModal'
import {
  startSession,
  submitResponse,
  revealSolution,
  completeSession,
  getErrorMessage,
  SolutionStep,
  isApiError,
} from './services/sessionApi'
import { getSubscription, createCheckout, SubscriptionInfo } from './services/billingApi'
import { HintLayer } from './types/enums'
import { useTranslation, useI18n } from './i18n'
import { useUserId } from './hooks/useUserId'
import { useOnboarding } from './hooks/useOnboarding'
import { useBetaCode } from './hooks/useBetaCode'

type AppView = 'main' | 'dashboard' | 'feedback-dashboard'

interface SessionState {
  sessionId: string
  sessionAccessToken: string
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
  const { t, locale } = useTranslation()
  const { setLocale } = useI18n()
  const userId = useUserId()
  const {
    isCompleted: onboardingCompleted,
    preferences,
    savePreferences,
    resetOnboarding,
  } = useOnboarding()
  const { setBetaCode, clearBetaCode, isValidated: hasBetaCode } = useBetaCode()
  const [showOnboardingModal, setShowOnboardingModal] = useState(!onboardingCompleted)
  const [showBetaGateModal, setShowBetaGateModal] = useState(!hasBetaCode)
  const [betaGateError, setBetaGateError] = useState<string | null>(null)
  const [betaGateLoading, setBetaGateLoading] = useState(false)
  const [view, setView] = useState<AppView>('main')
  const [session, setSession] = useState<SessionState | null>(null)
  const [solution, setSolution] = useState<SolutionState | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [gradeLevel, setGradeLevel] = useState<GradeLevel | null>(preferences.gradeLevel)
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null)
  const [showUpgradeModal, setShowUpgradeModal] = useState(false)
  const [showFeedbackModal, setShowFeedbackModal] = useState(false)

  const handleBetaCodeSubmit = useCallback(
    async (code: string) => {
      setBetaGateLoading(true)
      setBetaGateError(null)

      setBetaCode(code)

      try {
        await startSession('1+1=?', { locale, gradeLevel: 4, userId })
        setShowBetaGateModal(false)
      } catch (err) {
        if (
          isApiError(err) &&
          (err.error === 'BETA_CODE_REQUIRED' || err.error === 'BETA_CODE_INVALID')
        ) {
          clearBetaCode()
          setBetaGateError('Invalid beta access code. Please check your code and try again.')
        } else {
          setShowBetaGateModal(false)
        }
      } finally {
        setBetaGateLoading(false)
      }
    },
    [locale, userId, setBetaCode, clearBetaCode]
  )

  useEffect(() => {
    const loadSubscription = async () => {
      try {
        const sub = await getSubscription(userId)
        setSubscription(sub)
      } catch {
        setSubscription({
          tier: 'free',
          status: 'active',
          current_period_end: null,
          usage: { used: 0, limit: 3, can_start: true },
        })
      }
    }
    loadSubscription()
  }, [userId])

  const handleBetaCodeError = useCallback(
    (err: unknown) => {
      if (
        isApiError(err) &&
        (err.error === 'BETA_CODE_REQUIRED' || err.error === 'BETA_CODE_INVALID')
      ) {
        clearBetaCode()
        setShowBetaGateModal(true)
        setBetaGateError('Your beta access code is invalid or expired. Please enter a valid code.')
        return true
      }
      return false
    },
    [clearBetaCode]
  )

  const handleStartSession = async (problemText: string) => {
    setIsLoading(true)
    setError(null)
    setSuccessMessage(null)
    setSolution(null)

    try {
      const response = await startSession(problemText, {
        locale,
        gradeLevel: gradeLevel ?? undefined,
        userId,
      })
      setSession({
        sessionId: response.session_id,
        sessionAccessToken: response.session_access_token,
        problemText,
        currentLayer: response.current_layer.toLowerCase() as HintLayer,
        hintContent: response.hint_content,
        confusionCount: 0,
        isDowngrade: false,
        canReveal: false,
      })
    } catch (err) {
      if (!handleBetaCodeError(err)) {
        setError(getErrorMessage(err))
      }
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
      if (!handleBetaCodeError(err)) {
        setError(getErrorMessage(err))
      }
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
      if (!handleBetaCodeError(err)) {
        setError(getErrorMessage(err))
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleComplete = async (email?: string) => {
    if (!session) return

    setIsLoading(true)
    setError(null)
    setSuccessMessage(null)

    try {
      const response = await completeSession(session.sessionId, email)
      setSession(null)

      if (email && response.email_sent) {
        setSuccessMessage(t('hintDialog.emailSent'))
      } else if (email && !response.email_sent) {
        setError(t('hintDialog.emailFailed'))
      }
    } catch (err) {
      if (!handleBetaCodeError(err)) {
        setError(getErrorMessage(err))
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    setSession(null)
    setSolution(null)
    setError(null)
  }

  const handleUpgrade = async (tier: 'pro' | 'family') => {
    try {
      const checkoutUrl = await createCheckout(
        userId,
        tier,
        `${window.location.origin}?upgraded=true`,
        window.location.href
      )
      window.location.href = checkoutUrl
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  const refreshSubscription = useCallback(async () => {
    try {
      const sub = await getSubscription(userId)
      setSubscription(sub)
    } catch (_) {
      void 0
    }
  }, [userId])

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    if (params.get('upgraded') === 'true') {
      refreshSubscription()
      window.history.replaceState({}, '', window.location.pathname)
    }
  }, [refreshSubscription])

  const handleOnboardingComplete = (data: OnboardingData) => {
    savePreferences(data)
    setGradeLevel(data.gradeLevel)
    setLocale(data.locale)
    setShowOnboardingModal(false)
  }

  const handleOpenSettings = () => {
    resetOnboarding()
    setShowOnboardingModal(true)
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
          <p style={{ color: '#6b7280', fontSize: '16px' }}>{t('app.subtitle')}</p>
        </header>

        {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}
        {successMessage && (
          <SuccessMessage message={successMessage} onDismiss={() => setSuccessMessage(null)} />
        )}

        {subscription && view === 'main' && !session && !solution && (
          <SubscriptionBanner
            tier={subscription.tier}
            used={subscription.usage?.used ?? 0}
            limit={subscription.usage?.limit ?? null}
            onUpgradeClick={() => setShowUpgradeModal(true)}
          />
        )}

        {view === 'dashboard' ? (
          <Dashboard onBack={() => setView('main')} />
        ) : view === 'feedback-dashboard' ? (
          <FeedbackDashboard onBack={() => setView('main')} />
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
            <GradeSelector value={gradeLevel} onChange={setGradeLevel} disabled={isLoading} />
            <ProblemInput onSubmit={handleStartSession} isLoading={isLoading} />
            <button
              data-testid="nav-dashboard"
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
              📊 View Learning Stats
            </button>
            <button
              data-testid="nav-feedback-dashboard"
              onClick={() => setView('feedback-dashboard')}
              style={{
                width: '100%',
                marginTop: '8px',
                padding: '10px 16px',
                fontSize: '14px',
                color: '#6b7280',
                backgroundColor: '#f3f4f6',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
              }}
            >
              📈 Feedback Analytics
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
            defaultEmail={preferences.optInSessionReports ? preferences.parentEmail : ''}
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
          <p>{t('app.footer')}</p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '8px' }}>
            <button
              data-testid="nav-feedback"
              onClick={() => setShowFeedbackModal(true)}
              style={{
                padding: '6px 12px',
                fontSize: '12px',
                color: '#6b7280',
                backgroundColor: 'transparent',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                cursor: 'pointer',
              }}
            >
              💬 Feedback
            </button>
            <button
              data-testid="nav-settings"
              onClick={handleOpenSettings}
              style={{
                padding: '6px 12px',
                fontSize: '12px',
                color: '#6b7280',
                backgroundColor: 'transparent',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                cursor: 'pointer',
              }}
            >
              ⚙️ {t('onboarding.settingsButton')}
            </button>
          </div>
        </footer>
      </div>

      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        onSelectTier={handleUpgrade}
        currentTier={subscription?.tier ?? 'free'}
      />

      <FeedbackModal
        isOpen={showFeedbackModal}
        onClose={() => setShowFeedbackModal(false)}
        onSuccess={() => setSuccessMessage('Thank you for your feedback!')}
      />

      <OnboardingModal
        isOpen={showOnboardingModal && !showBetaGateModal}
        onComplete={handleOnboardingComplete}
        initialData={preferences}
      />

      <BetaGateModal
        isOpen={showBetaGateModal}
        onSubmit={handleBetaCodeSubmit}
        error={betaGateError}
        isLoading={betaGateLoading}
      />
    </div>
  )
}

export default App
