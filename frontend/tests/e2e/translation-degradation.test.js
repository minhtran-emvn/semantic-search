import { test, expect } from '@playwright/test';

test('translation degradation shows warning', async ({ page }) => {
  await page.route('**/api/search', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: [],
        query: 'sonido',
        num_results: 0,
        content_type: 'song',
        original_query: 'sonido',
        was_translated: false,
        translation_warning:
          'Translation unavailable. Searching with original text may yield less accurate results.'
      })
    });
  });

  await page.goto('http://localhost:5173');

  const input = page.getByPlaceholder(/Describe the music you need/i);
  await input.fill('sonido');
  await page.getByRole('button', { name: /search/i }).click();

  await expect(
    page.getByText(/Translation unavailable/i)
  ).toBeVisible();
});
