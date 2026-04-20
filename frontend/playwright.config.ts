import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://127.0.0.1:4173',
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: 'node ./scripts/e2e-webserver.mjs',
    port: 4173,
    reuseExistingServer: !process.env.CI,
  },
})
