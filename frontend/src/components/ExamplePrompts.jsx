import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

import { fetchExamplePrompts } from '../services/api';
import SearchTips from './SearchTips';

function ExamplePrompts({ isVisible }) {
  const [searchTips, setSearchTips] = useState([]);
  const [tipHeader, setTipHeader] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const loadPrompts = async () => {
      try {
        const lang = navigator.language?.split('-')[0] || 'en';
        const response = await fetchExamplePrompts(lang);
        if (isMounted) {
          setSearchTips(Array.isArray(response?.search_tips) ? response.search_tips : []);
          setTipHeader(response?.tip_header || '');
        }
      } catch (err) {
        if (isMounted) {
          setError('Unable to load search tips');
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
        Loading...
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
    <SearchTips tips={searchTips} tipHeader={tipHeader} isVisible={isVisible} />
  );
}

ExamplePrompts.propTypes = {
  isVisible: PropTypes.bool
};

ExamplePrompts.defaultProps = {
  isVisible: true
};

export default ExamplePrompts;
