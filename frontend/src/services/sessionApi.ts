import { apiClient, ApiRequestError } from './api'

export interface StartSessionRequest {
  problem_text: string
  client_id?: string
}

export interface StartSessionResponse {
  session_id: string
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

export async function startSession(problemText: string): Promise<StartSessionResponse> {
  return apiClient.post<StartSessionResponse>('/sessions/start', {
    problem_text: problemText,
  })
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

export async function completeSession(sessionId: string): Promise<CompleteResponse> {
  return apiClient.post<CompleteResponse>(`/sessions/${sessionId}/complete`, {})
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
