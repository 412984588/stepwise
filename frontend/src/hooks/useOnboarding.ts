import { useState, useCallback } from 'react'
import { GradeLevel } from '../components/GradeSelector'
import { Locale } from '../i18n'

const STORAGE_KEYS = {
  COMPLETED: 'onboarding_completed',
  GRADE_LEVEL: 'grade_level',
  LOCALE: 'locale',
  PARENT_EMAIL: 'parent_email',
  OPT_IN_SESSION_REPORTS: 'opt_in_session_reports',
  OPT_IN_WEEKLY_DIGEST: 'opt_in_weekly_digest',
} as const

export interface OnboardingPreferences {
  gradeLevel: GradeLevel | null
  locale: Locale
  parentEmail: string
  optInSessionReports: boolean
  optInWeeklyDigest: boolean
}

function getStoredBoolean(key: string, defaultValue: boolean): boolean {
  const stored = localStorage.getItem(key)
  if (stored === null) return defaultValue
  return stored === 'true'
}

function getStoredGrade(): GradeLevel | null {
  const stored = localStorage.getItem(STORAGE_KEYS.GRADE_LEVEL)
  if (!stored) return null
  const parsed = parseInt(stored, 10)
  if (parsed >= 4 && parsed <= 9) return parsed as GradeLevel
  return null
}

function getStoredLocale(): Locale {
  const stored = localStorage.getItem(STORAGE_KEYS.LOCALE)
  if (stored === 'en-US' || stored === 'zh-CN') return stored
  return 'en-US'
}

function readPreferences(): OnboardingPreferences {
  return {
    gradeLevel: getStoredGrade(),
    locale: getStoredLocale(),
    parentEmail: localStorage.getItem(STORAGE_KEYS.PARENT_EMAIL) ?? '',
    optInSessionReports: getStoredBoolean(STORAGE_KEYS.OPT_IN_SESSION_REPORTS, false),
    optInWeeklyDigest: getStoredBoolean(STORAGE_KEYS.OPT_IN_WEEKLY_DIGEST, false),
  }
}

export function useOnboarding() {
  const [isCompleted, setIsCompleted] = useState(() =>
    getStoredBoolean(STORAGE_KEYS.COMPLETED, false)
  )
  const [preferences, setPreferences] = useState<OnboardingPreferences>(readPreferences)

  const savePreferences = useCallback((prefs: OnboardingPreferences) => {
    if (prefs.gradeLevel !== null) {
      localStorage.setItem(STORAGE_KEYS.GRADE_LEVEL, String(prefs.gradeLevel))
    } else {
      localStorage.removeItem(STORAGE_KEYS.GRADE_LEVEL)
    }
    localStorage.setItem(STORAGE_KEYS.LOCALE, prefs.locale)

    if (prefs.parentEmail) {
      localStorage.setItem(STORAGE_KEYS.PARENT_EMAIL, prefs.parentEmail)
    } else {
      localStorage.removeItem(STORAGE_KEYS.PARENT_EMAIL)
    }

    localStorage.setItem(STORAGE_KEYS.OPT_IN_SESSION_REPORTS, String(prefs.optInSessionReports))
    localStorage.setItem(STORAGE_KEYS.OPT_IN_WEEKLY_DIGEST, String(prefs.optInWeeklyDigest))
    localStorage.setItem(STORAGE_KEYS.COMPLETED, 'true')

    setPreferences(prefs)
    setIsCompleted(true)
  }, [])

  const resetOnboarding = useCallback(() => {
    localStorage.removeItem(STORAGE_KEYS.COMPLETED)
    setPreferences(readPreferences())
    setIsCompleted(false)
  }, [])

  return {
    isCompleted,
    preferences,
    savePreferences,
    resetOnboarding,
  }
}
