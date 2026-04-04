import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { chromium } from '@playwright/test'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const repoRoot = path.resolve(__dirname, '../../..')
const outputDir = path.join(repoRoot, 'docs', 'screenshots')
const tempVideoDir = path.join(outputDir, '.tmp-video')
const outputVideoPath = path.join(outputDir, 'prd-pilot-demo.webm')
const baseUrl = process.env.PRD_PILOT_DEMO_BASE_URL || 'http://127.0.0.1:5173'

const modelConfig = {
  provider: 'deepseek',
  model: 'deepseek-chat',
  api_key: 'mock-key',
  base_url: 'https://api.deepseek.com/v1',
  max_tokens: 0,
}

const demoIdea = 'Build a web tool that helps student PMs turn vague ideas into a Requirement Spec, PRD, and reviewable demo.'
const demoIteration = 'Add a dedicated result page and make the feedback summary more obvious for reviewers.'

const pause = (page, ms) => page.waitForTimeout(ms)

async function main() {
  await fs.mkdir(tempVideoDir, { recursive: true })
  await fs.mkdir(outputDir, { recursive: true })

  const browser = await chromium.launch({
    headless: true,
    args: ['--window-size=1520,980'],
  })

  const context = await browser.newContext({
    viewport: { width: 1520, height: 980 },
    recordVideo: {
      dir: tempVideoDir,
      size: { width: 1520, height: 980 },
    },
  })

  const page = await context.newPage()
  const video = page.video()

  await page.addInitScript(([storageKey, config]) => {
    localStorage.setItem(storageKey, JSON.stringify(config))
  }, ['prd-pilot-model-config-v1', modelConfig])

  await page.goto(baseUrl, { waitUntil: 'networkidle' })
  await pause(page, 1500)

  const ideaInput = page.locator('textarea').first()
  await ideaInput.click()
  await ideaInput.pressSequentially(demoIdea, { delay: 32 })
  await pause(page, 1200)

  const primaryActions = page.locator('.input-card .actions-grid .el-button')
  await primaryActions.nth(0).click()
  await expectVisible(page.locator('.spec-card input').first())
  await pause(page, 1800)

  await primaryActions.nth(1).click()
  await expectVisible(page.locator('.markdown-body h1'))
  await pause(page, 1800)

  await primaryActions.nth(2).click()
  await expectVisible(page.locator('.quality-banner'))
  await pause(page, 2800)

  await page.locator('.result-card .toolbar-actions .el-button').first().click()
  await expectVisible(page.locator('.consistency .score'))
  await pause(page, 2200)

  const feedbackCard = page.locator('.feedback-card')
  await feedbackCard.scrollIntoViewIfNeeded()
  await pause(page, 1000)

  const iterationInput = page.locator('.feedback-card textarea')
  await iterationInput.click()
  await iterationInput.pressSequentially(demoIteration, { delay: 24 })
  await pause(page, 1000)

  await page.locator('.feedback-card .feedback-actions .el-button').nth(1).click()
  await expectVisible(page.locator('.feedback-card .check-item'))
  await pause(page, 3500)

  await page.close()
  await context.close()
  await browser.close()

  const recordedVideoPath = await video.path()
  await fs.copyFile(recordedVideoPath, outputVideoPath)
  await fs.rm(tempVideoDir, { recursive: true, force: true })

  process.stdout.write(`${outputVideoPath}\n`)
}

async function expectVisible(locator) {
  await locator.waitFor({ state: 'visible', timeout: 60_000 })
}

main().catch(async (error) => {
  process.stderr.write(`${error.stack || error}\n`)
  try {
    await fs.rm(tempVideoDir, { recursive: true, force: true })
  } catch {}
  process.exit(1)
})
