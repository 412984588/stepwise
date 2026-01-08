import { DailyStats } from '../services/sessionApi'

interface TrendChartProps {
  data: DailyStats[]
}

export function TrendChart({ data }: TrendChartProps) {
  const maxTotal = Math.max(...data.map((d) => d.total), 1)
  const chartHeight = 120
  const chartWidth = 280
  const barWidth = (chartWidth - 20) / data.length - 4

  return (
    <div
      data-testid="dashboard-trend"
      style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '16px 20px',
        boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
        marginBottom: '20px',
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
        <span style={{ fontWeight: 600, color: '#374151' }}>📈 Practice Trend</span>
        <span style={{ fontSize: '12px', color: '#9ca3af' }}>Last 7 days</span>
      </div>

      <svg width="100%" viewBox={`0 0 ${chartWidth} ${chartHeight + 30}`}>
        {data.map((day, i) => {
          const barHeight = (day.total / maxTotal) * chartHeight
          const completedHeight = (day.completed / maxTotal) * chartHeight
          const x = 10 + i * (barWidth + 4)
          const dayLabel = new Date(day.date).toLocaleDateString('zh-CN', { weekday: 'short' })

          return (
            <g key={day.date}>
              <rect
                x={x}
                y={chartHeight - barHeight}
                width={barWidth}
                height={barHeight}
                fill="#e5e7eb"
                rx={4}
              />
              <rect
                x={x}
                y={chartHeight - completedHeight}
                width={barWidth}
                height={completedHeight}
                fill="#22c55e"
                rx={4}
              />
              {day.total > 0 && (
                <text
                  x={x + barWidth / 2}
                  y={chartHeight - barHeight - 5}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#6b7280"
                >
                  {day.total}
                </text>
              )}
              <text
                x={x + barWidth / 2}
                y={chartHeight + 15}
                textAnchor="middle"
                fontSize="10"
                fill="#9ca3af"
              >
                {dayLabel}
              </text>
            </g>
          )
        })}
      </svg>

      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '16px',
          marginTop: '8px',
          fontSize: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <div
            style={{
              width: '12px',
              height: '12px',
              backgroundColor: '#22c55e',
              borderRadius: '2px',
            }}
          />
          <span style={{ color: '#6b7280' }}>Independent</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <div
            style={{
              width: '12px',
              height: '12px',
              backgroundColor: '#e5e7eb',
              borderRadius: '2px',
            }}
          />
          <span style={{ color: '#6b7280' }}>Total Practice</span>
        </div>
      </div>
    </div>
  )
}
