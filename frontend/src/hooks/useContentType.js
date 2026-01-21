import { useCallback, useState } from 'react';

const STORAGE_KEY = 'promptSearchContentType';

const getInitialState = () => {
  if (typeof window === 'undefined') {
    return { contentType: 'song', hasManualOverride: false };
  }

  const stored = sessionStorage.getItem(STORAGE_KEY);
  if (stored === 'song' || stored === 'sfx') {
    return { contentType: stored, hasManualOverride: true };
  }

  return { contentType: 'song', hasManualOverride: false };
};

export default function useContentType() {
  const initialState = getInitialState();
  const [contentType, setContentType] = useState(initialState.contentType);
  const [hasManualOverride, setHasManualOverride] = useState(
    initialState.hasManualOverride
  );

  const updateContentType = useCallback((newType, isManual = false) => {
    setContentType(newType);

    if (isManual) {
      setHasManualOverride(true);
      if (typeof window !== 'undefined') {
        sessionStorage.setItem(STORAGE_KEY, newType);
      }
      return;
    }

    if (hasManualOverride && typeof window !== 'undefined') {
      sessionStorage.removeItem(STORAGE_KEY);
      setHasManualOverride(false);
    }
  }, [hasManualOverride]);

  const applyAutoDetection = useCallback(
    (detectedType) => {
      if (!detectedType) {
        return;
      }
      // Always update the content type from backend detection
      // This ensures the UI reflects what the backend is actually searching
      if (detectedType !== contentType) {
        setContentType(detectedType);
      }
      // Clear manual override if the detected type matches the manual selection
      // This allows auto-detection to work again for future searches
      if (hasManualOverride && detectedType === contentType) {
        // User's manual choice matches auto-detection, clear the override
        setHasManualOverride(false);
        if (typeof window !== 'undefined') {
          sessionStorage.removeItem(STORAGE_KEY);
        }
      }
    },
    [contentType, hasManualOverride]
  );

  const clearManualOverride = useCallback(() => {
    setHasManualOverride(false);
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  return {
    contentType,
    hasManualOverride,
    updateContentType,
    applyAutoDetection,
    clearManualOverride
  };
}
