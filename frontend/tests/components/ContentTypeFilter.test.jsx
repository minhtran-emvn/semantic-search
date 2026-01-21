import { fireEvent, render, screen } from '@testing-library/react';
import { vi } from 'vitest';

import ContentTypeFilter from '../../src/components/ContentTypeFilter';

describe('ContentTypeFilter', () => {
  it('renders songs label when contentType is song', () => {
    render(
      <ContentTypeFilter
        contentType="song"
        onToggle={() => {}}
        onAuto={() => {}}
        isLoading={false}
      />
    );

    expect(screen.getByText('Searching: Songs')).toBeInTheDocument();
  });

  it('renders sfx label when contentType is sfx', () => {
    render(
      <ContentTypeFilter
        contentType="sfx"
        onToggle={() => {}}
        onAuto={() => {}}
        isLoading={false}
      />
    );

    expect(screen.getByText('Searching: SFX')).toBeInTheDocument();
  });

  it('fires onToggle when clicked', () => {
    const onToggle = vi.fn();
    render(
      <ContentTypeFilter
        contentType="song"
        onToggle={onToggle}
        onAuto={() => {}}
        isLoading={false}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /searching/i }));
    expect(onToggle).toHaveBeenCalledTimes(1);
  });

  it('disables button when loading', () => {
    render(
      <ContentTypeFilter
        contentType="song"
        onToggle={() => {}}
        onAuto={() => {}}
        isLoading={true}
      />
    );

    expect(screen.getByRole('button', { name: /searching/i })).toBeDisabled();
  });

  it('disables auto when not manual', () => {
    render(
      <ContentTypeFilter
        contentType="song"
        onToggle={() => {}}
        onAuto={() => {}}
        isManual={false}
        isLoading={false}
      />
    );

    expect(screen.getByRole('button', { name: /auto/i })).toBeDisabled();
  });
});
