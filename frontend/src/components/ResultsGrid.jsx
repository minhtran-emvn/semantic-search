import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

import AudioCard from './AudioCard';

const INITIAL_COUNT = 20;
const PAGE_SIZE = 20;

function ResultsGrid({ results, isLoading }) {
  const [displayCount, setDisplayCount] = useState(INITIAL_COUNT);

  useEffect(() => {
    setDisplayCount(INITIAL_COUNT);
  }, [results]);

  if (isLoading) {
    return (
      <div className="grid w-full grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <div
            key={index}
            className="h-40 animate-pulse rounded-2xl border border-slate-700 bg-slate-800/60"
          />
        ))}
      </div>
    );
  }

  if (!results.length) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-10 text-center text-slate-300">
        No results found. Try a different description.
      </div>
    );
  }

  const visibleResults = results.slice(0, displayCount);

  return (
    <div className="w-full">
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {visibleResults.map((result) => (
          <AudioCard key={result.filename} result={result} />
        ))}
      </div>
      {results.length > displayCount && (
        <div className="mt-8 flex justify-center">
          <button
            type="button"
            onClick={() => setDisplayCount((count) => count + PAGE_SIZE)}
            className="rounded-full border border-slate-600 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:border-slate-400"
          >
            Show More
          </button>
        </div>
      )}
    </div>
  );
}

ResultsGrid.propTypes = {
  results: PropTypes.arrayOf(
    PropTypes.shape({
      filename: PropTypes.string.isRequired,
      similarity: PropTypes.number.isRequired,
      audio_url: PropTypes.string.isRequired
    })
  ).isRequired,
  isLoading: PropTypes.bool
};

ResultsGrid.defaultProps = {
  isLoading: false
};

export default ResultsGrid;
