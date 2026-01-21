import { renderHook, act } from '@testing-library/react';

import useContentType from '../../src/hooks/useContentType';

describe('useContentType', () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it('defaults to song when no session override', () => {
    const { result } = renderHook(() => useContentType());
    expect(result.current.contentType).toBe('song');
    expect(result.current.hasManualOverride).toBe(false);
  });

  it('persists manual override to sessionStorage', () => {
    const { result } = renderHook(() => useContentType());
    act(() => {
      result.current.updateContentType('sfx', true);
    });

    expect(sessionStorage.getItem('promptSearchContentType')).toBe('sfx');
    expect(result.current.hasManualOverride).toBe(true);
  });

  it('applies auto detection when no manual override', () => {
    const { result } = renderHook(() => useContentType());
    act(() => {
      result.current.applyAutoDetection('sfx');
    });

    expect(result.current.contentType).toBe('sfx');
  });

  it('ignores auto detection when manual override exists', () => {
    const { result } = renderHook(() => useContentType());
    act(() => {
      result.current.updateContentType('sfx', true);
    });
    act(() => {
      result.current.applyAutoDetection('song');
    });

    expect(result.current.contentType).toBe('sfx');
  });

  it('clears manual override', () => {
    const { result } = renderHook(() => useContentType());
    act(() => {
      result.current.updateContentType('sfx', true);
    });
    act(() => {
      result.current.clearManualOverride();
    });

    expect(sessionStorage.getItem('promptSearchContentType')).toBeNull();
    expect(result.current.hasManualOverride).toBe(false);
  });
});
