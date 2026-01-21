import { test, expect } from '@playwright/test';

test('content type toggle re-executes search', async ({ page }) => {
  await page.goto('http://localhost:5173');

  const input = page.getByPlaceholder(/Describe the music you need/i);
  await input.fill('dramatic explosion');
  await page.getByRole('button', { name: /search/i }).click();

  const chip = page.getByRole('button', { name: /Searching:/i });
  await expect(chip).toBeVisible();

  await chip.click();
  await expect(page.getByText('Searching: Songs')).toBeVisible();
});
