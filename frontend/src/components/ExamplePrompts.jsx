import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

import { fetchExamplePrompts } from '../services/api';
import SearchTips from './SearchTips';

function ExamplePrompts({ onSelectPrompt, isVisible }) {
  const [prompts, setPrompts] = useState([]);
  const [searchTips, setSearchTips] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const loadPrompts = async () => {
      try {
        const lang = navigator.language?.split('-')[0] || 'en';
        const response = await fetchExamplePrompts(lang);
        if (isMounted) {
          setPrompts(Array.isArray(response?.prompts) ? response.prompts : []);
          setSearchTips(Array.isArray(response?.search_tips) ? response.search_tips : []);
        }
      } catch (err) {
        if (isMounted) {
          setError('Unable to load example prompts');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadPrompts();
    return () => {
      isMounted = false;
    };
  }, []);

  if (!isVisible) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="mt-4 w-full max-w-3xl text-sm text-text-400">
        Loading example prompts...
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-4 w-full max-w-3xl text-sm text-danger-100">
        {error}
      </div>
    );
  }

  return (
    <>
      <div className="mt-4 grid w-full max-w-3xl gap-3 md:grid-cols-2">
        {prompts.map((prompt) => (
          <button
            key={`${prompt.category}-${prompt.text}`}
            type="button"
            onClick={() => onSelectPrompt(prompt.text)}
            className="rounded-[0.75rem] border border-border-300/20 bg-bg-000 px-4 py-3 text-left shadow-card transition duration-150 hover:-translate-y-[1px] hover:border-border-300/40"
          >
            <span className="text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-text-400">
              {prompt.category}
            </span>
            <p className="mt-2 text-sm text-text-200">{prompt.text}</p>
          </button>
        ))}
      </div>
      <SearchTips tips={searchTips} isVisible={isVisible} />
    </>
  );
}

ExamplePrompts.propTypes = {
  onSelectPrompt: PropTypes.func.isRequired,
  isVisible: PropTypes.bool
};

ExamplePrompts.defaultProps = {
  isVisible: true
};

export default ExamplePrompts;
