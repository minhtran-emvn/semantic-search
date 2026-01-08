import { API_BASE_URL } from '../config';

/**
 * Perform a semantic audio search.
 *
 * @param {string} query - Natural language query string.
 * @param {number} topK - Number of top results to return.
 * @returns {Promise<object>} Search response payload.
 */
export async function searchAudio(query, topK = 20) {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query,
      top_k: topK
    })
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
