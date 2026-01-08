import { useMemo } from 'react'

const USER_ID_KEY = 'stepwise_user_id'

function generateUserId(): string {
  return `usr_${crypto.randomUUID().replace(/-/g, '').slice(0, 16)}`
}

function getOrCreateUserId(): string {
  const stored = localStorage.getItem(USER_ID_KEY)
  if (stored) return stored
  const newId = generateUserId()
  localStorage.setItem(USER_ID_KEY, newId)
  return newId
}

export function useUserId(): string {
  return useMemo(getOrCreateUserId, [])
}
