import { useTranslation } from '../i18n'
import { Locale } from '../i18n'

interface LocaleSelectorProps {
  value: Locale
  onChange: (locale: Locale) => void
  disabled?: boolean
}

const LOCALES: { value: Locale; label: string }[] = [
  { value: 'en-US', label: 'English (US)' },
  { value: 'zh-CN', label: '中文 (简体)' },
]

export function LocaleSelector({ value, onChange, disabled = false }: LocaleSelectorProps) {
  const { t } = useTranslation()

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange(e.target.value as Locale)
  }

  return (
    <div style={{ marginBottom: '16px' }}>
      <label
        htmlFor="locale-select"
        style={{
          display: 'block',
          marginBottom: '8px',
          fontWeight: 600,
          color: '#374151',
        }}
      >
        {t('localeSelector.label')}
      </label>
      <select
        id="locale-select"
        value={value}
        onChange={handleChange}
        disabled={disabled}
        style={{
          width: '100%',
          padding: '12px',
          fontSize: '16px',
          border: '2px solid #e5e7eb',
          borderRadius: '8px',
          backgroundColor: 'white',
          color: '#374151',
          cursor: disabled ? 'not-allowed' : 'pointer',
          outline: 'none',
          transition: 'border-color 0.2s',
        }}
        onFocus={(e) => (e.target.style.borderColor = '#3b82f6')}
        onBlur={(e) => (e.target.style.borderColor = '#e5e7eb')}
      >
        {LOCALES.map((loc) => (
          <option key={loc.value} value={loc.value}>
            {loc.label}
          </option>
        ))}
      </select>
    </div>
  )
}
