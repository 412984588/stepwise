const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  body?: unknown
  headers?: Record<string, string>
}

interface ApiError {
  error: string
  message: string
  details?: Array<{ field: string | null; message: string }>
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { method = 'GET', body, headers = {} } = options

    const config: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    }

    if (body) {
      config.body = JSON.stringify(body)
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, config)

    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        error: 'unknown_error',
        message: `HTTP ${response.status}: ${response.statusText}`,
      }))
      throw new ApiRequestError(errorData, response.status)
    }

    return response.json()
  }

  get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  post<T>(endpoint: string, body: unknown): Promise<T> {
    return this.request<T>(endpoint, { method: 'POST', body })
  }

  put<T>(endpoint: string, body: unknown): Promise<T> {
    return this.request<T>(endpoint, { method: 'PUT', body })
  }

  delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }
}

export class ApiRequestError extends Error {
  public readonly error: string
  public readonly details?: ApiError['details']
  public readonly statusCode: number

  constructor(apiError: ApiError, statusCode: number) {
    super(apiError.message)
    this.name = 'ApiRequestError'
    this.error = apiError.error
    this.details = apiError.details
    this.statusCode = statusCode
  }
}

export const apiClient = new ApiClient(`${API_BASE_URL}/api/v1`)
