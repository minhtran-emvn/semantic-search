import { useCallback, useState } from 'react';

import { DEFAULT_TOP_K } from '../config';
import { searchAudio } from '../services/api';
import useContentType from './useContentType';

export default function useSearch() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState(null);
  const [translationWarning, setTranslationWarning] = useState(null);
  const [lastQuery, setLastQuery] = useState('');
  const {
    contentType,
    hasManualOverride,
    updateContentType,
    applyAutoDetection,
    clearManualOverride
  } = useContentType();

  const performSearch = useCallback(async (query, topK = DEFAULT_TOP_K, manualType = null) => {
    setIsLoading(true);
    setIsTranslating(true);
    setError(null);
    setTranslationWarning(null);

    // Check if this is a new query (not just toggling content type)
    const isNewQuery = query !== lastQuery;
    setLastQuery(query);

    try {
      // If this is a new query and no explicit manualType was passed,
      // let the backend auto-detect the content type
      let resolvedType = manualType;
      if (!manualType && !isNewQuery && hasManualOverride) {
        // Only preserve manual override for same query (e.g., toggling)
        resolvedType = contentType;
      }
      // For new queries, resolvedType stays null to allow auto-detection

      const response = await searchAudio(query, topK, resolvedType);
      setResults(Array.isArray(response?.results) ? response.results : []);
      setTranslationWarning(response?.translation_warning || null);

      if (response?.content_type) {
        applyAutoDetection(response.content_type);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Unable to complete search';
      setError(message);
      setResults([]);
    } finally {
      setIsLoading(false);
      setIsTranslating(false);
    }
  }, [applyAutoDetection, contentType, hasManualOverride, lastQuery]);

  const toggleContentType = useCallback(() => {
    const newType = contentType === 'song' ? 'sfx' : 'song';
    updateContentType(newType, true);

    if (lastQuery) {
      performSearch(lastQuery, DEFAULT_TOP_K, newType);
    }
  }, [contentType, lastQuery, performSearch, updateContentType]);

  const resetContentType = useCallback(() => {
    clearManualOverride();
    if (lastQuery) {
      performSearch(lastQuery, DEFAULT_TOP_K, null);
    }
  }, [clearManualOverride, lastQuery, performSearch]);

  return {
    results,
    isLoading,
    isTranslating,
    error,
    translationWarning,
    contentType,
    hasManualOverride,
    performSearch,
    toggleContentType,
    resetContentType
  };
}
