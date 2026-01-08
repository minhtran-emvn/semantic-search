import SearchBar from './components/SearchBar';
import ResultsGrid from './components/ResultsGrid';
import useSearch from './hooks/useSearch';
import { DEFAULT_TOP_K } from './config';

function App() {
  const { results, isLoading, error, performSearch } = useSearch();

  const handleSearch = (query) => {
    performSearch(query, DEFAULT_TOP_K);
  };

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

        <SearchBar onSearch={handleSearch} isLoading={isLoading} />

        {error && (
          <p className="mt-8 text-center font-base-bold text-danger-100">
            {error}
          </p>
        )}

        <div className="mt-10 w-full">
          <ResultsGrid results={results} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}

export default App;
