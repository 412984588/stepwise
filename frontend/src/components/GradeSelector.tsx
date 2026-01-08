import { useTranslation } from '../i18n'

export type GradeLevel = 4 | 5 | 6 | 7 | 8 | 9

interface GradeSelectorProps {
  value: GradeLevel | null
  onChange: (grade: GradeLevel | null) => void
  disabled?: boolean
}

const GRADES: GradeLevel[] = [4, 5, 6, 7, 8, 9]

export function GradeSelector({ value, onChange, disabled = false }: GradeSelectorProps) {
  const { t } = useTranslation()

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value
    onChange(val ? (parseInt(val, 10) as GradeLevel) : null)
  }

  return (
    <div style={{ marginBottom: '16px' }}>
      <label
        htmlFor="grade-select"
        style={{
          display: 'block',
          marginBottom: '8px',
          fontWeight: 600,
          color: '#374151',
        }}
      >
        {t('gradeSelector.label')}
      </label>
      <select
        id="grade-select"
        value={value ?? ''}
        onChange={handleChange}
        disabled={disabled}
        style={{
          width: '100%',
          padding: '12px',
          fontSize: '16px',
          border: '2px solid #e5e7eb',
          borderRadius: '8px',
          backgroundColor: 'white',
          color: value ? '#374151' : '#9ca3af',
          cursor: disabled ? 'not-allowed' : 'pointer',
          outline: 'none',
          transition: 'border-color 0.2s',
        }}
        onFocus={(e) => (e.target.style.borderColor = '#3b82f6')}
        onBlur={(e) => (e.target.style.borderColor = '#e5e7eb')}
      >
        <option value="">{t('gradeSelector.placeholder')}</option>
        {GRADES.map((grade) => (
          <option key={grade} value={grade}>
            {t(`gradeSelector.grades.${grade}`)}
          </option>
        ))}
      </select>
    </div>
  )
}
