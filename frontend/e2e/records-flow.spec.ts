import { expect, test } from '@playwright/test'

test('records flow', async ({ page }) => {
  const today = new Date().toISOString().slice(0, 10)

  await page.goto('/records')

  await page.getByRole('button', { name: 'Add Record' }).click()
  const dialog = page.getByRole('dialog')

  await dialog.locator('.form-group', { hasText: 'Date *' }).locator('input').fill(today)
  await dialog.locator('.form-group', { hasText: 'Weight (kg) *' }).locator('input').fill('75.0')
  await dialog.locator('.form-group', { hasText: 'Sleep Hours *' }).locator('input').fill('7')
  await dialog.locator('.form-group', { hasText: 'Calories (kcal) *' }).locator('input').fill('2200')

  await dialog.getByRole('button', { name: 'Save Record' }).click()
  await expect(page.getByText('Record saved successfully.')).toBeVisible()

  await expect(page.getByRole('cell', { name: today })).toBeVisible()

  await page.getByRole('link', { name: 'Dashboard' }).click()
  await expect(page.getByText(`Last record: ${today}`)).toBeVisible()

  await page.getByRole('link', { name: 'Analysis' }).click()
  await expect(page.getByRole('heading', { name: 'Analysis' })).toBeVisible()
})
