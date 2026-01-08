import { useState } from 'react';
import PropTypes from 'prop-types';

import { API_BASE_URL } from '../config';

function AudioCard({ result }) {
  const [playbackError, setPlaybackError] = useState(false);

  const similarityPercentage = Number.isFinite(result.similarity)
    ? (result.similarity * 100).toFixed(1)
    : '0.0';
  const sourceUrl = result.audio_url?.startsWith('http')
    ? result.audio_url
    : `${API_BASE_URL}${result.audio_url}`;

  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-800/80 p-5 shadow-lg transition hover:border-slate-500">
      <div className="flex items-start justify-between gap-4">
        <h3 className="text-base font-semibold text-slate-100">
          {result.filename}
        </h3>
        <span className="rounded-full bg-slate-700 px-3 py-1 text-xs font-semibold text-slate-200">
          {similarityPercentage}%
        </span>
      </div>
      <div className="mt-4">
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
      {playbackError && (
        <p className="mt-3 text-sm text-red-300">
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
    audio_url: PropTypes.string.isRequired
  }).isRequired
};

export default AudioCard;
