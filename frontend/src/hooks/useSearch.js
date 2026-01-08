import { useState } from 'react';

import { DEFAULT_TOP_K } from '../config';
import { searchAudio } from '../services/api';

export default function useSearch() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const performSearch = async (query, topK = DEFAULT_TOP_K) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await searchAudio(query, topK);
      setResults(Array.isArray(response?.results) ? response.results : []);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Unable to complete search';
      setError(message);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    results,
    isLoading,
    error,
    performSearch
  };
}
