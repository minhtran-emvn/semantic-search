import { useState } from 'react';
import PropTypes from 'prop-types';

function SearchBar({ onSearch, isLoading }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) {
      return;
    }
    onSearch(trimmed);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex w-full max-w-2xl items-center gap-3"
    >
      <input
        type="text"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Describe the sound you need..."
        className="flex-1 rounded-[0.625rem] border border-border-300/15 bg-bg-000 px-5 py-3 font-base text-text-100 shadow-card focus:border-accent-secondary-100/40 focus:outline-none focus:ring-2 focus:ring-accent-secondary-100/20 placeholder:text-text-400 disabled:bg-bg-100 disabled:text-text-400"
        disabled={isLoading}
      />
      <button
        type="submit"
        className="rounded-[0.625rem] bg-[#d97757] px-5 py-3 font-base-bold text-always-white shadow-[0_2px_8px_0_hsl(var(--accent-secondary-200)/16%)] transition duration-150 hover:bg-[#c6613f] disabled:cursor-not-allowed disabled:opacity-60"
        disabled={isLoading}
      >
        {isLoading ? 'Searching...' : 'Search'}
      </button>
    </form>
  );
}

SearchBar.propTypes = {
  onSearch: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

SearchBar.defaultProps = {
  isLoading: false
};

export default SearchBar;
