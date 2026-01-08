import { useState, useEffect } from 'react';
import {
  getDashboard,
  getTrendData,
  getGoalProgress,
  DashboardData,
  TrendData,
  GoalProgress as GoalProgressData,
} from '../services/sessionApi';
import { SessionHistoryList } from './SessionHistoryList';
import { TrendChart } from './TrendChart';
import { GoalProgress } from './GoalProgress';
import { useTranslation } from '../i18n';

interface DashboardProps {
  onBack: () => void
}

export function Dashboard({ onBack }: DashboardProps) {
  const { t } = useTranslation()
  const [data, setData] = useState<DashboardData | null>(null)
  const [trendData, setTrendData] = useState<TrendData | null>(null)
  const [goalData, setGoalData] = useState<GoalProgressData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true)
        const [dashboardData, trend, goals] = await Promise.all([
          getDashboard(),
          getTrendData(7),
          getGoalProgress(3, 15),
        ])
        setData(dashboardData)
        setTrendData(trend)
        setGoalData(goals)
      } catch (err) {
        setError(t('errors.loadingFailed'))
      } finally {
        setIsLoading(false)
      }
    }
    loadData()
  }, [t])

  if (isLoading) {
    return <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>{t('dashboard.encouragement.loading')}</div>
  }

  if (error) {
    return <div style={{ textAlign: 'center', padding: '40px', color: '#ef4444' }}>{error}</div>
  }

  if (!data) return null

  return (
    <div>
      <div
        style={{
          marginBottom: '16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h2 style={{ margin: 0, fontSize: '24px', fontWeight: 600, color: '#1f2937' }}>{t('dashboard.title')}</h2>
        <button
          onClick={onBack}
          style={{
            padding: '8px 16px',
            fontSize: '14px',
            color: '#3b82f6',
            backgroundColor: 'white',
            border: '1px solid #3b82f6',
            borderRadius: '8px',
            cursor: 'pointer',
          }}
        >
          {t('dashboard.backButton')}
        </button>
      </div>

      <div
        style={{
          backgroundColor: '#eff6ff',
          padding: '16px 20px',
          borderRadius: '12px',
          marginBottom: '20px',
          borderLeft: '4px solid #3b82f6',
        }}
      >
        <p style={{ margin: '0 0 4px 0', fontSize: '16px', color: '#1e40af', fontWeight: 500 }}>
          👋 {data.encouragement.streak_message}
        </p>
        <p style={{ margin: 0, fontSize: '14px', color: '#3b82f6' }}>
          {data.encouragement.performance_message}
        </p>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '12px',
          marginBottom: '20px',
        }}
      >
        <StatCard
          icon="📅"
          label={t('dashboard.stats.learningDays')}
          value={`${data.total_learning_days} ${t('dashboard.stats.days')}`}
          color="#3b82f6"
        />
        <StatCard
          icon="✅"
          label={t('dashboard.stats.completionRate')}
          value={`${data.independent_completion_rate}%`}
          color="#22c55e"
        />
        <StatCard
          icon="📊"
          label={t('dashboard.stats.weeklyPractice')}
          value={`${data.sessions_this_week} ${t('dashboard.stats.problems')}`}
          color="#8b5cf6"
        />
        <StatCard icon="🔥" label={t('dashboard.stats.streak')} value={`${data.learning_streak} ${t('dashboard.stats.days')}`} color="#f59e0b" />
      </div>

      {goalData && <GoalProgress data={goalData} />}

      {trendData && trendData.daily_stats.length > 0 && (
        <TrendChart data={trendData.daily_stats} />
      )}

      {data.problem_type_stats.length > 0 && (
        <div
          style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
            marginBottom: '20px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              padding: '16px 20px',
              borderBottom: '1px solid #e5e7eb',
              fontWeight: 600,
              color: '#374151',
            }}
          >
            📈 {t('dashboard.problemTypes')}
          </div>
          <div style={{ padding: '16px 20px' }}>
            {data.problem_type_stats.map((stat) => (
              <ProblemTypeBar key={stat.type} stat={stat} />
            ))}
          </div>
        </div>
      )}

      <div
        style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            padding: '16px 20px',
            borderBottom: '1px solid #e5e7eb',
            fontWeight: 600,
            color: '#374151',
          }}
        >
            📜 {t('dashboard.recentSessions')}
          </div>
        <SessionHistoryList sessions={data.recent_sessions} />
      </div>
    </div>
  )
}

interface StatCardProps {
  icon: string
  label: string
  value: string
  color: string
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  return (
    <div
      style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '16px',
        boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
        borderLeft: `4px solid ${color}`,
      }}
    >
      <div style={{ fontSize: '20px', marginBottom: '4px' }}>{icon}</div>
      <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>{label}</div>
      <div style={{ fontSize: '24px', fontWeight: 700, color: color }}>{value}</div>
    </div>
  )
}

interface ProblemTypeBarProps {
  stat: {
    label: string
    total: number
    completed: number
    completion_rate: number
  }
}

function ProblemTypeBar({ stat }: ProblemTypeBarProps) {
  const barColor =
    stat.completion_rate >= 70 ? '#22c55e' : stat.completion_rate >= 40 ? '#f59e0b' : '#ef4444'

  return (
    <div style={{ marginBottom: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
        <span style={{ fontSize: '14px', color: '#374151' }}>{stat.label}</span>
        <span style={{ fontSize: '14px', color: '#6b7280' }}>
          {stat.completion_rate}% ({stat.completed}/{stat.total})
        </span>
      </div>
      <div
        style={{
          height: '8px',
          backgroundColor: '#e5e7eb',
          borderRadius: '4px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${stat.completion_rate}%`,
            backgroundColor: barColor,
            borderRadius: '4px',
            transition: 'width 0.3s ease',
          }}
        />
      </div>
    </div>
  )
}
