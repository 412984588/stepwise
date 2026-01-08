import { useTranslation } from '../i18n'

interface SubscriptionBannerProps {
  tier: 'free' | 'pro' | 'family'
  used: number
  limit: number | null
  onUpgradeClick: () => void
}

const tierColors: Record<string, { bg: string; text: string }> = {
  free: { bg: '#f3f4f6', text: '#6b7280' },
  pro: { bg: '#dbeafe', text: '#1d4ed8' },
  family: { bg: '#f3e8ff', text: '#7c3aed' },
}

export function SubscriptionBanner({ tier, used, limit, onUpgradeClick }: SubscriptionBannerProps) {
  const { t } = useTranslation()
  const colors = tierColors[tier] || tierColors.free
  const progress = limit ? Math.min((used / limit) * 100, 100) : 0

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 16px',
        backgroundColor: 'white',
        borderRadius: '8px',
        marginBottom: '16px',
        boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span
          style={{
            padding: '4px 10px',
            borderRadius: '12px',
            fontSize: '12px',
            fontWeight: 600,
            backgroundColor: colors.bg,
            color: colors.text,
            textTransform: 'uppercase',
          }}
        >
          {t(`billing.tiers.${tier}`)}
        </span>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <span style={{ fontSize: '14px', color: '#374151' }}>
            {limit
              ? t('billing.usage.limited', { used: String(used), limit: String(limit) })
              : t('billing.usage.unlimited')}
          </span>

          {limit && (
            <div
              style={{
                width: '120px',
                height: '4px',
                backgroundColor: '#e5e7eb',
                borderRadius: '2px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${progress}%`,
                  height: '100%',
                  backgroundColor: progress >= 100 ? '#ef4444' : '#3b82f6',
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
          )}
        </div>
      </div>

      {tier === 'free' && (
        <button
          onClick={onUpgradeClick}
          style={{
            padding: '8px 16px',
            fontSize: '14px',
            fontWeight: 600,
            color: 'white',
            backgroundColor: '#3b82f6',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            transition: 'background-color 0.2s',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#2563eb')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#3b82f6')}
        >
          {t('billing.upgradeButton')}
        </button>
      )}
    </div>
  )
}
