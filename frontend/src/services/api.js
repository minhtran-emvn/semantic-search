import { API_BASE_URL } from '../config';

/**
 * Perform a semantic audio search.
 *
 * @param {string} query - Natural language query string.
 * @param {number} topK - Number of top results to return.
 * @param {string|null} contentType - Optional content type override ("song" | "sfx").
 * @returns {Promise<object>} Search response payload.
 */
export async function searchAudio(query, topK = 20, contentType = null) {
  const payload = {
    query,
    top_k: topK
  };

  if (contentType) {
    payload.content_type = contentType;
  }

  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    let errorDetail = 'Search request failed';
    try {
      const errorBody = await response.json();
      if (errorBody?.detail) {
        errorDetail = errorBody.detail;
      }
    } catch (err) {
      // Ignore JSON parse errors and use fallback message.
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

/**
 * Fetch example prompts with optional localization.
 *
 * @param {string|null} lang - Language code (e.g. "en", "es").
 * @returns {Promise<object>} Example prompts response payload.
 */
export async function fetchExamplePrompts(lang = null) {
  const query = lang ? `?lang=${encodeURIComponent(lang)}` : '';
  const response = await fetch(`${API_BASE_URL}/api/example-prompts${query}`);

  if (!response.ok) {
    throw new Error('Example prompts request failed');
  }

  return response.json();
}

/**
 * Check backend health status.
 *
 * @returns {Promise<object>} Health response payload.
 */
export async function healthCheck() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  } catch (err) {
    throw new Error('Unable to reach backend');
  }
}
