import { useState } from 'react';
import { SearchBar } from './SearchBar';
import { CatalogHeading } from './CatalogHeading';

type Props = { initialQuery: string; total: number; directoryTotal: number; initialSort: string; filters: Record<string, string> };

export function ResearcherSearch({ initialQuery, total, directoryTotal, initialSort, filters }: Props) {
  const [query, setQuery] = useState(initialQuery);
  return <form method="get" role="search">
    {Object.entries(filters).filter(([, value]) => value).map(([name, value]) => <input key={name} type="hidden" name={name} value={value}/>)}
    <CatalogHeading title="Researchers" titleId="researchers-title" count={`${total} of ${directoryTotal}`}
      countLabel={`${total} researcher${total === 1 ? '' : 's'}${initialQuery ? ` matching “${initialQuery}”` : ''}`}
      search={<SearchBar value={query} onChange={value => {
        setQuery(value);
        if (!value && initialQuery) {
          const url = new URL(window.location.href);
          url.searchParams.delete('q');
          url.searchParams.delete('page');
          window.location.assign(url.toString());
        }
      }} name="q" maxLength={200} label="Search researchers by name, username, university, or research interest"
        placeholder="Search researchers…" helpId="researcher-search-help"/>}
      sort={<label className="catalog-sort">Sort by <select name="sort" defaultValue={initialSort} onChange={event => event.currentTarget.form?.requestSubmit()}><option value="name">Name (A–Z)</option><option value="joined">Recently joined</option></select></label>}/>
    <button className="sr-only" type="submit">Search</button>
  </form>;
}
