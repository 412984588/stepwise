import { apiClient } from './api'

export interface UsageInfo {
  used: number
  limit: number | null
  can_start: boolean
}

export interface SubscriptionInfo {
  tier: 'free' | 'pro' | 'family'
  status: string
  current_period_end: string | null
  usage: UsageInfo | null
}

export interface CheckoutRequest {
  tier: 'pro' | 'family'
  success_url: string
  cancel_url: string
}

export interface CheckoutResponse {
  url: string
}

export interface PortalResponse {
  url: string
}

export async function getSubscription(userId: string): Promise<SubscriptionInfo> {
  return apiClient.get<SubscriptionInfo>('/billing/subscription', {
    headers: { 'X-User-ID': userId },
  })
}

export async function getUsage(userId: string): Promise<UsageInfo> {
  return apiClient.get<UsageInfo>('/billing/usage', {
    headers: { 'X-User-ID': userId },
  })
}

export async function createCheckout(
  userId: string,
  tier: 'pro' | 'family',
  successUrl: string,
  cancelUrl: string
): Promise<string> {
  const response = await apiClient.post<CheckoutResponse>(
    '/billing/checkout',
    {
      tier,
      success_url: successUrl,
      cancel_url: cancelUrl,
    },
    {
      headers: { 'X-User-ID': userId },
    }
  )
  return response.url
}

export async function createPortal(userId: string, returnUrl: string): Promise<string> {
  const response = await apiClient.post<PortalResponse>(
    '/billing/portal',
    {
      return_url: returnUrl,
    },
    {
      headers: { 'X-User-ID': userId },
    }
  )
  return response.url
}

export function getTierDisplayName(tier: string): string {
  const names: Record<string, string> = {
    free: 'Free',
    pro: 'Pro',
    family: 'Family',
  }
  return names[tier] || tier
}

export function getTierPrice(tier: string): string {
  const prices: Record<string, string> = {
    free: '$0',
    pro: '$9.99/mo',
    family: '$19.99/mo',
  }
  return prices[tier] || ''
}
