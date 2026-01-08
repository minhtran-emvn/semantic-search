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
    <div className="px-5 py-4 transition duration-150 hover:bg-bg-200/60">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:gap-6">
        <div className="flex items-center justify-between gap-4 md:w-[45%] md:flex-col md:items-start md:gap-2">
          <div className="min-w-0">
            <h3 className="font-large-bold text-text-100 truncate">
              {result.filename}
            </h3>
            <p className="mt-1 font-small-bold uppercase tracking-[0.18em] text-text-400">
              Audio Clip
            </p>
          </div>
          <span className="rounded-full bg-bg-200 px-3 py-1 text-[0.7rem] font-semibold text-text-300 md:hidden">
            {similarityPercentage}%
          </span>
        </div>
        <div className="hidden md:flex md:w-[15%] md:justify-end">
          <span className="rounded-full bg-bg-200 px-3 py-1 text-[0.7rem] font-semibold text-text-300">
            {similarityPercentage}%
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
    audio_url: PropTypes.string.isRequired
  }).isRequired
};

export default AudioCard;
