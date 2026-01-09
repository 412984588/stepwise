import { useState, useCallback } from 'react'

const BETA_CODE_KEY = 'beta_access_code'

export interface UseBetaCodeResult {
  betaCode: string | null
  setBetaCode: (code: string) => void
  clearBetaCode: () => void
  isValidated: boolean
}

export function useBetaCode(): UseBetaCodeResult {
  const [betaCode, setBetaCodeState] = useState<string | null>(() => {
    try {
      return localStorage.getItem(BETA_CODE_KEY)
    } catch {
      return null
    }
  })

  const [isValidated, setIsValidated] = useState<boolean>(() => {
    try {
      return localStorage.getItem(BETA_CODE_KEY) !== null
    } catch {
      return false
    }
  })

  const setBetaCode = useCallback((code: string) => {
    try {
      localStorage.setItem(BETA_CODE_KEY, code)
      setBetaCodeState(code)
      setIsValidated(true)
    } catch (error) {
      console.error('Failed to save beta code to localStorage:', error)
    }
  }, [])

  const clearBetaCode = useCallback(() => {
    try {
      localStorage.removeItem(BETA_CODE_KEY)
      setBetaCodeState(null)
      setIsValidated(false)
    } catch (error) {
      console.error('Failed to clear beta code from localStorage:', error)
    }
  }, [])

  return {
    betaCode,
    setBetaCode,
    clearBetaCode,
    isValidated,
  }
}

/**
 * Get the beta code from localStorage (for use in API client).
 * Returns null if not set.
 */
export function getBetaCode(): string | null {
  try {
    return localStorage.getItem(BETA_CODE_KEY)
  } catch {
    return null
  }
}
