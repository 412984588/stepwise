import { SolutionStep } from '../services/sessionApi'

interface SolutionViewerProps {
  steps: SolutionStep[]
  finalAnswer: string
  explanation: string | null
  onNewProblem: () => void
}

export function SolutionViewer({
  steps,
  finalAnswer,
  explanation,
  onNewProblem,
}: SolutionViewerProps) {
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
          backgroundColor: '#f59e0b',
          color: 'white',
          padding: '16px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <span style={{ fontWeight: 600 }}>完整解答</span>
        <span style={{ fontSize: '14px' }}>📖</span>
      </div>

      <div style={{ padding: '20px' }}>
        <div
          style={{
            backgroundColor: '#fef3c7',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '20px',
            fontSize: '14px',
            color: '#92400e',
          }}
        >
          💡 这是完整的解题步骤，希望对你有帮助！
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h3
            style={{
              fontSize: '16px',
              fontWeight: 600,
              color: '#374151',
              marginBottom: '12px',
            }}
          >
            解题步骤
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {steps.map((step, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  gap: '12px',
                  padding: '12px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '8px',
                  borderLeft: '4px solid #3b82f6',
                }}
              >
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    fontWeight: 600,
                    flexShrink: 0,
                  }}
                >
                  {index + 1}
                </div>
                <div style={{ flex: 1 }}>
                  <p style={{ margin: '0 0 4px 0', color: '#4b5563' }}>{step.description}</p>
                  <p
                    style={{
                      margin: 0,
                      fontWeight: 600,
                      color: '#1f2937',
                      fontFamily: 'monospace',
                    }}
                  >
                    {step.result}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div
          style={{
            backgroundColor: '#dcfce7',
            padding: '16px',
            borderRadius: '8px',
            marginBottom: '16px',
            borderLeft: '4px solid #22c55e',
          }}
        >
          <p
            style={{
              margin: '0 0 4px 0',
              fontSize: '14px',
              color: '#166534',
              fontWeight: 500,
            }}
          >
            最终答案
          </p>
          <p
            style={{
              margin: 0,
              fontSize: '20px',
              fontWeight: 700,
              color: '#15803d',
              fontFamily: 'monospace',
            }}
          >
            {finalAnswer}
          </p>
        </div>

        {explanation && (
          <div
            style={{
              backgroundColor: '#eff6ff',
              padding: '12px 16px',
              borderRadius: '8px',
              marginBottom: '20px',
            }}
          >
            <p style={{ margin: 0, color: '#1e40af', fontSize: '14px' }}>{explanation}</p>
          </div>
        )}

        <button
          onClick={onNewProblem}
          style={{
            width: '100%',
            padding: '12px 24px',
            fontSize: '16px',
            fontWeight: 600,
            color: 'white',
            backgroundColor: '#3b82f6',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
          }}
        >
          练习下一道题
        </button>
      </div>
    </div>
  )
}
