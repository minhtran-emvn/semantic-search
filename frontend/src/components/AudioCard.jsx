import { useState } from 'react';
import PropTypes from 'prop-types';

import { API_BASE_URL } from '../config';

function AudioCard({ result }) {
  const [playbackError, setPlaybackError] = useState(false);

  const similarityValue = Number.isFinite(result.similarity)
    ? result.similarity
    : 0;
  const similarityPercentage = (similarityValue * 100).toFixed(1);
  const sourceUrl = result.audio_url?.startsWith('http')
    ? result.audio_url
    : `${API_BASE_URL}${result.audio_url}`;
  const contentTypeLabel = result.content_type === 'sfx' ? '🔊 SFX' : '🎵 Song';

  const getSimilarityBadge = (score) => {
    if (score >= 0.9) {
      return { label: 'Excellent Match', className: 'bg-success-900 text-success-100' };
    }
    if (score >= 0.75) {
      return { label: 'Good Match', className: 'bg-accent-secondary-900 text-accent-secondary-100' };
    }
    if (score >= 0.6) {
      return { label: 'Fair Match', className: 'bg-warning-900 text-warning-100' };
    }
    return { label: 'Low Match', className: 'bg-bg-200 text-text-300' };
  };

  const similarityBadge = getSimilarityBadge(similarityValue);

  return (
    <div className="px-5 py-4 transition duration-150 hover:bg-bg-200/60">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:gap-6">
        <div className="flex items-center justify-between gap-4 md:w-[45%] md:flex-col md:items-start md:gap-2">
          <div className="min-w-0">
            <h3 className="font-large-bold text-text-100 truncate">
              {result.filename}
            </h3>
            <div className="mt-1 flex items-center gap-2">
              <span className="font-small-bold uppercase tracking-[0.18em] text-text-400">
                {contentTypeLabel}
              </span>
              {result.folder && (
                <span className="text-xs text-text-500 truncate max-w-[150px]" title={result.folder}>
                  📁 {result.folder}
                </span>
              )}
            </div>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-[0.7rem] font-semibold md:hidden ${similarityBadge.className}`}
          >
            {similarityBadge.label} · {similarityPercentage}%
          </span>
        </div>
        <div className="hidden md:flex md:w-[15%] md:justify-end">
          <span
            className={`rounded-full px-3 py-1 text-[0.7rem] font-semibold ${similarityBadge.className}`}
          >
            {similarityBadge.label} · {similarityPercentage}%
          </span>
        </div>
        <div className="md:flex-1">
          <audio
            controls
            preload="metadata"
            onError={() => setPlaybackError(true)}
            className="w-full"
          >
            <source src={sourceUrl} />
            Your browser does not support the audio element.
          </audio>
        </div>
      </div>
      {playbackError && (
        <p className="mt-2 font-base text-danger-100">
          Playback failed. Please check the audio file.
        </p>
      )}
    </div>
  );
}

AudioCard.propTypes = {
  result: PropTypes.shape({
    filename: PropTypes.string.isRequired,
    similarity: PropTypes.number.isRequired,
    audio_url: PropTypes.string.isRequired,
    content_type: PropTypes.oneOf(['song', 'sfx']).isRequired,
    folder: PropTypes.string
  }).isRequired
};

export default AudioCard;
