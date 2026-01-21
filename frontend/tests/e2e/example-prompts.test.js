import { test, expect } from '@playwright/test';

test('example prompts flow', async ({ page }) => {
  await page.goto('http://localhost:5173');

  const promptButton = page.getByRole('button', { name: /Upbeat electronic instrumental/i });
  await expect(promptButton).toBeVisible();

  await promptButton.click();
  const input = page.getByPlaceholder(/Describe the music you need/i);
  await expect(input).toHaveValue(/Upbeat electronic instrumental/i);
});
