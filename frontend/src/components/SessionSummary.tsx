import { useState, useEffect } from 'react'
import { getSessionSummary, SessionSummary as SummaryData } from '../services/sessionApi'

interface SessionSummaryProps {
  sessionId: string
}

export function SessionSummary({ sessionId }: SessionSummaryProps) {
  const [summary, setSummary] = useState<SummaryData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadSummary() {
      try {
        setIsLoading(true)
        const data = await getSessionSummary(sessionId)
        setSummary(data)
      } catch (err) {
        setError('Failed to load summary')
      } finally {
        setIsLoading(false)
      }
    }
    loadSummary()
  }, [sessionId])

  if (isLoading) {
    return (
      <div
        style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
          marginBottom: '20px',
        }}
      >
        <div style={{ color: '#9ca3af', textAlign: 'center' }}>Loading summary...</div>
      </div>
    )
  }

  if (error || !summary) {
    return null
  }

  const levelColors: Record<string, string> = {
    Excellent: '#22c55e',
    Good: '#3b82f6',
    'Needs Practice': '#f59e0b',
  }

  const levelColor = levelColors[summary.performance_level] || '#6b7280'

  return (
    <div
      style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
        marginBottom: '20px',
        border: `2px solid ${levelColor}15`,
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px',
        }}
      >
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#1f2937' }}>
          📊 Session Summary for Parents
        </h3>
        <div
          style={{
            padding: '4px 12px',
            fontSize: '13px',
            fontWeight: 600,
            color: levelColor,
            backgroundColor: `${levelColor}15`,
            borderRadius: '12px',
          }}
        >
          {summary.performance_level}
        </div>
      </div>

      <div
        style={{
          fontSize: '20px',
          fontWeight: 600,
          color: levelColor,
          marginBottom: '16px',
        }}
      >
        {summary.headline}
      </div>

      <div style={{ marginBottom: '16px' }}>
        <div
          style={{
            fontSize: '14px',
            fontWeight: 600,
            color: '#374151',
            marginBottom: '8px',
          }}
        >
          Key Insights:
        </div>
        <ul style={{ margin: 0, paddingLeft: '20px' }}>
          {summary.insights.map((insight, index) => (
            <li
              key={index}
              style={{
                fontSize: '14px',
                color: '#6b7280',
                marginBottom: '4px',
              }}
            >
              {insight}
            </li>
          ))}
        </ul>
      </div>

      <div
        style={{
          padding: '12px 16px',
          backgroundColor: '#f9fafb',
          borderRadius: '8px',
          borderLeft: `4px solid ${levelColor}`,
        }}
      >
        <div
          style={{
            fontSize: '13px',
            fontWeight: 600,
            color: '#374151',
            marginBottom: '4px',
          }}
        >
          💡 Recommendation:
        </div>
        <div style={{ fontSize: '14px', color: '#6b7280' }}>{summary.recommendation}</div>
      </div>
    </div>
  )
}
