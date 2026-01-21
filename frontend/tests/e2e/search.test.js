import { test, expect } from '@playwright/test';

test('english search flow', async ({ page }) => {
  await page.goto('http://localhost:5173');

  const input = page.getByPlaceholder(/Describe the music you need/i);
  await input.fill('relaxing piano music');
  await page.getByRole('button', { name: /search/i }).click();

  await expect(page.getByText('Searching: Songs')).toBeVisible();
  await expect(page.getByText(/Match/)).toBeVisible();
  await expect(page.getByText(/Song|SFX/)).toBeVisible();
});
