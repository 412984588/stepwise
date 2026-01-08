import React, { useState } from 'react'
import { HintLayer } from '../types/enums'
import { useTranslation } from '../i18n'

interface HintDialogProps {
  problemText: string
  currentLayer: HintLayer
  hintContent: string
  onRespond: (responseText: string) => void
  onCancel: () => void
  onReveal?: () => void
  onComplete?: () => void
  isLoading?: boolean
  confusionCount?: number
  isDowngrade?: boolean
  canReveal?: boolean
}

const MIN_RESPONSE_LENGTH = 10

const LAYER_KEYS: Record<HintLayer, string> = {
  [HintLayer.CONCEPT]: 'hintDialog.layers.concept',
  [HintLayer.STRATEGY]: 'hintDialog.layers.strategy',
  [HintLayer.STEP]: 'hintDialog.layers.step',
  [HintLayer.COMPLETED]: 'hintDialog.layers.completed',
  [HintLayer.REVEALED]: 'hintDialog.layers.revealed',
}

const LAYER_COLORS: Record<HintLayer, string> = {
  [HintLayer.CONCEPT]: '#3b82f6',
  [HintLayer.STRATEGY]: '#8b5cf6',
  [HintLayer.STEP]: '#10b981',
  [HintLayer.COMPLETED]: '#22c55e',
  [HintLayer.REVEALED]: '#f59e0b',
}

export function HintDialog({
  problemText,
  currentLayer,
  hintContent,
  onRespond,
  onCancel,
  onReveal,
  onComplete,
  isLoading = false,
  confusionCount = 0,
  isDowngrade = false,
  canReveal = false,
}: HintDialogProps) {
  const { t } = useTranslation()
  const [responseText, setResponseText] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (isResponseValid && !isLoading) {
      onRespond(responseText.trim())
      setResponseText('')
    }
  }

  const charCount = responseText.trim().length
  const isResponseValid = charCount >= MIN_RESPONSE_LENGTH
  const charsNeeded = MIN_RESPONSE_LENGTH - charCount

  return (
    <div
      style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        overflow: 'hidden',
        width: '100%',
        maxWidth: '600px',
      }}
    >
      <div
        style={{
          backgroundColor: LAYER_COLORS[currentLayer],
          color: 'white',
          padding: '16px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <span id="hint-layer-label" style={{ fontWeight: 600 }} data-test-id="hint-layer-label">{t(LAYER_KEYS[currentLayer])}</span>
        <div style={{ display: 'flex', gap: '8px' }}>
          {[HintLayer.CONCEPT, HintLayer.STRATEGY, HintLayer.STEP].map((layer, idx) => (
            <div
              key={layer}
              style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor:
                  currentLayer === layer
                    ? 'white'
                    : idx <
                        [HintLayer.CONCEPT, HintLayer.STRATEGY, HintLayer.STEP].indexOf(
                          currentLayer
                        )
                      ? 'rgba(255,255,255,0.7)'
                      : 'rgba(255,255,255,0.3)',
                color: currentLayer === layer ? LAYER_COLORS[currentLayer] : 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px',
                fontWeight: 600,
              }}
            >
              {idx + 1}
            </div>
          ))}
        </div>
      </div>

      <div style={{ padding: '20px' }}>
        <div
          style={{
            backgroundColor: '#f3f4f6',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '16px',
            fontSize: '14px',
            color: '#4b5563',
          }}
        >
          <strong>{t('hintDialog.problem')}</strong>
          {problemText}
        </div>

        <div
          style={{
            backgroundColor: '#eff6ff',
            padding: '16px',
            borderRadius: '8px',
            marginBottom: '20px',
            borderLeft: `4px solid ${LAYER_COLORS[currentLayer]}`,
          }}
        >
          <p style={{ margin: 0, lineHeight: 1.6, color: '#1e40af' }} data-test-id="hint-content">{hintContent}</p>
        </div>

        {isDowngrade && (
          <div
            style={{
              backgroundColor: '#dbeafe',
              padding: '12px 16px',
              borderRadius: '6px',
              marginBottom: '16px',
              fontSize: '14px',
              color: '#1e40af',
              borderLeft: '4px solid #3b82f6',
            }}
          >
            🌟 {t('hintDialog.downgradeMessage')}
          </div>
        )}

        {!isDowngrade && confusionCount > 0 && confusionCount < 3 && (
          <div
            style={{
              backgroundColor: '#fef3c7',
              padding: '8px 12px',
              borderRadius: '6px',
              marginBottom: '16px',
              fontSize: '13px',
              color: '#92400e',
            }}
          >
            💡 {t('hintDialog.confusionMessage')} ({confusionCount}/3)
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '12px' }}>
            <label
              htmlFor="response-input"
              style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 500,
                color: '#374151',
              }}
            >
              {t('hintDialog.responseLabel')}
            </label>
            <textarea
              id="response-input"
              data-test-id="response-input"
              value={responseText}
              onChange={(e) => setResponseText(e.target.value)}
              placeholder={t('hintDialog.responsePlaceholder')}
              disabled={isLoading}
              style={{
                width: '100%',
                minHeight: '80px',
                padding: '12px',
                fontSize: '15px',
                border: `2px solid ${isResponseValid ? '#10b981' : '#e5e7eb'}`,
                borderRadius: '8px',
                resize: 'vertical',
                fontFamily: 'inherit',
                outline: 'none',
                transition: 'border-color 0.2s',
              }}
            />
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginTop: '4px',
                fontSize: '12px',
                color: isResponseValid ? '#10b981' : '#6b7280',
              }}
            >
              <span>{isResponseValid ? `✓ ${t('hintDialog.readyToSubmit')}` : t('hintDialog.charsNeeded', { count: charsNeeded })}</span>
              <span>{t('hintDialog.charCount', { count: charCount })}</span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              type="button"
              data-test-id="cancel-button"
              onClick={onCancel}
              disabled={isLoading}
              style={{
                flex: 1,
                padding: '10px 16px',
                fontSize: '14px',
                color: '#6b7280',
                backgroundColor: '#f3f4f6',
                border: 'none',
                borderRadius: '8px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
              }}
            >
              {t('hintDialog.cancelButton')}
            </button>
            <button
              type="submit"
              data-test-id="submit-button"
              disabled={!isResponseValid || isLoading}
              style={{
                flex: 2,
                padding: '10px 16px',
                fontSize: '14px',
                fontWeight: 600,
                color: 'white',
                backgroundColor: isResponseValid && !isLoading ? '#3b82f6' : '#9ca3af',
                border: 'none',
                borderRadius: '8px',
                cursor: isResponseValid && !isLoading ? 'pointer' : 'not-allowed',
              }}
            >
              {isLoading ? t('hintDialog.processing') : t('hintDialog.submitButton')}
            </button>
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
            <button
              type="button"
              data-test-id="reveal-button"
              onClick={onReveal}
              disabled={!canReveal || isLoading}
              style={{
                flex: 1,
                padding: '10px 16px',
                fontSize: '14px',
                fontWeight: 500,
                color: canReveal && !isLoading ? '#f59e0b' : '#9ca3af',
                backgroundColor: canReveal && !isLoading ? '#fef3c7' : '#f3f4f6',
                border: canReveal && !isLoading ? '1px solid #f59e0b' : '1px solid #e5e7eb',
                borderRadius: '8px',
                cursor: canReveal && !isLoading ? 'pointer' : 'not-allowed',
              }}
            >
              {t('hintDialog.revealButton')}
            </button>
            <button
              type="button"
              data-test-id="complete-button"
              onClick={onComplete}
              disabled={currentLayer !== HintLayer.STEP || isLoading}
              style={{
                flex: 1,
                padding: '10px 16px',
                fontSize: '14px',
                fontWeight: 500,
                color: currentLayer === HintLayer.STEP && !isLoading ? '#22c55e' : '#9ca3af',
                backgroundColor:
                  currentLayer === HintLayer.STEP && !isLoading ? '#dcfce7' : '#f3f4f6',
                border:
                  currentLayer === HintLayer.STEP && !isLoading
                    ? '1px solid #22c55e'
                    : '1px solid #e5e7eb',
                borderRadius: '8px',
                cursor: currentLayer === HintLayer.STEP && !isLoading ? 'pointer' : 'not-allowed',
              }}
            >
              {t('hintDialog.completeButton')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
