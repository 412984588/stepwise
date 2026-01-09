import { test, expect } from '@playwright/test'

test.describe('Feedback Modal Flow', () => {
  test('should open feedback modal, submit feedback, and show success toast', async ({ page }) => {
    // Navigate to the app
    await page.goto('/')

    // Click the feedback button in the footer
    const feedbackButton = page.getByTestId('nav-feedback')
    await expect(feedbackButton).toBeVisible()
    await feedbackButton.click()

    // Verify modal is open
    const modal = page.getByTestId('feedback-modal')
    await expect(modal).toBeVisible()

    // Fill in PMF question - click the radio button
    await page.getByTestId('pmf-very_disappointed').click()

    // Fill in optional text fields
    await page.getByTestId('what-worked').fill('The hints were very helpful!')
    await page.getByTestId('what-confused').fill('Nothing was confusing')

    // Select would pay option
    await page.getByTestId('would-pay').selectOption('yes_probably')

    // Select grade level
    await page.getByTestId('grade-level').selectOption('grade_6')

    // Submit button should be enabled now
    const submitButton = page.getByTestId('submit-feedback')
    await expect(submitButton).toBeEnabled()

    // Submit the feedback
    await submitButton.click()

    // Modal should close
    await expect(modal).not.toBeVisible()

    // Success message should appear
    await expect(page.getByText('Thank you for your feedback!')).toBeVisible()
  })

  test('should require PMF answer and grade level before submit', async ({ page }) => {
    await page.goto('/')

    // Open feedback modal
    await page.getByTestId('nav-feedback').click()
    const modal = page.getByTestId('feedback-modal')
    await expect(modal).toBeVisible()

    // Submit button should be disabled initially
    const submitButton = page.getByTestId('submit-feedback')
    await expect(submitButton).toBeDisabled()

    // Select only PMF answer - still disabled
    await page.getByTestId('pmf-somewhat_disappointed').click()
    await expect(submitButton).toBeDisabled()

    // Select grade level - now enabled
    await page.getByTestId('grade-level').selectOption('grade_5')
    await expect(submitButton).toBeEnabled()
  })

  test('should close modal when clicking cancel', async ({ page }) => {
    await page.goto('/')

    // Open feedback modal
    await page.getByTestId('nav-feedback').click()
    const modal = page.getByTestId('feedback-modal')
    await expect(modal).toBeVisible()

    // Click cancel
    await page.getByRole('button', { name: 'Cancel' }).click()

    // Modal should close
    await expect(modal).not.toBeVisible()
  })

  test('should validate email format when provided', async ({ page }) => {
    await page.goto('/')

    // Open feedback modal
    await page.getByTestId('nav-feedback').click()

    // Fill required fields
    await page.getByTestId('pmf-very_disappointed').click()
    await page.getByTestId('grade-level').selectOption('grade_7')

    // Enter invalid email
    await page.getByTestId('feedback-email').fill('not-an-email')

    // Submit should be disabled due to invalid email
    const submitButton = page.getByTestId('submit-feedback')
    await expect(submitButton).toBeDisabled()

    // Fix the email
    await page.getByTestId('feedback-email').fill('parent@example.com')

    // Now consent checkbox should appear
    const consentCheckbox = page.getByTestId('consent-checkbox')
    await expect(consentCheckbox).toBeVisible()

    // Submit still disabled until consent is given
    await expect(submitButton).toBeDisabled()

    // Check consent
    await consentCheckbox.click()

    // Now submit should be enabled
    await expect(submitButton).toBeEnabled()
  })
})
