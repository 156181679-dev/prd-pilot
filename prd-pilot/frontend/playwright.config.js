import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 120_000,
  fullyParallel: false,
  use: {
    baseURL: process.env.PRD_PILOT_E2E_BASE_URL || 'http://127.0.0.1:5173',
    trace: 'retain-on-failure'
  },
  reporter: 'list'
})
