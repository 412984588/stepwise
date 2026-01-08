import { useTranslation } from '../i18n'

interface UpgradeModalProps {
  isOpen: boolean
  onClose: () => void
  onSelectTier: (tier: 'pro' | 'family') => void
  currentTier: 'free' | 'pro' | 'family'
}

interface PlanInfo {
  tier: 'free' | 'pro' | 'family'
  price: string
  features: string[]
  color: string
}

const plans: PlanInfo[] = [
  {
    tier: 'free',
    price: '$0',
    features: ['billing.features.freeProblems', 'billing.features.basicHints'],
    color: '#6b7280',
  },
  {
    tier: 'pro',
    price: '$9.99',
    features: [
      'billing.features.unlimitedProblems',
      'billing.features.allHints',
      'billing.features.dashboard',
    ],
    color: '#3b82f6',
  },
  {
    tier: 'family',
    price: '$19.99',
    features: [
      'billing.features.everythingPro',
      'billing.features.fiveProfiles',
    ],
    color: '#7c3aed',
  },
]

export function UpgradeModal({
  isOpen,
  onClose,
  onSelectTier,
  currentTier,
}: UpgradeModalProps) {
  const { t } = useTranslation()

  if (!isOpen) return null

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '32px',
          maxWidth: '800px',
          width: '90%',
          maxHeight: '90vh',
          overflow: 'auto',
          position: 'relative',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: 'none',
            border: 'none',
            fontSize: '24px',
            cursor: 'pointer',
            color: '#9ca3af',
            padding: '4px',
            lineHeight: 1,
          }}
        >
          ×
        </button>

        <h2
          style={{
            fontSize: '24px',
            fontWeight: 700,
            color: '#1f2937',
            marginBottom: '24px',
            textAlign: 'center',
          }}
        >
          {t('billing.modal.title')}
        </h2>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '20px',
          }}
        >
          {plans.map((plan) => {
            const isCurrent = plan.tier === currentTier
            const isUpgrade = plan.tier !== 'free'

            return (
              <div
                key={plan.tier}
                style={{
                  border: isCurrent ? `2px solid ${plan.color}` : '1px solid #e5e7eb',
                  borderRadius: '12px',
                  padding: '24px',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'box-shadow 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = 'none'
                }}
              >
                <div
                  style={{
                    fontSize: '14px',
                    fontWeight: 600,
                    color: plan.color,
                    textTransform: 'uppercase',
                    marginBottom: '8px',
                  }}
                >
                  {t(`billing.tiers.${plan.tier}`)}
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <span style={{ fontSize: '32px', fontWeight: 700, color: '#1f2937' }}>
                    {plan.price}
                  </span>
                  <span style={{ fontSize: '14px', color: '#6b7280' }}>
                    {t('billing.perMonth')}
                  </span>
                </div>

                <ul style={{ listStyle: 'none', padding: 0, margin: 0, flex: 1 }}>
                  {plan.features.map((featureKey) => (
                    <li
                      key={featureKey}
                      style={{
                        fontSize: '14px',
                        color: '#4b5563',
                        marginBottom: '8px',
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '8px',
                      }}
                    >
                      <span style={{ color: '#10b981' }}>✓</span>
                      {t(featureKey)}
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => isUpgrade && onSelectTier(plan.tier as 'pro' | 'family')}
                  disabled={isCurrent || !isUpgrade}
                  style={{
                    marginTop: '16px',
                    padding: '12px 24px',
                    fontSize: '14px',
                    fontWeight: 600,
                    color: isCurrent ? plan.color : 'white',
                    backgroundColor: isCurrent ? 'transparent' : isUpgrade ? plan.color : '#e5e7eb',
                    border: isCurrent ? `2px solid ${plan.color}` : 'none',
                    borderRadius: '8px',
                    cursor: isCurrent || !isUpgrade ? 'default' : 'pointer',
                    transition: 'opacity 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    if (!isCurrent && isUpgrade) e.currentTarget.style.opacity = '0.9'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.opacity = '1'
                  }}
                >
                  {isCurrent ? t('billing.currentPlan') : t('billing.selectPlan')}
                </button>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
