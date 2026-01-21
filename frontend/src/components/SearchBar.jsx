import { useState } from 'react';
import PropTypes from 'prop-types';

function SearchBar({
  onSearch,
  isLoading,
  isTranslating,
  query,
  onQueryChange,
  onFocusChange
}) {
  const [validationError, setValidationError] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) {
      setValidationError('Please enter a search query');
      return;
    }
    if (trimmed.length > 500) {
      setValidationError('Query must be 500 characters or less');
      return;
    }
    setValidationError('');
    onSearch(trimmed);
  };

  const showCharCount = query.length > 450;

  return (
    <form
      onSubmit={handleSubmit}
      className="flex w-full max-w-2xl flex-col gap-2"
    >
      <div className="flex w-full items-center gap-3">
        <input
          type="text"
          value={query}
          onChange={(event) => {
            onQueryChange(event.target.value);
            if (validationError) {
              setValidationError('');
            }
          }}
          onFocus={() => onFocusChange(true)}
          onBlur={() => onFocusChange(false)}
          placeholder="Describe the music you need or what it's for. Type in entire sync briefs, scene outlines, the vibe you're after, pop culture references or whatever comes to mind."
          className="flex-1 rounded-[0.625rem] border border-border-300/15 bg-bg-000 px-5 py-3 font-base text-text-100 shadow-card focus:border-accent-secondary-100/40 focus:outline-none focus:ring-2 focus:ring-accent-secondary-100/20 placeholder:text-text-400 disabled:bg-bg-100 disabled:text-text-400"
          disabled={isLoading}
          aria-invalid={Boolean(validationError)}
          aria-describedby={validationError ? 'search-error' : undefined}
        />
        <button
          type="submit"
          className="rounded-[0.625rem] bg-[#d97757] px-5 py-3 font-base-bold text-always-white shadow-[0_2px_8px_0_hsl(var(--accent-secondary-200)/16%)] transition duration-150 hover:bg-[#c6613f] disabled:cursor-not-allowed disabled:opacity-60"
          disabled={isLoading || isTranslating}
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </div>
      <div className="flex w-full items-center justify-between text-xs text-text-400">
        {isTranslating ? (
          <span className="animate-pulse">Translating...</span>
        ) : (
          <span />
        )}
        {showCharCount ? <span>{query.length}/500</span> : null}
      </div>
      {validationError ? (
        <div id="search-error" role="alert" className="text-xs text-danger-500">
          {validationError}
        </div>
      ) : null}
    </form>
  );
}

SearchBar.propTypes = {
  onSearch: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  isTranslating: PropTypes.bool,
  query: PropTypes.string.isRequired,
  onQueryChange: PropTypes.func.isRequired,
  onFocusChange: PropTypes.func.isRequired
};

SearchBar.defaultProps = {
  isLoading: false,
  isTranslating: false
};

export default SearchBar;
