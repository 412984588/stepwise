import { useState } from 'react'

interface FeedbackModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

type PMFAnswer = 'very_disappointed' | 'somewhat_disappointed' | 'not_disappointed' | ''
type WouldPayAnswer =
  | 'yes_definitely'
  | 'yes_probably'
  | 'not_sure'
  | 'probably_not'
  | 'definitely_not'
  | ''
type GradeLevel = 'grade_4' | 'grade_5' | 'grade_6' | 'grade_7' | 'grade_8' | 'grade_9' | ''

interface FeedbackFormData {
  pmfAnswer: PMFAnswer
  whatWorked: string
  whatConfused: string
  wouldPay: WouldPayAnswer
  gradeLevel: GradeLevel
  email: string
  consent: boolean
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export function FeedbackModal({ isOpen, onClose, onSuccess }: FeedbackModalProps) {
  const [formData, setFormData] = useState<FeedbackFormData>({
    pmfAnswer: '',
    whatWorked: '',
    whatConfused: '',
    wouldPay: '',
    gradeLevel: '',
    email: '',
    consent: false,
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const isEmailValid = !formData.email || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)
  const canSubmit =
    formData.pmfAnswer &&
    formData.gradeLevel &&
    isEmailValid &&
    (!formData.email || formData.consent)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!canSubmit) return

    setIsSubmitting(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pmf_answer: formData.pmfAnswer,
          what_worked: formData.whatWorked || null,
          what_confused: formData.whatConfused || null,
          would_pay: formData.wouldPay || null,
          grade_level: formData.gradeLevel,
          email: formData.email || null,
          locale: navigator.language || 'en-US',
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to submit feedback')
      }

      onSuccess()
      onClose()
      setFormData({
        pmfAnswer: '',
        whatWorked: '',
        whatConfused: '',
        wouldPay: '',
        gradeLevel: '',
        email: '',
        consent: false,
      })
    } catch {
      setError('Failed to submit feedback. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const radioStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 12px',
    border: '1px solid #e5e7eb',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
  }

  const selectedRadioStyle = {
    ...radioStyle,
    borderColor: '#3b82f6',
    backgroundColor: '#eff6ff',
  }

  return (
    <div
      data-testid="feedback-modal"
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '20px',
      }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          maxWidth: '500px',
          width: '100%',
          maxHeight: '90vh',
          overflow: 'auto',
          boxShadow: '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        }}
      >
        <div style={{ padding: '24px', borderBottom: '1px solid #e5e7eb' }}>
          <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 600, color: '#1f2937' }}>
            Share Your Feedback
          </h2>
          <p style={{ margin: '8px 0 0', fontSize: '14px', color: '#6b7280' }}>
            Help us improve StepWise for families like yours.
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: '24px' }}>
          {error && (
            <div
              style={{
                padding: '12px',
                backgroundColor: '#fef2f2',
                borderRadius: '6px',
                marginBottom: '16px',
                color: '#dc2626',
                fontSize: '14px',
              }}
            >
              {error}
            </div>
          )}

          {/* PMF Question */}
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 500,
                fontSize: '14px',
                color: '#374151',
              }}
            >
              How would you feel if you could no longer use StepWise? *
            </label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {[
                { value: 'very_disappointed', label: 'Very disappointed' },
                { value: 'somewhat_disappointed', label: 'Somewhat disappointed' },
                { value: 'not_disappointed', label: 'Not disappointed' },
              ].map((option) => (
                <label
                  key={option.value}
                  style={formData.pmfAnswer === option.value ? selectedRadioStyle : radioStyle}
                >
                  <input
                    type="radio"
                    name="pmfAnswer"
                    value={option.value}
                    checked={formData.pmfAnswer === option.value}
                    onChange={(e) =>
                      setFormData({ ...formData, pmfAnswer: e.target.value as PMFAnswer })
                    }
                    data-testid={`pmf-${option.value}`}
                  />
                  {option.label}
                </label>
              ))}
            </div>
          </div>

          {/* What Worked */}
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 500,
                fontSize: '14px',
                color: '#374151',
              }}
            >
              What did you find most valuable?
            </label>
            <textarea
              value={formData.whatWorked}
              onChange={(e) =>
                setFormData({ ...formData, whatWorked: e.target.value.slice(0, 500) })
              }
              placeholder="What worked well for your family..."
              maxLength={500}
              data-testid="what-worked"
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px',
                resize: 'vertical',
                minHeight: '80px',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {/* What Was Confusing */}
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 500,
                fontSize: '14px',
                color: '#374151',
              }}
            >
              What was confusing or frustrating?
            </label>
            <textarea
              value={formData.whatConfused}
              onChange={(e) =>
                setFormData({ ...formData, whatConfused: e.target.value.slice(0, 500) })
              }
              placeholder="What could we improve..."
              maxLength={500}
              data-testid="what-confused"
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px',
                resize: 'vertical',
                minHeight: '80px',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {/* Would You Pay */}
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 500,
                fontSize: '14px',
                color: '#374151',
              }}
            >
              Would you pay for StepWise?
            </label>
            <select
              value={formData.wouldPay}
              onChange={(e) =>
                setFormData({ ...formData, wouldPay: e.target.value as WouldPayAnswer })
              }
              data-testid="would-pay"
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px',
                backgroundColor: 'white',
              }}
            >
              <option value="">Select an option</option>
              <option value="yes_definitely">Yes, definitely</option>
              <option value="yes_probably">Yes, probably</option>
              <option value="not_sure">Not sure</option>
              <option value="probably_not">Probably not</option>
              <option value="definitely_not">Definitely not</option>
            </select>
          </div>

          {/* Grade Level */}
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 500,
                fontSize: '14px',
                color: '#374151',
              }}
            >
              What grade is your child in? *
            </label>
            <select
              value={formData.gradeLevel}
              onChange={(e) =>
                setFormData({ ...formData, gradeLevel: e.target.value as GradeLevel })
              }
              data-testid="grade-level"
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px',
                backgroundColor: 'white',
              }}
            >
              <option value="">Select grade</option>
              <option value="grade_4">Grade 4</option>
              <option value="grade_5">Grade 5</option>
              <option value="grade_6">Grade 6</option>
              <option value="grade_7">Grade 7</option>
              <option value="grade_8">Grade 8</option>
              <option value="grade_9">Grade 9</option>
            </select>
          </div>

          {/* Email */}
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 500,
                fontSize: '14px',
                color: '#374151',
              }}
            >
              Your email (optional)
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="parent@example.com"
              data-testid="feedback-email"
              style={{
                width: '100%',
                padding: '10px 12px',
                border: `1px solid ${!isEmailValid ? '#dc2626' : '#d1d5db'}`,
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box',
              }}
            />
            {!isEmailValid && (
              <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#dc2626' }}>
                Please enter a valid email address
              </p>
            )}
          </div>

          {/* Consent */}
          {formData.email && (
            <div style={{ marginBottom: '20px' }}>
              <label
                style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', cursor: 'pointer' }}
              >
                <input
                  type="checkbox"
                  checked={formData.consent}
                  onChange={(e) => setFormData({ ...formData, consent: e.target.checked })}
                  data-testid="consent-checkbox"
                  style={{ marginTop: '3px' }}
                />
                <span style={{ fontSize: '13px', color: '#6b7280' }}>
                  I agree that StepWise may contact me about my feedback. My email will only be used
                  for product research and will not be shared or used for marketing.
                </span>
              </label>
            </div>
          )}

          {/* Buttons */}
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '10px 20px',
                fontSize: '14px',
                fontWeight: 500,
                color: '#374151',
                backgroundColor: '#f3f4f6',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!canSubmit || isSubmitting}
              data-testid="submit-feedback"
              style={{
                padding: '10px 20px',
                fontSize: '14px',
                fontWeight: 500,
                color: 'white',
                backgroundColor: canSubmit && !isSubmitting ? '#3b82f6' : '#9ca3af',
                border: 'none',
                borderRadius: '6px',
                cursor: canSubmit && !isSubmitting ? 'pointer' : 'not-allowed',
              }}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
