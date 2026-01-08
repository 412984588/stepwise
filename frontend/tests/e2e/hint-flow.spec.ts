import { test, expect } from '@playwright/test'

test.describe('Hint Flow - User Story 1', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('displays problem input form on initial load', async ({ page }) => {
    await expect(page.getByLabel('输入你的数学题')).toBeVisible()
    await expect(page.getByRole('button', { name: '开始解题' })).toBeVisible()
  })

  test('submit button is disabled when input is empty', async ({ page }) => {
    const submitButton = page.getByRole('button', { name: '开始解题' })
    await expect(submitButton).toBeDisabled()
  })

  test('submit button is enabled when input has content', async ({ page }) => {
    await page.getByLabel('输入你的数学题').fill('3x + 5 = 14')
    const submitButton = page.getByRole('button', { name: '开始解题' })
    await expect(submitButton).toBeEnabled()
  })

  test('cannot skip response - submit disabled with less than 10 chars', async ({ page }) => {
    await page.getByLabel('输入你的数学题').fill('3x + 5 = 14')
    await page.getByRole('button', { name: '开始解题' }).click()

    await expect(page.getByText('概念提示')).toBeVisible()

    const responseInput = page.getByLabel('写下你的想法')
    await responseInput.fill('短回复')

    const submitButton = page.getByRole('button', { name: '提交回答' })
    await expect(submitButton).toBeDisabled()

    await expect(page.getByText(/还需要输入.*个字符/)).toBeVisible()
  })

  test('can submit response with 10+ characters', async ({ page }) => {
    await page.getByLabel('输入你的数学题').fill('3x + 5 = 14')
    await page.getByRole('button', { name: '开始解题' }).click()

    await expect(page.getByText('概念提示')).toBeVisible()

    const responseInput = page.getByLabel('写下你的想法')
    await responseInput.fill('我认为这是一道一元一次方程')

    const submitButton = page.getByRole('button', { name: '提交回答' })
    await expect(submitButton).toBeEnabled()

    await expect(page.getByText('✓ 可以提交了')).toBeVisible()
  })

  test('response character counter updates in real-time', async ({ page }) => {
    await page.getByLabel('输入你的数学题').fill('3x + 5 = 14')
    await page.getByRole('button', { name: '开始解题' }).click()

    const responseInput = page.getByLabel('写下你的想法')

    await responseInput.fill('12345')
    await expect(page.getByText('5 字符')).toBeVisible()
    await expect(page.getByText('还需要输入 5 个字符')).toBeVisible()

    await responseInput.fill('1234567890')
    await expect(page.getByText('10 字符')).toBeVisible()
    await expect(page.getByText('✓ 可以提交了')).toBeVisible()
  })

  test('can cancel and return to input form', async ({ page }) => {
    await page.getByLabel('输入你的数学题').fill('3x + 5 = 14')
    await page.getByRole('button', { name: '开始解题' }).click()

    await expect(page.getByText('概念提示')).toBeVisible()

    await page.getByRole('button', { name: '重新开始' }).click()

    await expect(page.getByLabel('输入你的数学题')).toBeVisible()
  })

  test('shows error message for empty input', async ({ page }) => {
    const textarea = page.getByLabel('输入你的数学题')
    await textarea.fill('   ')

    const submitButton = page.getByRole('button', { name: '开始解题' })
    await expect(submitButton).toBeDisabled()
  })

  test('layer progress indicator shows current layer', async ({ page }) => {
    await page.getByLabel('输入你的数学题').fill('3x + 5 = 14')
    await page.getByRole('button', { name: '开始解题' }).click()

    await expect(page.getByText('概念提示')).toBeVisible()

    const progressIndicators = page.locator('[style*="border-radius: 50%"]')
    await expect(progressIndicators).toHaveCount(3)
  })
})

test.describe('Layer Progression - User Story 2', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.getByLabel('输入你的数学题').fill('3x + 5 = 14')
    await page.getByRole('button', { name: '开始解题' }).click()
    await expect(page.getByText('概念提示')).toBeVisible()
  })

  test('understood response with keyword advances to STRATEGY layer', async ({ page }) => {
    const responseInput = page.getByLabel('写下你的想法')
    await responseInput.fill('我觉得需要使用移项来把常数移到等式右边')

    await page.getByRole('button', { name: '提交回答' }).click()

    await expect(page.getByText('策略提示')).toBeVisible()
  })

  test('confused response without keyword stays on same layer', async ({ page }) => {
    const responseInput = page.getByLabel('写下你的想法')
    await responseInput.fill('我觉得这道题目看起来挺有意思的')

    await page.getByRole('button', { name: '提交回答' }).click()

    await expect(page.getByText('概念提示')).toBeVisible()
    await expect(page.getByText(/没关系.*再想想看/)).toBeVisible()
  })

  test('confusion counter increments on confused response', async ({ page }) => {
    const responseInput = page.getByLabel('写下你的想法')
    await responseInput.fill('我觉得这道题目看起来挺有意思的')

    await page.getByRole('button', { name: '提交回答' }).click()

    await expect(page.getByText('(1/3)')).toBeVisible()
  })

  test('full layer progression from CONCEPT to COMPLETED', async ({ page }) => {
    await page.getByLabel('写下你的想法').fill('我觉得需要使用移项来把常数移到等式右边')
    await page.getByRole('button', { name: '提交回答' }).click()
    await expect(page.getByText('策略提示')).toBeVisible()

    await page.getByLabel('写下你的想法').fill('我理解了，需要先移项再合并同类项')
    await page.getByRole('button', { name: '提交回答' }).click()
    await expect(page.getByText('步骤提示')).toBeVisible()

    await page.getByLabel('写下你的想法').fill('按照步骤来，先把5移到右边变成负数')
    await page.getByRole('button', { name: '提交回答' }).click()
    await expect(page.getByText('已完成')).toBeVisible()
  })
})

test.describe('Dashboard Flow - User Story 4', () => {
  test('can navigate to dashboard from main page', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: '查看学习统计' }).click()
    await expect(page.getByText('学习统计')).toBeVisible()
  })

  test('dashboard shows stats cards', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: '查看学习统计' }).click()

    await expect(page.getByText('学习天数')).toBeVisible()
    await expect(page.getByText('独立完成率')).toBeVisible()
    await expect(page.getByText('本周练习')).toBeVisible()
    await expect(page.getByText('连续学习')).toBeVisible()
  })

  test('can return to main from dashboard', async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: '查看学习统计' }).click()
    await expect(page.getByText('学习统计')).toBeVisible()

    await page.getByRole('button', { name: '返回做题' }).click()
    await expect(page.getByLabel('输入你的数学题')).toBeVisible()
  })

  test('dashboard shows session history after completing a session', async ({ page }) => {
    await page.goto('/')
    await page.getByLabel('输入你的数学题').fill('5x = 25')
    await page.getByRole('button', { name: '开始解题' }).click()
    await expect(page.getByText('概念提示')).toBeVisible()

    await page.getByRole('button', { name: '重新开始' }).click()
    await page.getByRole('button', { name: '查看学习统计' }).click()

    await expect(page.getByText('最近练习')).toBeVisible()
    await expect(page.getByText('5x = 25')).toBeVisible()
  })
})

test.describe('Reveal Solution Flow - User Story 3', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.getByLabel('输入你的数学题').fill('3x + 5 = 14')
    await page.getByRole('button', { name: '开始解题' }).click()
    await expect(page.getByText('概念提示')).toBeVisible()
  })

  test('reveal button is disabled at CONCEPT layer', async ({ page }) => {
    const revealButton = page.getByRole('button', { name: '显示解答' })
    await expect(revealButton).toBeDisabled()
  })

  test('I solved it button is disabled at CONCEPT layer', async ({ page }) => {
    const completeButton = page.getByRole('button', { name: '我做出来了！' })
    await expect(completeButton).toBeDisabled()
  })

  test('reveal button becomes enabled after reaching STEP layer', async ({ page }) => {
    // Progress to STRATEGY
    await page.getByLabel('写下你的想法').fill('我觉得需要使用移项来把常数移到等式右边')
    await page.getByRole('button', { name: '提交回答' }).click()
    await expect(page.getByText('策略提示')).toBeVisible()

    // Progress to STEP
    await page.getByLabel('写下你的想法').fill('我理解了，需要先移项再合并同类项')
    await page.getByRole('button', { name: '提交回答' }).click()
    await expect(page.getByText('步骤提示')).toBeVisible()

    // Reveal button should now be enabled
    const revealButton = page.getByRole('button', { name: '显示解答' })
    await expect(revealButton).toBeEnabled()
  })

  test('I solved it button becomes enabled at STEP layer', async ({ page }) => {
    // Progress to STRATEGY
    await page.getByLabel('写下你的想法').fill('我觉得需要使用移项来把常数移到等式右边')
    await page.getByRole('button', { name: '提交回答' }).click()
    await expect(page.getByText('策略提示')).toBeVisible()

    // Progress to STEP
    await page.getByLabel('写下你的想法').fill('我理解了，需要先移项再合并同类项')
    await page.getByRole('button', { name: '提交回答' }).click()
    await expect(page.getByText('步骤提示')).toBeVisible()

    // Complete button should now be enabled
    const completeButton = page.getByRole('button', { name: '我做出来了！' })
    await expect(completeButton).toBeEnabled()
  })

  test('clicking reveal shows solution viewer', async ({ page }) => {
    // Progress to STEP layer
    await page.getByLabel('写下你的想法').fill('我觉得需要使用移项来把常数移到等式右边')
    await page.getByRole('button', { name: '提交回答' }).click()
    await page.getByLabel('写下你的想法').fill('我理解了，需要先移项再合并同类项')
    await page.getByRole('button', { name: '提交回答' }).click()
    await expect(page.getByText('步骤提示')).toBeVisible()

    // Click reveal
    await page.getByRole('button', { name: '显示解答' }).click()

    await expect(page.getByText('完整解答')).toBeVisible()
    await expect(page.getByText('最终答案')).toBeVisible()
    await expect(page.getByRole('button', { name: '练习下一道题' })).toBeVisible()
  })

  test('clicking I solved it returns to problem input', async ({ page }) => {
    // Progress to STEP layer
    await page.getByLabel('写下你的想法').fill('我觉得需要使用移项来把常数移到等式右边')
    await page.getByRole('button', { name: '提交回答' }).click()
    await page.getByLabel('写下你的想法').fill('我理解了，需要先移项再合并同类项')
    await page.getByRole('button', { name: '提交回答' }).click()
    await expect(page.getByText('步骤提示')).toBeVisible()

    // Click complete
    await page.getByRole('button', { name: '我做出来了！' }).click()

    // Should return to problem input
    await expect(page.getByLabel('输入你的数学题')).toBeVisible()
  })
})
