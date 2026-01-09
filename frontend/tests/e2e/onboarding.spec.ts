import { test, expect } from '@playwright/test'

test.describe('Onboarding Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.clear()
      localStorage.setItem('beta_access_code', 'test-beta-code')
    })
  })

  test('shows onboarding modal on first visit', async ({ page }) => {
    await page.goto('/')
    const modal = page.getByTestId('onboarding-modal')
    await expect(modal).toBeVisible()
    await expect(page.getByText('Welcome to StepWise!')).toBeVisible()
  })

  test('displays all three feature bullets', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByText('Guided hints (Concept → Strategy → Step)')).toBeVisible()
    await expect(page.getByText('PDF learning report after completion')).toBeVisible()
    await expect(page.getByText('Weekly digest (optional)')).toBeVisible()
  })

  test('completing onboarding hides modal and saves to localStorage', async ({ page }) => {
    await page.goto('/')
    const modal = page.getByTestId('onboarding-modal')
    await expect(modal).toBeVisible()

    await page.getByTestId('onboarding-continue').click()

    await expect(modal).not.toBeVisible()

    const completed = await page.evaluate(() => localStorage.getItem('onboarding_completed'))
    expect(completed).toBe('true')
  })

  test('reload does not show onboarding again after completion', async ({ page }) => {
    await page.goto('/')
    await page.getByTestId('onboarding-continue').click()
    await expect(page.getByTestId('onboarding-modal')).not.toBeVisible()

    const completed = await page.evaluate(() => localStorage.getItem('onboarding_completed'))
    expect(completed).toBe('true')

    await page.addInitScript(() => {
      localStorage.setItem('onboarding_completed', 'true')
      localStorage.setItem('beta_access_code', 'test-beta-code')
    })
    await page.reload()

    await expect(page.getByTestId('onboarding-modal')).not.toBeVisible()
    await expect(page.getByLabel('Enter your math problem')).toBeVisible()
  })

  test('can reopen onboarding via Settings button', async ({ page }) => {
    await page.goto('/')
    await page.getByTestId('onboarding-continue').click()
    await expect(page.getByTestId('onboarding-modal')).not.toBeVisible()

    await page.getByTestId('nav-settings').click()

    await expect(page.getByTestId('onboarding-modal')).toBeVisible()
  })

  test('grade selector saves selection to localStorage', async ({ page }) => {
    await page.goto('/')

    const gradeSelect = page.getByTestId('onboarding-grade').locator('select')
    await gradeSelect.selectOption('6')

    await page.getByTestId('onboarding-continue').click()

    const savedGrade = await page.evaluate(() => localStorage.getItem('grade_level'))
    expect(savedGrade).toBe('6')
  })

  test('locale selector saves selection to localStorage', async ({ page }) => {
    await page.goto('/')

    const localeSelect = page.getByTestId('onboarding-locale').locator('select')
    await localeSelect.selectOption('zh-CN')

    await page.getByTestId('onboarding-continue').click()

    const savedLocale = await page.evaluate(() => localStorage.getItem('locale'))
    expect(savedLocale).toBe('zh-CN')
  })

  test('email input validates email format', async ({ page }) => {
    await page.goto('/')

    const emailInput = page.getByTestId('onboarding-email')
    await emailInput.fill('invalid-email')
    await emailInput.blur()

    await expect(page.getByText('Please enter a valid email address')).toBeVisible()
  })

  test('email input accepts valid email', async ({ page }) => {
    await page.goto('/')

    const emailInput = page.getByTestId('onboarding-email')
    await emailInput.fill('parent@example.com')
    await emailInput.blur()

    await expect(page.getByText('Please enter a valid email address')).not.toBeVisible()
  })

  test('opt-in checkboxes are disabled when no email is provided', async ({ page }) => {
    await page.goto('/')

    const sessionOptIn = page.getByTestId('onboarding-session-optin')
    const weeklyOptIn = page.getByTestId('onboarding-weekly-optin')

    await expect(sessionOptIn).toBeDisabled()
    await expect(weeklyOptIn).toBeDisabled()
  })

  test('opt-in checkboxes are enabled when email is provided', async ({ page }) => {
    await page.goto('/')

    await page.getByTestId('onboarding-email').fill('parent@example.com')

    const sessionOptIn = page.getByTestId('onboarding-session-optin')
    const weeklyOptIn = page.getByTestId('onboarding-weekly-optin')

    await expect(sessionOptIn).toBeEnabled()
    await expect(weeklyOptIn).toBeEnabled()
  })

  test('saves email preferences to localStorage', async ({ page }) => {
    await page.goto('/')

    await page.getByTestId('onboarding-email').fill('parent@example.com')
    await page.getByTestId('onboarding-session-optin').check()
    await page.getByTestId('onboarding-weekly-optin').check()

    await page.getByTestId('onboarding-continue').click()

    const savedEmail = await page.evaluate(() => localStorage.getItem('parent_email'))
    const sessionOptIn = await page.evaluate(() => localStorage.getItem('opt_in_session_reports'))
    const weeklyOptIn = await page.evaluate(() => localStorage.getItem('opt_in_weekly_digest'))

    expect(savedEmail).toBe('parent@example.com')
    expect(sessionOptIn).toBe('true')
    expect(weeklyOptIn).toBe('true')
  })

  test('does not save opt-in preferences when email is cleared', async ({ page }) => {
    await page.goto('/')

    await page.getByTestId('onboarding-email').fill('parent@example.com')
    await page.getByTestId('onboarding-session-optin').check()
    await page.getByTestId('onboarding-email').clear()

    await page.getByTestId('onboarding-continue').click()

    const sessionOptIn = await page.evaluate(() => localStorage.getItem('opt_in_session_reports'))
    expect(sessionOptIn).toBe('false')
  })

  test('preserves preferences when reopening via Settings', async ({ page }) => {
    await page.goto('/')

    const gradeSelect = page.getByTestId('onboarding-grade').locator('select')
    await gradeSelect.selectOption('7')
    await page.getByTestId('onboarding-email').fill('test@example.com')

    await page.getByTestId('onboarding-continue').click()
    await page.getByTestId('nav-settings').click()

    await expect(gradeSelect).toHaveValue('7')
    await expect(page.getByTestId('onboarding-email')).toHaveValue('test@example.com')
  })

  test('continue button is always enabled (email is optional)', async ({ page }) => {
    await page.goto('/')

    const continueButton = page.getByTestId('onboarding-continue')
    await expect(continueButton).toBeEnabled()
  })

  test('shows validation error for invalid email format', async ({ page }) => {
    await page.goto('/')

    await page.getByTestId('onboarding-email').fill('invalid')
    await page.getByTestId('onboarding-email').blur()

    await expect(page.getByText('Please enter a valid email address')).toBeVisible()
  })

  test('shows Privacy Policy and Terms links', async ({ page }) => {
    await page.goto('/')

    await expect(page.getByRole('link', { name: 'Privacy Policy' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Terms of Service' })).toBeVisible()
  })
})

test.describe('Onboarding Integration with App', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.clear()
      localStorage.setItem('beta_access_code', 'test-beta-code')
    })
  })

  test('grade selection in onboarding is reflected in main app', async ({ page }) => {
    await page.goto('/')

    const onboardingGradeSelect = page.getByTestId('onboarding-grade').locator('select')
    await onboardingGradeSelect.selectOption('5')

    await page.getByTestId('onboarding-continue').click()

    const mainGradeSelect = page.locator('#grade-select')
    await expect(mainGradeSelect).toHaveValue('5')
  })

  test('email is pre-filled in HintDialog when session reports opt-in is enabled', async ({
    page,
  }) => {
    await page.goto('/')

    await page.getByTestId('onboarding-email').fill('parent@test.com')
    await page.getByTestId('onboarding-session-optin').check()
    await page.getByTestId('onboarding-continue').click()

    await page.getByLabel('Enter your math problem').fill('2x + 3 = 7')
    await page.getByRole('button', { name: 'Start Solving' }).click()

    await expect(page.locator('#hint-layer-label')).toBeVisible()

    await page
      .getByLabel('Write your thoughts')
      .fill('I need to use transposition to move the constant')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Strategy Hint')

    await page
      .getByLabel('Write your thoughts')
      .fill('I understand, first transpose then combine like terms')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Step Hint')

    const emailInput = page.locator('[data-test-id="email-input"]')
    await expect(emailInput).toHaveValue('parent@test.com')
  })
})
