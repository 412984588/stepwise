import { useState } from 'react'
import { useTranslation } from '../i18n'
import { GradeSelector, GradeLevel } from './GradeSelector'
import { LocaleSelector } from './LocaleSelector'
import { Locale } from '../i18n'

export interface OnboardingData {
  gradeLevel: GradeLevel | null
  locale: Locale
  parentEmail: string
  optInSessionReports: boolean
  optInWeeklyDigest: boolean
}

interface OnboardingModalProps {
  isOpen: boolean
  onComplete: (data: OnboardingData) => void
  initialData?: Partial<OnboardingData>
}

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function OnboardingModal({ isOpen, onComplete, initialData }: OnboardingModalProps) {
  const { t, locale: currentLocale } = useTranslation()

  const [gradeLevel, setGradeLevel] = useState<GradeLevel | null>(initialData?.gradeLevel ?? null)
  const [locale, setLocale] = useState<Locale>(initialData?.locale ?? currentLocale)
  const [parentEmail, setParentEmail] = useState(initialData?.parentEmail ?? '')
  const [optInSessionReports, setOptInSessionReports] = useState(
    initialData?.optInSessionReports ?? false
  )
  const [optInWeeklyDigest, setOptInWeeklyDigest] = useState(
    initialData?.optInWeeklyDigest ?? false
  )
  const [emailError, setEmailError] = useState<string | null>(null)

  if (!isOpen) return null

  const validateEmail = (email: string): boolean => {
    if (!email) return true // Empty is valid (optional field)
    return EMAIL_REGEX.test(email)
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setParentEmail(value)
    if (value && !validateEmail(value)) {
      setEmailError(t('onboarding.emailInvalid'))
    } else {
      setEmailError(null)
    }
  }

  const handleContinue = () => {
    if (parentEmail && !validateEmail(parentEmail)) {
      setEmailError(t('onboarding.emailInvalid'))
      return
    }

    onComplete({
      gradeLevel,
      locale,
      parentEmail: parentEmail.trim(),
      optInSessionReports: parentEmail ? optInSessionReports : false,
      optInWeeklyDigest: parentEmail ? optInWeeklyDigest : false,
    })
  }

  const canContinue = !emailError && (!parentEmail || validateEmail(parentEmail))

  return (
    <div
      data-testid="onboarding-modal"
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
    >
      <div
        style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '32px',
          maxWidth: '500px',
          width: '90%',
          maxHeight: '90vh',
          overflow: 'auto',
        }}
      >
        {/* Welcome Section */}
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <h2
            style={{
              fontSize: '24px',
              fontWeight: 700,
              color: '#1f2937',
              marginBottom: '8px',
            }}
          >
            {t('onboarding.welcome.title')}
          </h2>
          <p style={{ color: '#6b7280', fontSize: '14px' }}>{t('onboarding.welcome.subtitle')}</p>
        </div>

        {/* Features List */}
        <div
          style={{
            backgroundColor: '#f0fdf4',
            borderRadius: '12px',
            padding: '16px',
            marginBottom: '24px',
          }}
        >
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            <li
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                marginBottom: '12px',
                fontSize: '14px',
                color: '#374151',
              }}
            >
              <span style={{ color: '#10b981', fontSize: '18px' }}>💡</span>
              <span>{t('onboarding.features.hints')}</span>
            </li>
            <li
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                marginBottom: '12px',
                fontSize: '14px',
                color: '#374151',
              }}
            >
              <span style={{ color: '#10b981', fontSize: '18px' }}>📄</span>
              <span>{t('onboarding.features.reports')}</span>
            </li>
            <li
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                fontSize: '14px',
                color: '#374151',
              }}
            >
              <span style={{ color: '#10b981', fontSize: '18px' }}>📧</span>
              <span>{t('onboarding.features.digest')}</span>
            </li>
          </ul>
        </div>

        {/* Preferences Section */}
        <div style={{ marginBottom: '24px' }}>
          <h3
            style={{
              fontSize: '16px',
              fontWeight: 600,
              color: '#374151',
              marginBottom: '16px',
            }}
          >
            {t('onboarding.preferences.title')}
          </h3>

          <div data-testid="onboarding-grade">
            <GradeSelector value={gradeLevel} onChange={setGradeLevel} />
          </div>

          <div data-testid="onboarding-locale">
            <LocaleSelector value={locale} onChange={setLocale} />
          </div>
        </div>

        {/* Email Section */}
        <div style={{ marginBottom: '24px' }}>
          <h3
            style={{
              fontSize: '16px',
              fontWeight: 600,
              color: '#374151',
              marginBottom: '16px',
            }}
          >
            {t('onboarding.email.title')}
          </h3>

          <div style={{ marginBottom: '16px' }}>
            <label
              htmlFor="parent-email"
              style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                color: '#4b5563',
              }}
            >
              {t('onboarding.email.label')}
            </label>
            <input
              id="parent-email"
              type="email"
              data-testid="onboarding-email"
              value={parentEmail}
              onChange={handleEmailChange}
              placeholder={t('onboarding.email.placeholder')}
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '16px',
                border: emailError ? '2px solid #ef4444' : '2px solid #e5e7eb',
                borderRadius: '8px',
                outline: 'none',
                boxSizing: 'border-box',
              }}
              onFocus={(e) => {
                if (!emailError) e.target.style.borderColor = '#3b82f6'
              }}
              onBlur={(e) => {
                if (!emailError) e.target.style.borderColor = '#e5e7eb'
              }}
            />
            {emailError && (
              <p style={{ color: '#ef4444', fontSize: '12px', marginTop: '4px' }}>{emailError}</p>
            )}
          </div>

          {/* Opt-in toggles */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <label
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                cursor: parentEmail ? 'pointer' : 'not-allowed',
                opacity: parentEmail ? 1 : 0.5,
              }}
            >
              <input
                type="checkbox"
                data-testid="onboarding-session-optin"
                checked={optInSessionReports}
                onChange={(e) => setOptInSessionReports(e.target.checked)}
                disabled={!parentEmail}
                style={{
                  width: '18px',
                  height: '18px',
                  cursor: parentEmail ? 'pointer' : 'not-allowed',
                }}
              />
              <span style={{ fontSize: '14px', color: '#374151' }}>
                {t('onboarding.email.sessionReports')}
              </span>
            </label>

            <label
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                cursor: parentEmail ? 'pointer' : 'not-allowed',
                opacity: parentEmail ? 1 : 0.5,
              }}
            >
              <input
                type="checkbox"
                data-testid="onboarding-weekly-optin"
                checked={optInWeeklyDigest}
                onChange={(e) => setOptInWeeklyDigest(e.target.checked)}
                disabled={!parentEmail}
                style={{
                  width: '18px',
                  height: '18px',
                  cursor: parentEmail ? 'pointer' : 'not-allowed',
                }}
              />
              <span style={{ fontSize: '14px', color: '#374151' }}>
                {t('onboarding.email.weeklyDigest')}
              </span>
            </label>
          </div>

          {/* Legal links */}
          <div
            style={{
              marginTop: '16px',
              fontSize: '12px',
              color: '#9ca3af',
            }}
          >
            <a
              href="/docs/PRIVACY_POLICY.md"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: '#3b82f6', textDecoration: 'underline' }}
            >
              {t('onboarding.legal.privacy')}
            </a>
            {' · '}
            <a
              href="/docs/TERMS_OF_SERVICE.md"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: '#3b82f6', textDecoration: 'underline' }}
            >
              {t('onboarding.legal.terms')}
            </a>
          </div>
        </div>

        {/* Continue Button */}
        <button
          data-testid="onboarding-continue"
          onClick={handleContinue}
          disabled={!canContinue}
          style={{
            width: '100%',
            padding: '14px 24px',
            fontSize: '16px',
            fontWeight: 600,
            color: 'white',
            backgroundColor: canContinue ? '#3b82f6' : '#9ca3af',
            border: 'none',
            borderRadius: '8px',
            cursor: canContinue ? 'pointer' : 'not-allowed',
            transition: 'background-color 0.2s',
          }}
          onMouseEnter={(e) => {
            if (canContinue) e.currentTarget.style.backgroundColor = '#2563eb'
          }}
          onMouseLeave={(e) => {
            if (canContinue) e.currentTarget.style.backgroundColor = '#3b82f6'
          }}
        >
          {t('onboarding.continueButton')}
        </button>
      </div>
    </div>
  )
}
