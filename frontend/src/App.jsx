import { useState } from 'react';

import ContentTypeFilter from './components/ContentTypeFilter';
import ExamplePrompts from './components/ExamplePrompts';
import SearchBar from './components/SearchBar';
import ResultsGrid from './components/ResultsGrid';
import useSearch from './hooks/useSearch';
import { DEFAULT_TOP_K } from './config';

function App() {
  const {
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
  } = useSearch();
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);

  const handleSearch = (query) => {
    performSearch(query, DEFAULT_TOP_K);
  };

  const showTips = searchQuery.trim().length === 0;

  return (
    <div className="min-h-screen bg-gradient-to-b from-bg-100 via-bg-100 to-bg-200 text-text-100">
      <div className="mx-auto flex w-full max-w-5xl flex-col items-center px-6 py-14 md:px-10">
        <header className="mb-10 text-center">
          <p className="font-small-bold uppercase tracking-[0.32em] text-text-400">
            Sound Library
          </p>
          <h1 className="mt-4 font-display text-text-100">
            Semantic Audio Search
          </h1>
          <p className="font-base mt-4 max-w-2xl text-text-400">
            Type a description and discover the closest matching sound clips in
            seconds.
          </p>
        </header>

        <SearchBar
          onSearch={handleSearch}
          isLoading={isLoading}
          isTranslating={isTranslating}
          query={searchQuery}
          onQueryChange={setSearchQuery}
          onFocusChange={setIsSearchFocused}
        />

        <ExamplePrompts
          isVisible={showTips || isSearchFocused}
        />

        <div className="mt-6 w-full max-w-3xl">
          <ContentTypeFilter
            contentType={contentType}
            onToggle={toggleContentType}
            onAuto={resetContentType}
            isManual={hasManualOverride}
            isLoading={isLoading}
          />
        </div>

        {error && (
          <p className="mt-8 text-center font-base-bold text-danger-100">
            {error}
          </p>
        )}

        <div className="mt-10 w-full">
          {translationWarning && (
            <div className="mb-4 rounded-[0.75rem] border border-warning-200/40 bg-warning-900 px-4 py-3 text-sm text-warning-100">
              {translationWarning}
            </div>
          )}
          <ResultsGrid results={results} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}

export default App;
