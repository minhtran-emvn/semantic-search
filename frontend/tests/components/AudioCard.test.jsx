import { render, screen } from '@testing-library/react';

import AudioCard from '../../src/components/AudioCard';

const baseResult = {
  filename: 'test.wav',
  similarity: 0.95,
  audio_url: '/audio/test.wav',
  content_type: 'song'
};

describe('AudioCard', () => {
  it('renders song label for song content type', () => {
    render(<AudioCard result={{ ...baseResult, content_type: 'song' }} />);
    expect(screen.getByText('🎵 Song')).toBeInTheDocument();
  });

  it('renders sfx label for sfx content type', () => {
    render(<AudioCard result={{ ...baseResult, content_type: 'sfx' }} />);
    expect(screen.getByText('🔊 SFX')).toBeInTheDocument();
  });

  it('renders correct similarity badge for excellent match', () => {
    render(<AudioCard result={{ ...baseResult, similarity: 0.95 }} />);
    const badge = screen.getByText(/Excellent Match/);
    expect(badge).toHaveClass('bg-success-900');
  });

  it('renders correct similarity badge for good match', () => {
    render(<AudioCard result={{ ...baseResult, similarity: 0.8 }} />);
    const badge = screen.getByText(/Good Match/);
    expect(badge).toHaveClass('bg-accent-secondary-900');
  });

  it('renders correct similarity badge for fair match', () => {
    render(<AudioCard result={{ ...baseResult, similarity: 0.65 }} />);
    const badge = screen.getByText(/Fair Match/);
    expect(badge).toHaveClass('bg-warning-900');
  });

  it('renders correct similarity badge for low match', () => {
    render(<AudioCard result={{ ...baseResult, similarity: 0.5 }} />);
    const badge = screen.getByText(/Low Match/);
    expect(badge).toHaveClass('bg-bg-200');
  });

  it('renders similarity percentage', () => {
    render(<AudioCard result={{ ...baseResult, similarity: 0.95 }} />);
    expect(screen.getByText(/95\.0%/)).toBeInTheDocument();
  });
});
