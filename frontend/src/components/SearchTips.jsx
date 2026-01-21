import PropTypes from 'prop-types';

function SearchTips({ tips, isVisible }) {
  if (!isVisible || !tips || tips.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 w-full max-w-3xl">
      <div className="rounded-[0.75rem] border border-border-300/20 bg-bg-000/50 px-4 py-3">
        <p className="text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-text-400 mb-2">
          Search Tips
        </p>
        <div className="space-y-2">
          {tips.map((tip, index) => (
            <div key={index} className="text-sm">
              <span className="text-text-400">Instead of </span>
              <span className="text-danger-100 line-through">&quot;{tip.bad}&quot;</span>
              <span className="text-text-400"> try </span>
              <span className="text-success-100">&quot;{tip.good}&quot;</span>
              <span className="text-text-500 text-xs ml-2">({tip.reason})</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

SearchTips.propTypes = {
  tips: PropTypes.arrayOf(
    PropTypes.shape({
      bad: PropTypes.string.isRequired,
      good: PropTypes.string.isRequired,
      reason: PropTypes.string.isRequired
    })
  ),
  isVisible: PropTypes.bool
};

SearchTips.defaultProps = {
  tips: [],
  isVisible: true
};

export default SearchTips;
