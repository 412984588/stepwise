import { test, expect } from '@playwright/test'

test.describe('Hint Flow - User Story 1', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('displays problem input form on initial load', async ({ page }) => {
    await expect(page.getByLabel('Enter your math problem')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Start Solving' })).toBeVisible()
  })

  test('submit button is disabled when input is empty', async ({ page }) => {
    const submitButton = page.getByRole('button', { name: 'Start Solving' })
    await expect(submitButton).toBeDisabled()
  })

  test('submit button is enabled when input has content', async ({ page }) => {
    await page.getByLabel('Enter your math problem').fill('3x + 5 = 14')
    const submitButton = page.getByRole('button', { name: 'Start Solving' })
    await expect(submitButton).toBeEnabled()
  })

  test('cannot skip response - submit disabled with less than 10 chars', async ({ page }) => {
    await page.getByLabel('Enter your math problem').fill('3x + 5 = 14')
    await page.getByRole('button', { name: 'Start Solving' }).click()

    await expect(page.locator('#hint-layer-label')).toBeVisible()
    await expect(page.locator('#hint-layer-label')).toContainText('Concept Hint')

    const responseInput = page.getByLabel('Write your thoughts')
    await responseInput.fill('short')

    const submitButton = page.getByRole('button', { name: 'Submit Answer' })
    await expect(submitButton).toBeDisabled()

    await expect(page.getByText(/Need.*more characters/)).toBeVisible()
  })

  test('can submit response with 10+ characters', async ({ page }) => {
    await page.getByLabel('Enter your math problem').fill('3x + 5 = 14')
    await page.getByRole('button', { name: 'Start Solving' }).click()

    await expect(page.locator('#hint-layer-label')).toBeVisible()
    await expect(page.locator('#hint-layer-label')).toContainText('Concept Hint')

    const responseInput = page.getByLabel('Write your thoughts')
    await responseInput.fill('I think this is a linear equation')

    const submitButton = page.getByRole('button', { name: 'Submit Answer' })
    await expect(submitButton).toBeEnabled()

    await expect(page.getByText(/Ready to submit/)).toBeVisible()
  })

  test('response character counter updates in real-time', async ({ page }) => {
    await page.getByLabel('Enter your math problem').fill('3x + 5 = 14')
    await page.getByRole('button', { name: 'Start Solving' }).click()

    const responseInput = page.getByLabel('Write your thoughts')

    await responseInput.fill('12345')
    await expect(page.getByText('5 characters')).toBeVisible()
    await expect(page.getByText('Need 5 more characters')).toBeVisible()

    await responseInput.fill('1234567890')
    await expect(page.getByText('10 characters')).toBeVisible()
    await expect(page.getByText(/Ready to submit/)).toBeVisible()
  })

  test('can cancel and return to input form', async ({ page }) => {
    await page.getByLabel('Enter your math problem').fill('3x + 5 = 14')
    await page.getByRole('button', { name: 'Start Solving' }).click()

    await expect(page.locator('#hint-layer-label')).toBeVisible()
    await expect(page.locator('#hint-layer-label')).toContainText('Concept Hint')

    await page.getByRole('button', { name: 'Start Over' }).click()

    await expect(page.getByLabel('Enter your math problem')).toBeVisible()
  })

  test('shows error message for empty input', async ({ page }) => {
    const textarea = page.getByLabel('Enter your math problem')
    await textarea.fill('   ')

    const submitButton = page.getByRole('button', { name: 'Start Solving' })
    await expect(submitButton).toBeDisabled()
  })

  test('layer progress indicator shows current layer', async ({ page }) => {
    await page.getByLabel('Enter your math problem').fill('3x + 5 = 14')
    await page.getByRole('button', { name: 'Start Solving' }).click()

    await expect(page.locator('#hint-layer-label')).toBeVisible()
    await expect(page.locator('#hint-layer-label')).toContainText('Concept Hint')

    const progressIndicators = page.locator('[style*="border-radius: 50%"]')
    await expect(progressIndicators).toHaveCount(3)
  })
})

test.describe('Layer Progression - User Story 2', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.getByLabel('Enter your math problem').fill('3x + 5 = 14')
    await page.getByRole('button', { name: 'Start Solving' }).click()
    await expect(page.locator('#hint-layer-label')).toBeVisible()
    await expect(page.locator('#hint-layer-label')).toContainText('Concept Hint')
  })

  test('understood response with keyword advances to STRATEGY layer', async ({ page }) => {
    const responseInput = page.getByLabel('Write your thoughts')
    await responseInput.fill('I need to use transposition to move the constant to the right side')

    await page.getByRole('button', { name: 'Submit Answer' }).click()

    await expect(page.locator('#hint-layer-label')).toHaveText('Strategy Hint')
  })

  test('confused response without keyword stays on same layer', async ({ page }) => {
    const responseInput = page.getByLabel('Write your thoughts')
    await responseInput.fill('I think this problem looks interesting')

    await page.getByRole('button', { name: 'Submit Answer' }).click()

    await expect(page.locator('#hint-layer-label')).toBeVisible()
    await expect(page.locator('#hint-layer-label')).toContainText('Concept Hint')
    await expect(page.getByText(/okay.*think about it/i)).toBeVisible()
  })

  test('confusion counter increments on confused response', async ({ page }) => {
    const responseInput = page.getByLabel('Write your thoughts')
    await responseInput.fill('I think this problem looks interesting')

    await page.getByRole('button', { name: 'Submit Answer' }).click()

    await expect(page.getByText('(1/3)')).toBeVisible()
  })

  test('full layer progression from CONCEPT to COMPLETED', async ({ page }) => {
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

    await page
      .getByLabel('Write your thoughts')
      .fill('Following the steps, move 5 to the right side')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Completed')
  })
})

// Dashboard Flow - User Story 4
test.describe('Dashboard Flow - User Story 4', () => {
  test('can navigate to dashboard from main page', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: 'View Learning Stats' }).click()
    await expect(page.getByText('Learning Statistics')).toBeVisible()
  })

  test('dashboard shows stats cards', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: 'View Learning Stats' }).click()

    await expect(page.getByText('Learning Days')).toBeVisible()
    await expect(page.getByText('Independent Completion Rate')).toBeVisible()
    await expect(page.getByText('Weekly Practice')).toBeVisible()
    await expect(page.getByText('Learning Streak')).toBeVisible()
  })

  test('dashboard shows learning goal progress', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: 'View Learning Stats' }).click()

    await expect(page.getByText('Learning Goals')).toBeVisible()
    await expect(page.getByText('Daily Goal')).toBeVisible()
    await expect(page.getByText('Weekly Goal')).toBeVisible()
  })

  test('dashboard shows trend chart', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: 'View Learning Stats' }).click()

    await expect(page.getByText('Practice Trend')).toBeVisible()
    await expect(page.getByText('Last 7 days')).toBeVisible()
    await expect(page.getByText('Independent', { exact: true })).toBeVisible()
    await expect(page.getByText('Total Practice')).toBeVisible()
  })

  test('can return to main from dashboard', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: 'View Learning Stats' }).click()
    await expect(page.getByText('Learning Statistics')).toBeVisible()

    await page.getByRole('button', { name: 'Back to Practice' }).click()
    await expect(page.getByLabel('Enter your math problem')).toBeVisible()
  })

  test('dashboard shows session history after completing a session', async ({ page }) => {
    await page.goto('/')
    await page.getByLabel('Enter your math problem').fill('5x = 25')
    await page.getByRole('button', { name: 'Start Solving' }).click()
    await expect(page.locator('#hint-layer-label')).toBeVisible()
    await expect(page.locator('#hint-layer-label')).toContainText('Concept Hint')

    await page.getByRole('button', { name: 'Start Over' }).click()
    await page.getByRole('button', { name: 'View Learning Stats' }).click()

    await expect(page.getByText('Recent Practice')).toBeVisible()
    await expect(page.getByText('5x = 25').first()).toBeVisible()
  })
})

test.describe('Reveal Solution Flow - User Story 3', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.getByLabel('Enter your math problem').fill('3x + 5 = 14')
    await page.getByRole('button', { name: 'Start Solving' }).click()
    await expect(page.locator('#hint-layer-label')).toBeVisible()
    await expect(page.locator('#hint-layer-label')).toContainText('Concept Hint')
  })

  test('reveal button is disabled at CONCEPT layer', async ({ page }) => {
    const revealButton = page.getByRole('button', { name: 'Show Solution' })
    await expect(revealButton).toBeDisabled()
  })

  test('I solved it button is disabled at CONCEPT layer', async ({ page }) => {
    const completeButton = page.getByRole('button', { name: 'I solved it!' })
    await expect(completeButton).toBeDisabled()
  })

  test('reveal button becomes enabled after reaching STEP layer', async ({ page }) => {
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

    const revealButton = page.getByRole('button', { name: 'Show Solution' })
    await expect(revealButton).toBeEnabled()
  })

  test('I solved it button becomes enabled at STEP layer', async ({ page }) => {
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

    const completeButton = page.getByRole('button', { name: 'I solved it!' })
    await expect(completeButton).toBeEnabled()
  })

  test('clicking reveal shows solution viewer', async ({ page }) => {
    await page
      .getByLabel('Write your thoughts')
      .fill('I need to use transposition to move the constant')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await page
      .getByLabel('Write your thoughts')
      .fill('I understand, first transpose then combine like terms')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Step Hint')

    await page.getByRole('button', { name: 'Show Solution' }).click()

    await expect(page.getByText('Complete Solution', { exact: true }).first()).toBeVisible()
    await expect(page.getByText('Final Answer')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Practice Next Problem' })).toBeVisible()
  })

  test('clicking I solved it returns to problem input', async ({ page }) => {
    await page
      .getByLabel('Write your thoughts')
      .fill('I need to use transposition to move the constant')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await page
      .getByLabel('Write your thoughts')
      .fill('I understand, first transpose then combine like terms')
    await page.getByRole('button', { name: 'Submit Answer' }).click()
    await expect(page.locator('#hint-layer-label')).toHaveText('Step Hint')

    await page.getByRole('button', { name: 'I solved it!' }).click()

    await expect(page.getByLabel('Enter your math problem')).toBeVisible()
  })
})
