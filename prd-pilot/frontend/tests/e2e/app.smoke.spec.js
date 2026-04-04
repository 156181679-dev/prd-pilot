import { expect, test } from '@playwright/test'

function seedModelConfig(page, model) {
  return page.addInitScript(([storageKey, selectedModel]) => {
    localStorage.setItem(
      storageKey,
      JSON.stringify({
        provider: 'deepseek',
        model: selectedModel,
        api_key: 'mock-key',
        base_url: 'https://api.deepseek.com/v1',
        max_tokens: 0
      })
    )
  }, ['prd-pilot-model-config-v1', model])
}

test('full happy path works with mock provider', async ({ page }) => {
  await seedModelConfig(page, 'deepseek-chat')
  await page.goto('/')

  await page.locator('textarea').first().fill('Build a web tool that helps student PMs turn vague ideas into a PRD and a demo.')
  await page.locator('.input-card .actions-grid .el-button').nth(0).click()
  await expect(page.locator('.spec-card input').first()).toHaveValue(/Mock/)

  await page.locator('.input-card .actions-grid .el-button').nth(1).click()
  await expect(page.locator('.markdown-body h1')).toContainText('Mock')

  await page.locator('.input-card .actions-grid .el-button').nth(2).click()
  await expect(page.locator('.quality-banner')).toBeVisible()
  await expect(page.locator('iframe.demo-frame')).toBeVisible()

  await page.locator('.result-card .toolbar-actions .el-button').first().click()
  await expect(page.locator('.consistency .score')).toBeVisible()

  await page.locator('.feedback-card textarea').fill('Add a dedicated result page and make the feedback summary more obvious.')
  await page.locator('.feedback-card .feedback-actions .el-button').nth(1).click()
  await expect(page.locator('.feedback-card .check-item')).toBeVisible()
})

test('demo timeout surfaces readable error instead of infinite loading', async ({ page }) => {
  await seedModelConfig(page, 'mock-timeout')
  await page.goto('/')

  await page.locator('textarea').first().fill('Build a web tool that helps student PMs turn vague ideas into a PRD and a demo.')
  await page.locator('.input-card .actions-grid .el-button').nth(2).click()

  const errorPanel = page.locator('.error-panel')
  await expect(errorPanel).toBeVisible()
  await expect(errorPanel).toContainText('demo_render_timeout')
  await expect(page.locator('iframe.demo-frame')).toHaveCount(0)
})
