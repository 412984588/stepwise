interface SuccessMessageProps {
  message: string
  onDismiss?: () => void
}

export function SuccessMessage({ message, onDismiss }: SuccessMessageProps) {
  if (!message) return null

  return (
    <div
      role="status"
      data-test-id="success-message"
      style={{
        padding: '12px 16px',
        backgroundColor: '#f0fdf4',
        border: '1px solid #bbf7d0',
        borderRadius: '8px',
        color: '#16a34a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
      }}
    >
      <span>{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: '#16a34a',
            fontSize: '18px',
            padding: '0 4px',
          }}
          aria-label="关闭成功提示"
        >
          ×
        </button>
      )}
    </div>
  )
}
