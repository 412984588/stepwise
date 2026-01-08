import { GoalProgress as GoalProgressData } from '../services/sessionApi';
import { useTranslation } from '../i18n';

interface GoalProgressProps {
  data: GoalProgressData;
}

export function GoalProgress({ data }: GoalProgressProps) {
  const { t } = useTranslation();
  return (
    <div
      style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '16px 20px',
        boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
        marginBottom: '20px',
      }}
    >
      <div style={{ fontWeight: 600, color: '#374151', marginBottom: '16px' }}>
        🎯 {t('dashboard.goals.title')}
      </div>

      <div style={{ display: 'flex', gap: '20px' }}>
        <ProgressRing
          label={t('dashboard.goals.daily')}
          completed={data.daily_completed}
          target={data.daily_target}
          progress={data.daily_progress}
          color="#3b82f6"
          achievedText={t('dashboard.goals.achieved')}
        />
        <ProgressRing
          label={t('dashboard.goals.weekly')}
          completed={data.weekly_completed}
          target={data.weekly_target}
          progress={data.weekly_progress}
          color="#8b5cf6"
          achievedText={t('dashboard.goals.achieved')}
        />
      </div>
    </div>
  );
}

interface ProgressRingProps {
  label: string;
  completed: number;
  target: number;
  progress: number;
  color: string;
  achievedText: string;
}

function ProgressRing({ label, completed, target, progress, color, achievedText }: ProgressRingProps) {
  const size = 80;
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div style={{ flex: 1, textAlign: 'center' }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.5s ease' }}
        />
      </svg>
      <div
        style={{
          marginTop: '-60px',
          position: 'relative',
          fontSize: '18px',
          fontWeight: 700,
          color: color,
        }}
      >
        {completed}/{target}
      </div>
      <div style={{ marginTop: '28px', fontSize: '13px', color: '#6b7280' }}>{label}</div>
      {progress >= 100 && (
        <div style={{ fontSize: '12px', color: '#22c55e', marginTop: '4px' }}>
          ✅ {achievedText}
        </div>
      )}
    </div>
  );
}
