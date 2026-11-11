import { useState } from 'react';
import { catalogLabels, filterCatalog, type CatalogEntry, type CatalogKind, type CatalogFilters } from '../catalog';
import { SearchBar } from './SearchBar';
import { CatalogCard } from './CatalogCard';
import { CatalogFilterTags } from './CatalogFilterTags';

export function CatalogExplorer({ entries, kind, title, introduction, shareLabel, shareUrl }: { entries: CatalogEntry[]; kind: CatalogKind; title: string; introduction: string; shareLabel: string; shareUrl: string }) {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [format, setFormat] = useState('');
  const [sort, setSort] = useState<CatalogFilters['sort']>('updated');
  const visible = filterCatalog(entries, { query, category, format, sort });
  const hasFilters = !!(query || category || format);
  const labels = catalogLabels[kind];
  function reset() { setQuery(''); setCategory(''); setFormat(''); }

  return <div className="catalog-explorer-layout">
    <div className="model-results-heading">
      <div className="catalog-heading-line"><div className="catalog-heading-title"><h1>{title}<span className="maize-dot">.</span></h1><span className="catalog-heading-count" role="status" aria-live="polite" aria-label={`${visible.length} of ${entries.length} ${kind === 'software' ? 'software projects' : kind}`}>{visible.length} of {entries.length}</span></div><div className="catalog-heading-search"><SearchBar value={query} onChange={setQuery} label={`Search ${kind} by ${labels.title.toLowerCase()}, lab, description, or tags`} placeholder={`Search ${kind}…`}/><span id="search-help" className="sr-only">Search {labels.title.toLowerCase()}s, labs, and keywords.</span></div><label className="catalog-sort">Sort by <select value={sort} onChange={event => setSort(event.target.value as CatalogFilters['sort'])}><option value="updated">Recently updated</option><option value="title">{labels.title} (A–Z)</option></select></label></div>
      {introduction && <p>{introduction}</p>}
    </div>
    <aside className="catalog-filter-sidebar" aria-label={`Filter ${kind}`}>
      <h2>Filters</h2>
      <CatalogFilterTags label={labels.category} values={entries.map(entry => entry.category)} selected={category} onChange={setCategory}/>
      <CatalogFilterTags label={labels.format} values={entries.map(entry => entry.format)} selected={format} onChange={setFormat}/>
      {hasFilters && <button className="catalog-filter-reset" type="button" onClick={reset}>Clear filters</button>}
      <a className="catalog-share-link" href={shareUrl}>{shareLabel} <span aria-hidden="true">↗</span></a>
    </aside>
    <div className="catalog-results">
      <div className="model-grid">{visible.map(entry => <CatalogCard key={entry.id} entry={entry} kind={kind}/>)}</div>
      {visible.length === 0 && <div className="empty-state"><h3>{entries.length ? `No matching ${kind}` : `No ${kind} yet`}</h3><p>{entries.length ? 'Try a different keyword or clear your filters.' : labels.empty}</p>{hasFilters && <button className="button button-secondary" onClick={reset}>Clear all filters</button>}</div>}
    </div>
  </div>;
}
