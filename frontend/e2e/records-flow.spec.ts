import { expect, test } from '@playwright/test'

test('records flow', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('link', { name: 'Records' }).click()
  await page.getByRole('button', { name: 'Add Record' }).click()
  await page.getByRole('button', { name: 'Save Record' }).click()
  await expect(page.getByText('Please fill in all required fields')).toBeVisible()
  await page.getByRole('link', { name: 'Analysis' }).click()
  await expect(page.getByText('Analysis')).toBeVisible()
})
