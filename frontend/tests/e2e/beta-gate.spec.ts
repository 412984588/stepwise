import { test, expect } from '@playwright/test'

test.describe('Beta Gate - Access Control', () => {
  test.describe('Without beta code', () => {
    test.beforeEach(async ({ page }) => {
      await page.addInitScript(() => {
        localStorage.setItem('onboarding_completed', 'true')
      })
      await page.goto('/')
    })

    test('shows beta gate modal when no code in localStorage', async ({ page }) => {
      await expect(page.getByTestId('beta-gate-modal')).toBeVisible()
      await expect(page.getByText('Private Beta Access')).toBeVisible()
    })

    test('beta code input is visible and focusable', async ({ page }) => {
      const input = page.getByTestId('beta-code-input')
      await expect(input).toBeVisible()
      await input.focus()
      await expect(input).toBeFocused()
    })

    test('submit button is disabled when input is empty', async ({ page }) => {
      const submitButton = page.getByTestId('beta-code-submit')
      await expect(submitButton).toBeDisabled()
    })

    test('submit button is enabled when input has content', async ({ page }) => {
      const input = page.getByTestId('beta-code-input')
      await input.fill('test-code')

      const submitButton = page.getByTestId('beta-code-submit')
      await expect(submitButton).toBeEnabled()
    })

    test('entering valid code closes modal and shows main app', async ({ page }) => {
      const input = page.getByTestId('beta-code-input')
      await input.fill('test-beta-code')

      const submitButton = page.getByTestId('beta-code-submit')
      await submitButton.click()

      await expect(page.getByTestId('beta-gate-modal')).not.toBeVisible({ timeout: 10000 })

      await expect(page.getByLabel('Enter your math problem')).toBeVisible()
    })

    test('beta code is stored in localStorage after submission', async ({ page }) => {
      const input = page.getByTestId('beta-code-input')
      await input.fill('my-beta-code')

      const submitButton = page.getByTestId('beta-code-submit')
      await submitButton.click()

      await expect(page.getByTestId('beta-gate-modal')).not.toBeVisible({ timeout: 10000 })

      const storedCode = await page.evaluate(() => localStorage.getItem('beta_access_code'))
      expect(storedCode).toBe('my-beta-code')
    })
  })

  test.describe('With beta code', () => {
    test.beforeEach(async ({ page }) => {
      await page.addInitScript(() => {
        localStorage.setItem('onboarding_completed', 'true')
        localStorage.setItem('beta_access_code', 'valid-beta-code')
      })
      await page.goto('/')
    })

    test('does not show beta gate modal when code exists', async ({ page }) => {
      await expect(page.getByTestId('beta-gate-modal')).not.toBeVisible()
      await expect(page.getByLabel('Enter your math problem')).toBeVisible()
    })

    test('can start a session with beta code', async ({ page }) => {
      await page.getByLabel('Enter your math problem').fill('Solve 2x + 5 = 11')
      await page.getByRole('button', { name: 'Start Solving' }).click()

      await expect(page.locator('#hint-layer-label')).toBeVisible({ timeout: 10000 })
      await expect(page.locator('#hint-layer-label')).toContainText('Concept Hint')
    })

    test('can complete full hint flow with beta code', async ({ page }) => {
      await page.getByLabel('Enter your math problem').fill('Solve 2x + 5 = 11')
      await page.getByRole('button', { name: 'Start Solving' }).click()

      await expect(page.locator('#hint-layer-label')).toContainText('Concept Hint')

      const responseInput = page.getByLabel('Write your thoughts')
      await responseInput.fill('I understand we need to move terms')

      await page.getByRole('button', { name: 'Submit Answer' }).click()

      await expect(page.locator('#hint-layer-label')).toBeVisible({ timeout: 10000 })
    })
  })

  test.describe('Beta gate modal interactions', () => {
    test.beforeEach(async ({ page }) => {
      await page.addInitScript(() => {
        localStorage.setItem('onboarding_completed', 'true')
      })
      await page.goto('/')
    })

    test('shows request access link', async ({ page }) => {
      await expect(page.getByText("Don't have a code?")).toBeVisible()
      await expect(page.getByText('Request access')).toBeVisible()
    })

    test('request access link has correct href', async ({ page }) => {
      const link = page.getByText('Request access')
      await expect(link).toHaveAttribute('href', /mailto:beta@stepwise.app/)
    })
  })
})
