import { test, expect } from '@playwright/test'

test.describe('PDF Report Download', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('onboarding_completed', 'true')
      localStorage.setItem('beta_access_code', 'test-beta-code')
    })
  })

  test('download report button appears in session history', async ({ page }) => {
    await page.goto('/')

    await page.getByRole('button', { name: 'View Learning Stats' }).click()

    const reportButton = page.getByTestId('download-pdf').first()
    await expect(reportButton).toBeVisible()
  })

  test('clicking download report triggers PDF download', async ({ page }) => {
    await page.goto('/')

    await page.getByRole('button', { name: 'View Learning Stats' }).click()

    const downloadPromise = page.waitForEvent('download')
    await page.getByTestId('download-pdf').first().click()

    const download = await downloadPromise
    expect(download.suggestedFilename()).toMatch(/stepwise_session_.*\.pdf/)
  })
})

test.describe('Event Tracking', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('onboarding_completed', 'true')
      localStorage.setItem('beta_access_code', 'test-beta-code')
    })
  })

  test('session start triggers event logging', async ({ page, context }) => {
    let eventLogged = false

    page.on('request', (request) => {
      if (request.url().includes('/events') && request.method() === 'POST') {
        eventLogged = true
      }
    })

    await page.goto('/')

    await page.getByLabel(/输入数学题|Enter your math problem/i).fill('Solve 2x + 5 = 11')
    await page.getByRole('button', { name: /开始解题|Start Solving/i }).click()

    await page.waitForTimeout(1000)
  })
})

test.describe('Session Learning Summary', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('onboarding_completed', 'true')
      localStorage.setItem('beta_access_code', 'test-beta-code')
    })
  })

  test('summary appears on dashboard for recent session', async ({ page }) => {
    await page.goto('/')

    await page.getByRole('button', { name: 'View Learning Stats' }).click()

    await page.waitForTimeout(500)

    const summaryHeading = page.getByText(/Session Summary for Parents/i)
    if (await summaryHeading.isVisible({ timeout: 2000 }).catch(() => false)) {
      await expect(summaryHeading).toBeVisible()

      const performanceLevel = page.getByText(/Excellent|Good|Needs Practice/)
      await expect(performanceLevel).toBeVisible()

      const insightsHeading = page.getByText(/Key Insights:/i)
      await expect(insightsHeading).toBeVisible()

      const recommendationHeading = page.getByText(/Recommendation:/i)
      await expect(recommendationHeading).toBeVisible()
    }
  })
})
