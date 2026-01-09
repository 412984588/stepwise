import React, { useState } from 'react'
import { useTranslation } from '../i18n'

interface ProblemInputProps {
  onSubmit: (problemText: string) => void
  isLoading?: boolean
  disabled?: boolean
}

export function ProblemInput({ onSubmit, isLoading = false, disabled = false }: ProblemInputProps) {
  const { t } = useTranslation()
  const [problemText, setProblemText] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = problemText.trim()
    if (trimmed && !isLoading && !disabled) {
      onSubmit(trimmed)
    }
  }

  const isValid = problemText.trim().length > 0

  return (
    <form onSubmit={handleSubmit} style={{ width: '100%' }}>
      <div style={{ marginBottom: '16px' }}>
        <label
          htmlFor="problem-input"
          style={{
            display: 'block',
            marginBottom: '8px',
            fontWeight: 600,
            color: '#374151',
          }}
        >
          {t('problemInput.label')}
        </label>
        <textarea
          id="problem-input"
          data-testid="problem-input"
          value={problemText}
          onChange={(e) => setProblemText(e.target.value)}
          placeholder={t('problemInput.placeholder')}
          disabled={isLoading || disabled}
          maxLength={500}
          style={{
            width: '100%',
            minHeight: '100px',
            padding: '12px',
            fontSize: '16px',
            border: '2px solid #e5e7eb',
            borderRadius: '8px',
            resize: 'vertical',
            fontFamily: 'inherit',
            outline: 'none',
            transition: 'border-color 0.2s',
          }}
          onFocus={(e) => (e.target.style.borderColor = '#3b82f6')}
          onBlur={(e) => (e.target.style.borderColor = '#e5e7eb')}
        />
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: '4px',
            fontSize: '12px',
            color: '#6b7280',
          }}
        >
          <span>{t('problemInput.supportedTypes')}</span>
          <span>{problemText.length}/500</span>
        </div>
      </div>
      <button
        type="submit"
        disabled={!isValid || isLoading || disabled}
        style={{
          width: '100%',
          padding: '12px 24px',
          fontSize: '16px',
          fontWeight: 600,
          color: 'white',
          backgroundColor: isValid && !isLoading && !disabled ? '#3b82f6' : '#9ca3af',
          border: 'none',
          borderRadius: '8px',
          cursor: isValid && !isLoading && !disabled ? 'pointer' : 'not-allowed',
          transition: 'background-color 0.2s',
        }}
      >
        {isLoading ? t('problemInput.analyzing') : t('problemInput.submitButton')}
      </button>
    </form>
  )
}
