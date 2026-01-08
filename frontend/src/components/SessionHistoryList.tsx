import { SessionListItem } from '../services/sessionApi'

interface SessionHistoryListProps {
  sessions: SessionListItem[]
}

const STATUS_LABELS: Record<string, string> = {
  active: '进行中',
  completed: '已完成',
  revealed: '查看解答',
  abandoned: '已放弃',
  paused: '已暂停',
}

const LAYER_LABELS: Record<string, string> = {
  concept: '概念',
  strategy: '策略',
  step: '步骤',
  completed: '完成',
  revealed: '解答',
}

const STATUS_COLORS: Record<string, string> = {
  active: '#3b82f6',
  completed: '#22c55e',
  revealed: '#f59e0b',
  abandoned: '#6b7280',
  paused: '#6b7280',
}

export function SessionHistoryList({ sessions }: SessionHistoryListProps) {
  if (sessions.length === 0) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#9ca3af' }}>
        还没有练习记录，开始做题吧！
      </div>
    )
  }

  return (
    <div>
      {sessions.map((session) => (
        <div
          key={session.session_id}
          style={{
            padding: '16px 20px',
            borderBottom: '1px solid #f3f4f6',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                fontSize: '15px',
                color: '#1f2937',
                marginBottom: '4px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {session.problem_text}
            </div>
            <div style={{ fontSize: '13px', color: '#9ca3af' }}>
              {formatDate(session.started_at)} · 到达
              {LAYER_LABELS[session.final_layer.toLowerCase()] || session.final_layer}层
              {session.confusion_count > 0 && ` · 困惑${session.confusion_count}次`}
            </div>
          </div>
          <div
            style={{
              padding: '4px 12px',
              fontSize: '12px',
              fontWeight: 500,
              color: STATUS_COLORS[session.status.toLowerCase()] || '#6b7280',
              backgroundColor: `${STATUS_COLORS[session.status.toLowerCase()] || '#6b7280'}15`,
              borderRadius: '12px',
              flexShrink: 0,
              marginLeft: '12px',
            }}
          >
            {STATUS_LABELS[session.status.toLowerCase()] || session.status}
          </div>
        </div>
      ))}
    </div>
  )
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`

  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
