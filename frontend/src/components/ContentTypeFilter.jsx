import PropTypes from 'prop-types';

function ContentTypeFilter({
  contentType,
  onToggle,
  onAuto,
  isLoading,
  isManual
}) {
  const isSong = contentType === 'song';
  const variantClasses = isSong
    ? 'border-accent-main-100/40 bg-accent-main-100/10 text-accent-main-100'
    : 'border-accent-secondary-100/40 bg-accent-secondary-100/10 text-accent-secondary-100';
  const autoClasses = isManual
    ? 'border-border-300/40 text-text-200 hover:border-border-300/70'
    : 'border-border-300/20 text-text-500';

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        onClick={onToggle}
        disabled={isLoading}
        className={`inline-flex items-center gap-2 rounded-full border px-4 py-2 text-[0.7rem] font-semibold uppercase tracking-[0.18em] transition duration-150 hover:-translate-y-[1px] disabled:cursor-not-allowed disabled:opacity-60 ${variantClasses}`}
      >
        Searching: {isSong ? 'Songs' : 'SFX'}
        <span aria-hidden="true">⇄</span>
      </button>
      <button
        type="button"
        onClick={onAuto}
        disabled={!isManual || isLoading}
        className={`rounded-full border px-3 py-2 text-[0.65rem] font-semibold uppercase tracking-[0.25em] transition duration-150 disabled:cursor-not-allowed disabled:opacity-50 ${autoClasses}`}
      >
        Auto
      </button>
    </div>
  );
}

ContentTypeFilter.propTypes = {
  contentType: PropTypes.oneOf(['song', 'sfx']).isRequired,
  onToggle: PropTypes.func.isRequired,
  onAuto: PropTypes.func.isRequired,
  isManual: PropTypes.bool,
  isLoading: PropTypes.bool
};

ContentTypeFilter.defaultProps = {
  isManual: false,
  isLoading: false
};

export default ContentTypeFilter;
