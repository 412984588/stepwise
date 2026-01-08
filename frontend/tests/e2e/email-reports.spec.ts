import { test, expect } from '@playwright/test'

test.describe('Email Reports - Completion with Email', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.getByLabel('Enter your math problem').fill('3x + 5 = 14')
    await page.getByRole('button', { name: 'Start Solving' }).click()
    await expect(page.locator('#hint-layer-label')).toBeVisible()
    await expect(page.locator('#hint-layer-label')).toContainText('Concept Hint')
  })

  test('email input is not visible at CONCEPT layer', async ({ page }) => {
    const emailInput = page.getByLabel('Send learning report to email (optional)')
    await expect(emailInput).not.toBeVisible()
  })

  test('email input is not visible at STRATEGY layer', async ({ page }) => {
    await page
      .getByLabel('Write your thoughts')
      .fill('I need to use transposition to move the constant')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Strategy Hint')

    const emailInput = page.getByLabel('Send learning report to email (optional)')
    await expect(emailInput).not.toBeVisible()
  })

  test('email input is visible at STEP layer', async ({ page }) => {
    await page
      .getByLabel('Write your thoughts')
      .fill('I need to use transposition to move the constant')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await page
      .getByLabel('Write your thoughts')
      .fill('I understand, first transpose then combine like terms')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Step Hint')

    const emailInput = page.getByLabel('Send learning report to email (optional)')
    await expect(emailInput).toBeVisible()
    await expect(emailInput).toHaveAttribute('placeholder', 'parent@example.com')
  })

  test('can complete session without providing email', async ({ page }) => {
    await page
      .getByLabel('Write your thoughts')
      .fill('I need to use transposition to move the constant')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await page
      .getByLabel('Write your thoughts')
      .fill('I understand, first transpose then combine like terms')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Step Hint')

    const emailInput = page.getByLabel('Send learning report to email (optional)')
    await expect(emailInput).toBeVisible()
    await expect(emailInput).toHaveValue('')

    await page.getByRole('button', { name: 'I solved it!' }).click()

    await expect(page.getByLabel('Enter your math problem')).toBeVisible()
    await expect(page.getByTestId('success-message')).not.toBeVisible()
  })

  test('shows validation error for invalid email format', async ({ page }) => {
    await page
      .getByLabel('Write your thoughts')
      .fill('I need to use transposition to move the constant')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await page
      .getByLabel('Write your thoughts')
      .fill('I understand, first transpose then combine like terms')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Step Hint')

    const emailInput = page.getByLabel('Send learning report to email (optional)')
    await emailInput.fill('invalid-email')

    await page.getByRole('button', { name: 'I solved it!' }).click()

    await expect(page.getByText(/valid email address/i)).toBeVisible()
    await expect(page.locator('#hint-layer-label')).toHaveText('Step Hint')
  })

  test('validation error clears when user types valid email', async ({ page }) => {
    await page
      .getByLabel('Write your thoughts')
      .fill('I need to use transposition to move the constant')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await page
      .getByLabel('Write your thoughts')
      .fill('I understand, first transpose then combine like terms')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Step Hint')

    const emailInput = page.getByLabel('Send learning report to email (optional)')
    await emailInput.fill('invalid-email')
    await page.getByRole('button', { name: 'I solved it!' }).click()
    await expect(page.getByText(/valid email address/i)).toBeVisible()

    await emailInput.fill('parent@example.com')
    await expect(page.getByText(/valid email address/i)).not.toBeVisible()
  })

  test('can complete session with valid email', async ({ page }) => {
    await page
      .getByLabel('Write your thoughts')
      .fill('I need to use transposition to move the constant')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await page
      .getByLabel('Write your thoughts')
      .fill('I understand, first transpose then combine like terms')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Step Hint')

    const emailInput = page.getByLabel('Send learning report to email (optional)')
    await emailInput.fill('parent@example.com')

    await page.getByRole('button', { name: 'I solved it!' }).click()

    await expect(page.getByLabel('Enter your math problem')).toBeVisible()
  })

  test('completes session and returns to input after providing email', async ({ page }) => {
    await page
      .getByLabel('Write your thoughts')
      .fill('I need to use transposition to move the constant')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await page
      .getByLabel('Write your thoughts')
      .fill('I understand, first transpose then combine like terms')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Step Hint')

    const emailInput = page.getByLabel('Send learning report to email (optional)')
    await emailInput.fill('parent@example.com')

    await page.getByRole('button', { name: 'I solved it!' }).click()

    await expect(page.getByLabel('Enter your math problem')).toBeVisible()
  })

  test('email input accepts various valid email formats', async ({ page }) => {
    await page
      .getByLabel('Write your thoughts')
      .fill('I need to use transposition to move the constant')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await page
      .getByLabel('Write your thoughts')
      .fill('I understand, first transpose then combine like terms')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Step Hint')

    const emailInput = page.getByLabel('Send learning report to email (optional)')
    const validEmails = ['user@example.com', 'user.name+tag@example.co.uk']

    for (const email of validEmails) {
      await emailInput.fill(email)
      await page.getByRole('button', { name: 'I solved it!' }).click()
      await expect(page.getByLabel('Enter your math problem')).toBeVisible()

      await page.getByLabel('Enter your math problem').fill('5x = 25')
      await page.getByRole('button', { name: 'Start Solving' }).click()
      await page
        .getByLabel('Write your thoughts')
        .fill('I need to use transposition to move the constant')
      await page.getByRole('button', { name: 'Submit Answer' }).click()
      await page
        .getByLabel('Write your thoughts')
        .fill('I understand, first transpose then combine like terms')
      await page.getByRole('button', { name: 'Submit Answer' }).click()
      await expect(page.locator('#hint-layer-label')).toHaveText('Step Hint')
    }
  })
})
