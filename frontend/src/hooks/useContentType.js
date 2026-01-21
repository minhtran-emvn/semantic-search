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
      if (hasManualOverride || !detectedType) {
        return;
      }
      if (detectedType !== contentType) {
        setContentType(detectedType);
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
