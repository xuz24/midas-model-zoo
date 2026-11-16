import type { ReactNode } from 'react';

export function EmptyState({ title, children, onReset }: { title: string; children: ReactNode; onReset?: () => void }) {
  return <div className="empty-state">
    <h3>{title}</h3>
    <p>{children}</p>
    {onReset && <button className="button button-secondary" type="button" onClick={onReset}>Clear all filters</button>}
  </div>;
}
