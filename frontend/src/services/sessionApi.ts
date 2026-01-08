import { apiClient, ApiRequestError } from './api'

export interface StartSessionRequest {
  problem_text: string
  client_id?: string
  locale?: string
  grade_level?: number
}

export interface StartSessionResponse {
  session_id: string
  session_access_token: string
  problem_type: string
  current_layer: string
  hint_content: string
  requires_response: boolean
}

export interface SessionResponse {
  session_id: string
  problem: {
    raw_text: string
    problem_type: string
  }
  status: string
  current_layer: string
  confusion_count: number
  layers_completed: string[]
  can_reveal_solution: boolean
  last_hint: string | null
  started_at: string
  last_active_at: string
}

export interface RespondRequest {
  response_text: string
}

export interface RespondResponse {
  session_id: string
  current_layer: string
  previous_layer?: string
  understanding_level: string
  confusion_count?: number
  is_downgrade?: boolean
  hint_content: string
  requires_response: boolean
  can_reveal_solution: boolean
}

export interface ApiErrorResponse {
  error: string
  message: string
}

export interface SolutionStep {
  description: string
  result: string
}

export interface RevealResponse {
  session_id: string
  steps: SolutionStep[]
  final_answer: string
  explanation: string | null
  status: string
}

export interface CompleteResponse {
  session_id: string
  status: string
  message: string
  email_sent?: boolean
}

export interface StatsSummary {
  total_sessions: number
  completed_sessions: number
  revealed_sessions: number
  active_sessions: number
  completion_rate: number
  avg_layers_to_complete: number | null
}

export interface SessionListItem {
  session_id: string
  session_access_token: string
  problem_text: string
  status: string
  final_layer: string
  confusion_count: number
  used_full_solution: boolean
  started_at: string
  completed_at: string | null
}

export interface SessionListResponse {
  sessions: SessionListItem[]
  total: number
  limit: number
  offset: number
}

export interface ProblemTypeStats {
  type: string
  label: string
  total: number
  completed: number
  revealed: number
  completion_rate: number
}

export interface EncouragementMessage {
  streak_message: string
  performance_message: string
}

export interface DashboardData {
  total_learning_days: number
  independent_completion_rate: number
  sessions_this_week: number
  learning_streak: number
  avg_confusion_count: number | null
  avg_layers_to_complete: number | null
  problem_type_stats: ProblemTypeStats[]
  recent_sessions: SessionListItem[]
  first_session_date: string | null
  last_session_date: string | null
  encouragement: EncouragementMessage
}

export async function startSession(
  problemText: string,
  options?: { locale?: string; gradeLevel?: number; userId?: string }
): Promise<StartSessionResponse> {
  const payload: StartSessionRequest = {
    problem_text: problemText,
  }
  if (options?.locale) {
    payload.locale = options.locale
  }
  if (options?.gradeLevel) {
    payload.grade_level = options.gradeLevel
  }
  const headers: Record<string, string> = {}
  if (options?.userId) {
    headers['X-User-ID'] = options.userId
  }
  return apiClient.post<StartSessionResponse>('/sessions/start', payload, { headers })
}

export async function getSession(sessionId: string): Promise<SessionResponse> {
  return apiClient.get<SessionResponse>(`/sessions/${sessionId}`)
}

export async function submitResponse(
  sessionId: string,
  responseText: string
): Promise<RespondResponse> {
  return apiClient.post<RespondResponse>(`/sessions/${sessionId}/respond`, {
    response_text: responseText,
  })
}

export async function revealSolution(sessionId: string): Promise<RevealResponse> {
  return apiClient.post<RevealResponse>(`/sessions/${sessionId}/reveal`, {})
}

export async function completeSession(
  sessionId: string,
  email?: string
): Promise<CompleteResponse> {
  const payload: { email?: string } = {}
  if (email) {
    payload.email = email
  }
  return apiClient.post<CompleteResponse>(`/sessions/${sessionId}/complete`, payload)
}

export async function getStatsSummary(): Promise<StatsSummary> {
  return apiClient.get<StatsSummary>('/stats/summary')
}

export async function getSessionHistory(
  limit: number = 20,
  offset: number = 0
): Promise<SessionListResponse> {
  return apiClient.get<SessionListResponse>(`/stats/sessions?limit=${limit}&offset=${offset}`)
}

export async function getDashboard(): Promise<DashboardData> {
  return apiClient.get<DashboardData>('/stats/dashboard')
}

export interface DailyStats {
  date: string
  total: number
  completed: number
  revealed: number
}

export interface TrendData {
  daily_stats: DailyStats[]
  period_days: number
}

export interface GoalProgress {
  daily_target: number
  daily_completed: number
  daily_progress: number
  weekly_target: number
  weekly_completed: number
  weekly_progress: number
}

export async function getTrendData(days: number = 7): Promise<TrendData> {
  return apiClient.get<TrendData>(`/stats/trend?days=${days}`)
}

export async function getGoalProgress(
  dailyTarget: number = 3,
  weeklyTarget: number = 15
): Promise<GoalProgress> {
  return apiClient.get<GoalProgress>(
    `/stats/goals?daily_target=${dailyTarget}&weekly_target=${weeklyTarget}`
  )
}

export function isApiError(error: unknown): error is ApiRequestError {
  return error instanceof ApiRequestError
}

export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return '发生了未知错误，请稍后重试'
}

export interface ReportEventRequest {
  event_type: string
  details?: Record<string, any>
}

export async function reportEvent(
  sessionId: string,
  eventType: string,
  details?: Record<string, any>
): Promise<void> {
  // Note: This is a fire-and-forget call for analytics
  // We don't want to block the UI if event logging fails
  try {
    await apiClient.post(`/sessions/${sessionId}/events`, {
      event_type: eventType,
      details,
    })
  } catch (error) {
    // Silently fail - event logging should not disrupt user experience
    console.warn('Failed to log event:', eventType, error)
  }
}

export async function downloadSessionPDF(
  sessionId: string,
  sessionAccessToken: string
): Promise<void> {
  const url = `${apiClient['baseUrl']}/reports/session/${sessionId}/pdf`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'X-Session-Access-Token': sessionAccessToken,
    },
  })

  if (response.status === 403) {
    throw new Error('Session access token invalid or expired')
  }

  if (!response.ok) {
    throw new Error(`Failed to download PDF: ${response.statusText}`)
  }

  const blob = await response.blob()
  const blobUrl = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = blobUrl
  link.download = `stepwise_session_${sessionId}.pdf`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(blobUrl)
}

export interface SessionSummary {
  headline: string
  performance_level: string
  insights: string[]
  recommendation: string
}

export async function getSessionSummary(sessionId: string): Promise<SessionSummary> {
  return apiClient.get<SessionSummary>(`/reports/session/${sessionId}/summary`)
}
