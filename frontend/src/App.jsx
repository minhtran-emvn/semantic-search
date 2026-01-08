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
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-slate-100">
      <div className="mx-auto flex w-full max-w-6xl flex-col items-center px-6 py-16">
        <header className="mb-12 text-center">
          <p className="text-sm uppercase tracking-[0.4em] text-slate-400">
            Sound Library
          </p>
          <h1 className="mt-4 text-4xl font-semibold text-white md:text-5xl">
            Semantic Audio Search
          </h1>
          <p className="mt-4 max-w-2xl text-base text-slate-300">
            Type a description and discover the closest matching sound clips in
            seconds.
          </p>
        </header>

        <SearchBar onSearch={handleSearch} isLoading={isLoading} />

        {error && (
          <p className="mt-8 text-center text-sm font-semibold text-red-300">
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
