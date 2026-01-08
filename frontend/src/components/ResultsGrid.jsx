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
      <div className="w-full rounded-[0.9rem] border border-border-300/20 bg-bg-000/60">
        <div className="hidden md:flex items-center gap-6 border-b border-border-300/15 px-5 py-3 text-[0.65rem] uppercase tracking-[0.32em] text-text-400">
          <span className="w-[45%]">Track</span>
          <span className="w-[15%] text-right">Match</span>
          <span className="flex-1">Preview</span>
        </div>
        <div className="divide-y divide-border-300/15">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="animate-pulse px-5 py-4">
              <div className="flex flex-col gap-3 md:flex-row md:items-center md:gap-6">
                <div className="h-4 w-48 rounded bg-bg-200" />
                <div className="h-6 w-20 rounded-full bg-bg-200 md:ml-auto md:w-16" />
                <div className="h-10 w-full rounded-md bg-bg-200 md:flex-1" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!results.length) {
    return (
      <div className="rounded-[0.9rem] border border-dashed border-border-300/20 bg-bg-000/60 p-10 text-center font-base text-text-300">
        No results found. Try a different description.
      </div>
    );
  }

  const visibleResults = results.slice(0, displayCount);

  return (
    <div className="w-full">
      <div className="rounded-[0.9rem] border border-border-300/20 bg-bg-000/60">
        <div className="hidden md:flex items-center gap-6 border-b border-border-300/15 px-5 py-3 text-[0.65rem] uppercase tracking-[0.32em] text-text-400">
          <span className="w-[45%]">Track</span>
          <span className="w-[15%] text-right">Match</span>
          <span className="flex-1">Preview</span>
        </div>
        <div className="divide-y divide-border-300/15">
          {visibleResults.map((result) => (
            <AudioCard key={result.filename} result={result} />
          ))}
        </div>
      </div>
      {results.length > displayCount && (
        <div className="mt-8 flex justify-center">
          <button
            type="button"
            onClick={() => setDisplayCount((count) => count + PAGE_SIZE)}
            className="rounded-[0.625rem] border border-border-300/30 bg-bg-100 px-5 py-2 font-base-bold text-text-200 transition duration-150 hover:bg-bg-200 hover:text-text-100"
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
