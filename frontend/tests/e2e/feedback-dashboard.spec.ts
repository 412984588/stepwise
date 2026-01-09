import { test, expect } from '@playwright/test'

test.describe('Feedback Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('onboarding_completed', 'true')
      localStorage.setItem('beta_access_code', 'test-beta-code')
    })
  })

  test('navigates to feedback dashboard from main page', async ({ page }) => {
    await page.goto('/')

    // Click the feedback analytics button
    await page.getByTestId('nav-feedback-dashboard').click()

    // Should show feedback dashboard
    await expect(page.getByTestId('feedback-dashboard')).toBeVisible()
  })

  test('displays stats cards after loading', async ({ page }) => {
    await page.goto('/')
    await page.getByTestId('nav-feedback-dashboard').click()
    await expect(page.getByTestId('feedback-dashboard')).toBeVisible()
    await expect(page.getByTestId('pmf-score')).toBeVisible()
    await expect(page.getByTestId('total-count')).toBeVisible()
    await expect(page.getByTestId('email-rate')).toBeVisible()
  })

  test('can navigate back to main page', async ({ page }) => {
    await page.goto('/')

    // Navigate to feedback dashboard
    await page.getByTestId('nav-feedback-dashboard').click()
    await expect(page.getByTestId('feedback-dashboard')).toBeVisible()

    // Click back button
    await page.getByTestId('back-button').click()

    // Should be back on main page (problem input visible)
    await expect(page.getByTestId('problem-input')).toBeVisible()
  })

  test('shows export CSV button', async ({ page }) => {
    await page.goto('/')

    // Navigate to feedback dashboard
    await page.getByTestId('nav-feedback-dashboard').click()
    await expect(page.getByTestId('feedback-dashboard')).toBeVisible()

    // Export button should be visible
    await expect(page.getByTestId('export-csv')).toBeVisible()
  })

  test('displays feedback items after submission', async ({ page }) => {
    await page.goto('/')

    // First submit some feedback
    await page.getByTestId('nav-feedback').click()
    await expect(page.getByTestId('feedback-modal')).toBeVisible()

    // Fill out the feedback form
    await page.getByTestId('pmf-very_disappointed').click()
    await page.getByTestId('grade-level').selectOption('grade_6')
    await page.getByTestId('submit-feedback').click()

    // Wait for modal to close (success)
    await expect(page.getByTestId('feedback-modal')).not.toBeVisible({ timeout: 5000 })

    // Navigate to feedback dashboard
    await page.getByTestId('nav-feedback-dashboard').click()
    await expect(page.getByTestId('feedback-dashboard')).toBeVisible()

    // Should show at least one feedback item
    await expect(page.getByTestId('feedback-item').first()).toBeVisible({ timeout: 5000 })
  })
})
