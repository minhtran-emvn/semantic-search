import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';

import ExamplePrompts from '../../src/components/ExamplePrompts';

const mockFetchExamplePrompts = vi.fn();

vi.mock('../../src/services/api', () => ({
  fetchExamplePrompts: (...args) => mockFetchExamplePrompts(...args)
}));

describe('ExamplePrompts', () => {
  beforeEach(() => {
    mockFetchExamplePrompts.mockReset();
  });

  it('fetches and renders prompts on mount', async () => {
    mockFetchExamplePrompts.mockResolvedValue({
      prompts: [
        { category: 'Mood/Emotion', text: 'Melancholic piano' },
        { category: 'Genre/Style', text: 'Upbeat electronic' },
        { category: 'Use-Case', text: 'Background music' },
        { category: 'Sound Effects', text: 'Subtle ambience' }
      ]
    });

    render(<ExamplePrompts onSelectPrompt={() => {}} isVisible={true} />);

    expect(await screen.findByText('Melancholic piano')).toBeInTheDocument();
    expect(screen.getAllByRole('button')).toHaveLength(4);
  });

  it('calls onSelectPrompt when a prompt is clicked', async () => {
    const onSelectPrompt = vi.fn();
    mockFetchExamplePrompts.mockResolvedValue({
      prompts: [{ category: 'Mood/Emotion', text: 'Melancholic piano' }]
    });

    render(<ExamplePrompts onSelectPrompt={onSelectPrompt} isVisible={true} />);

    const button = await screen.findByRole('button');
    fireEvent.click(button);
    expect(onSelectPrompt).toHaveBeenCalledWith('Melancholic piano');
  });

  it('renders nothing when isVisible is false', () => {
    render(<ExamplePrompts onSelectPrompt={() => {}} isVisible={false} />);
    expect(screen.queryByRole('button')).toBeNull();
  });
});
