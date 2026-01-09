import React, { useState } from 'react'

export interface BetaGateModalProps {
  isOpen: boolean
  onSubmit: (code: string) => void
  error?: string | null
  isLoading?: boolean
}

export function BetaGateModal({ isOpen, onSubmit, error, isLoading = false }: BetaGateModalProps) {
  const [code, setCode] = useState('')

  if (!isOpen) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (code.trim()) {
      onSubmit(code.trim())
    }
  }

  return (
    <div
      data-testid="beta-gate-modal"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
    >
      <div
        style={{
          backgroundColor: 'white',
          padding: '32px',
          borderRadius: '12px',
          maxWidth: '400px',
          width: '90%',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        }}
      >
        <h2
          style={{
            fontSize: '24px',
            fontWeight: 700,
            color: '#1f2937',
            marginBottom: '8px',
            textAlign: 'center',
          }}
        >
          Private Beta Access
        </h2>

        <p
          style={{
            color: '#6b7280',
            fontSize: '14px',
            textAlign: 'center',
            marginBottom: '24px',
          }}
        >
          StepWise is currently in private beta for US families. Please enter your beta access code
          to continue.
        </p>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <label
              htmlFor="beta-code"
              style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: 500,
                color: '#374151',
                marginBottom: '6px',
              }}
            >
              Beta Access Code
            </label>
            <input
              id="beta-code"
              data-testid="beta-code-input"
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Enter your code"
              disabled={isLoading}
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '16px',
                border: error ? '2px solid #ef4444' : '1px solid #d1d5db',
                borderRadius: '8px',
                outline: 'none',
                boxSizing: 'border-box',
              }}
            />
            {error && (
              <p
                data-testid="beta-code-error"
                style={{
                  color: '#ef4444',
                  fontSize: '13px',
                  marginTop: '6px',
                }}
              >
                {error}
              </p>
            )}
          </div>

          <button
            type="submit"
            data-testid="beta-code-submit"
            disabled={!code.trim() || isLoading}
            style={{
              width: '100%',
              padding: '12px',
              fontSize: '16px',
              fontWeight: 600,
              color: 'white',
              backgroundColor: !code.trim() || isLoading ? '#9ca3af' : '#2563eb',
              border: 'none',
              borderRadius: '8px',
              cursor: !code.trim() || isLoading ? 'not-allowed' : 'pointer',
            }}
          >
            {isLoading ? 'Verifying...' : 'Enter Beta'}
          </button>
        </form>

        <p
          style={{
            marginTop: '20px',
            fontSize: '12px',
            color: '#9ca3af',
            textAlign: 'center',
          }}
        >
          Don't have a code?{' '}
          <a
            href="mailto:beta@stepwise.app?subject=Beta%20Access%20Request"
            style={{ color: '#2563eb', textDecoration: 'none' }}
          >
            Request access
          </a>
        </p>
      </div>
    </div>
  )
}
