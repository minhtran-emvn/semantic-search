import { test, expect } from '@playwright/test';

test('non-english search shows translation indicator', async ({ page }) => {
  await page.goto('http://localhost:5173');

  const input = page.getByPlaceholder(/Describe the music you need/i);
  await input.fill('música relajante para yoga');
  await page.getByRole('button', { name: /search/i }).click();

  await expect(page.getByText('Translating...')).toBeVisible();
  await expect(input).toHaveValue('música relajante para yoga');
});
