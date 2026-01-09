import { useState, useEffect } from 'react'

interface FeedbackStats {
  total_count: number
  pmf_score: number
  pmf_breakdown: {
    very_disappointed: number
    somewhat_disappointed: number
    not_disappointed: number
  }
  grade_breakdown: Record<string, number>
  would_pay_breakdown: Record<string, number>
  email_opt_in_rate: number
}

interface FeedbackItem {
  id: string
  created_at: string
  grade_level: string
  pmf_answer: string
  would_pay: string | null
  what_worked: string | null
  what_confused: string | null
  email: string | null
  locale: string
}

interface FeedbackListResponse {
  items: FeedbackItem[]
  total: number
  has_more: boolean
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const PMF_LABELS: Record<string, string> = {
  very_disappointed: 'Very Disappointed',
  somewhat_disappointed: 'Somewhat Disappointed',
  not_disappointed: 'Not Disappointed',
}

const GRADE_LABELS: Record<string, string> = {
  grade_4: 'Grade 4',
  grade_5: 'Grade 5',
  grade_6: 'Grade 6',
  grade_7: 'Grade 7',
  grade_8: 'Grade 8',
  grade_9: 'Grade 9',
}

const WOULD_PAY_LABELS: Record<string, string> = {
  yes_definitely: 'Yes, definitely',
  yes_probably: 'Yes, probably',
  not_sure: 'Not sure',
  probably_not: 'Probably not',
  definitely_not: 'Definitely not',
}

interface FeedbackDashboardProps {
  onBack: () => void
}

export function FeedbackDashboard({ onBack }: FeedbackDashboardProps) {
  const [stats, setStats] = useState<FeedbackStats | null>(null)
  const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [listTotal, setListTotal] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const [offset, setOffset] = useState(0)

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const [statsRes, listRes] = await Promise.all([
          fetch(`${API_BASE}/api/v1/feedback/stats`),
          fetch(`${API_BASE}/api/v1/feedback/list?limit=20&offset=0`),
        ])

        if (!statsRes.ok || !listRes.ok) {
          throw new Error('Failed to load feedback data')
        }

        const statsData: FeedbackStats = await statsRes.json()
        const listData: FeedbackListResponse = await listRes.json()

        setStats(statsData)
        setFeedbackList(listData.items)
        setListTotal(listData.total)
        setHasMore(listData.has_more)
        setOffset(20)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  const loadMore = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/feedback/list?limit=20&offset=${offset}`)
      if (!res.ok) throw new Error('Failed to load more')
      const data: FeedbackListResponse = await res.json()
      setFeedbackList((prev) => [...prev, ...data.items])
      setHasMore(data.has_more)
      setOffset((prev) => prev + 20)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  const handleExport = () => {
    window.open(`${API_BASE}/api/v1/feedback/export`, '_blank')
  }

  if (isLoading) {
    return (
      <div data-testid="feedback-dashboard" style={{ padding: '32px', textAlign: 'center' }}>
        Loading feedback data...
      </div>
    )
  }

  if (error) {
    return (
      <div data-testid="feedback-dashboard" style={{ padding: '32px' }}>
        <div style={{ color: '#dc2626', marginBottom: '16px' }}>Error: {error}</div>
        <button onClick={onBack} style={backButtonStyle}>
          ← Back
        </button>
      </div>
    )
  }

  if (!stats) {
    return null
  }

  const pmfColor = stats.pmf_score >= 40 ? '#16a34a' : stats.pmf_score >= 25 ? '#ca8a04' : '#dc2626'

  return (
    <div data-testid="feedback-dashboard" style={{ padding: '0' }}>
      <div
        style={{
          marginBottom: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <button onClick={onBack} style={backButtonStyle} data-testid="back-button">
          ← Back
        </button>
        <button onClick={handleExport} style={exportButtonStyle} data-testid="export-csv">
          📥 Export CSV
        </button>
      </div>

      <h2 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '24px', color: '#1f2937' }}>
        Feedback Analytics
      </h2>

      {/* PMF Score Card */}
      <div style={cardStyle}>
        <h3 style={cardTitleStyle}>Product-Market Fit Score</h3>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <span
            data-testid="pmf-score"
            style={{ fontSize: '48px', fontWeight: 700, color: pmfColor }}
          >
            {stats.pmf_score}%
          </span>
          <span style={{ color: '#6b7280', fontSize: '14px' }}>
            ({stats.pmf_breakdown.very_disappointed || 0} of {stats.total_count} very disappointed)
          </span>
        </div>
        <p style={{ marginTop: '8px', fontSize: '13px', color: '#6b7280' }}>
          Target: 40%+ indicates strong product-market fit
        </p>
      </div>

      {/* Stats Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '16px',
          marginBottom: '24px',
        }}
      >
        <div style={cardStyle}>
          <h3 style={cardTitleStyle}>Total Responses</h3>
          <span
            data-testid="total-count"
            style={{ fontSize: '32px', fontWeight: 600, color: '#1f2937' }}
          >
            {stats.total_count}
          </span>
        </div>
        <div style={cardStyle}>
          <h3 style={cardTitleStyle}>Email Opt-in Rate</h3>
          <span
            data-testid="email-rate"
            style={{ fontSize: '32px', fontWeight: 600, color: '#1f2937' }}
          >
            {stats.email_opt_in_rate}%
          </span>
        </div>
      </div>

      {/* PMF Breakdown */}
      <div style={cardStyle}>
        <h3 style={cardTitleStyle}>PMF Breakdown</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {Object.entries(stats.pmf_breakdown).map(([key, value]) => (
            <div key={key} style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#4b5563' }}>{PMF_LABELS[key] || key}</span>
              <span style={{ fontWeight: 500 }}>{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Grade Breakdown */}
      {Object.keys(stats.grade_breakdown).length > 0 && (
        <div style={cardStyle}>
          <h3 style={cardTitleStyle}>By Grade Level</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Object.entries(stats.grade_breakdown)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([key, value]) => (
                <div key={key} style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#4b5563' }}>{GRADE_LABELS[key] || key}</span>
                  <span style={{ fontWeight: 500 }}>{value}</span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Would Pay Breakdown */}
      {Object.keys(stats.would_pay_breakdown).length > 0 && (
        <div style={cardStyle}>
          <h3 style={cardTitleStyle}>Would Pay?</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Object.entries(stats.would_pay_breakdown).map(([key, value]) => (
              <div key={key} style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#4b5563' }}>{WOULD_PAY_LABELS[key] || key}</span>
                <span style={{ fontWeight: 500 }}>{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Feedback */}
      <div style={{ ...cardStyle, marginTop: '24px' }}>
        <h3 style={cardTitleStyle}>Recent Feedback ({listTotal} total)</h3>
        {feedbackList.length === 0 ? (
          <p style={{ color: '#6b7280' }}>No feedback yet</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {feedbackList.map((item) => (
              <div
                key={item.id}
                data-testid="feedback-item"
                style={{
                  padding: '12px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '8px',
                  fontSize: '14px',
                }}
              >
                <div
                  style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}
                >
                  <span style={{ fontWeight: 500, color: '#1f2937' }}>
                    {GRADE_LABELS[item.grade_level] || item.grade_level}
                  </span>
                  <span style={{ color: '#6b7280', fontSize: '12px' }}>
                    {new Date(item.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div style={{ marginBottom: '4px' }}>
                  <span style={{ color: '#6b7280' }}>PMF: </span>
                  <span style={{ fontWeight: 500 }}>
                    {PMF_LABELS[item.pmf_answer] || item.pmf_answer}
                  </span>
                </div>
                {item.would_pay && (
                  <div style={{ marginBottom: '4px' }}>
                    <span style={{ color: '#6b7280' }}>Would Pay: </span>
                    <span>{WOULD_PAY_LABELS[item.would_pay] || item.would_pay}</span>
                  </div>
                )}
                {item.what_worked && (
                  <div style={{ marginBottom: '4px' }}>
                    <span style={{ color: '#6b7280' }}>What worked: </span>
                    <span>{item.what_worked}</span>
                  </div>
                )}
                {item.what_confused && (
                  <div style={{ marginBottom: '4px' }}>
                    <span style={{ color: '#6b7280' }}>What confused: </span>
                    <span>{item.what_confused}</span>
                  </div>
                )}
                {item.email && (
                  <div>
                    <span style={{ color: '#6b7280' }}>Email: </span>
                    <span>{item.email}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
        {hasMore && (
          <button
            onClick={loadMore}
            data-testid="load-more"
            style={{
              marginTop: '16px',
              padding: '8px 16px',
              backgroundColor: '#f3f4f6',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              width: '100%',
            }}
          >
            Load More
          </button>
        )}
      </div>
    </div>
  )
}

const cardStyle: React.CSSProperties = {
  backgroundColor: 'white',
  padding: '20px',
  borderRadius: '12px',
  boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
  marginBottom: '16px',
}

const cardTitleStyle: React.CSSProperties = {
  fontSize: '14px',
  fontWeight: 500,
  color: '#6b7280',
  marginBottom: '12px',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
}

const backButtonStyle: React.CSSProperties = {
  padding: '8px 16px',
  fontSize: '14px',
  color: '#6b7280',
  backgroundColor: '#f3f4f6',
  border: 'none',
  borderRadius: '6px',
  cursor: 'pointer',
}

const exportButtonStyle: React.CSSProperties = {
  padding: '8px 16px',
  fontSize: '14px',
  color: 'white',
  backgroundColor: '#2563eb',
  border: 'none',
  borderRadius: '6px',
  cursor: 'pointer',
}
