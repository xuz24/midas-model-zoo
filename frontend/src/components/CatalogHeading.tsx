import type { ReactNode } from 'react';

type Props = {
  title: string;
  titleId?: string;
  count: string;
  countLabel: string;
  search: ReactNode;
  sort: ReactNode;
};

export function CatalogHeading({ title, titleId, count, countLabel, search, sort }: Props) {
  return <div className="catalog-heading-line">
    <div className="catalog-heading-title">
      <h1 id={titleId}>{title}<span className="maize-dot">.</span></h1>
      <span className="catalog-heading-count" role="status" aria-live="polite" aria-label={countLabel}>{count}</span>
    </div>
    <div className="catalog-heading-search">{search}</div>
    {sort}
  </div>;
}
