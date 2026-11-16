import { useState } from 'react';
import { catalogLabels, filterCatalog, type CatalogEntry, type CatalogKind, type CatalogFilters } from '../catalog';
import { SearchBar } from './SearchBar';
import { CatalogCard } from './CatalogCard';
import { CatalogFilterTags } from './CatalogFilterTags';
import { EmptyState } from './EmptyState';
import { CatalogHeading } from './CatalogHeading';
import { paginate } from '../pagination';
import { Pagination } from './Pagination';

export function CatalogExplorer({ entries, kind, title, introduction, shareLabel, shareUrl }: { entries: CatalogEntry[]; kind: CatalogKind; title: string; introduction: string; shareLabel: string; shareUrl: string }) {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [format, setFormat] = useState('');
  const [sort, setSort] = useState<CatalogFilters['sort']>('updated');
  const [page, setPage] = useState(1);
  const visible = filterCatalog(entries, { query, category, format, sort });
  const pagination = paginate(visible, page);
  const hasFilters = !!(query || category || format);
  const labels = catalogLabels[kind];
  function reset() { setQuery(''); setCategory(''); setFormat(''); setPage(1); }

  return <div className="catalog-explorer-layout">
    <div className="model-results-heading">
      <CatalogHeading title={title} count={`${visible.length} of ${entries.length}`}
        countLabel={`${visible.length} of ${entries.length} ${kind === 'software' ? 'software projects' : kind}`}
        search={<><SearchBar value={query} onChange={value => { setQuery(value); setPage(1); }} label={`Search ${kind} by ${labels.title.toLowerCase()}, lab, description, or tags`} placeholder={`Search ${kind}…`}/><span id="search-help" className="sr-only">Search {labels.title.toLowerCase()}s, labs, and keywords.</span></>}
        sort={<label className="catalog-sort">Sort by <select value={sort} onChange={event => { setSort(event.target.value as CatalogFilters['sort']); setPage(1); }}><option value="updated">Recently updated</option><option value="title">{labels.title} (A–Z)</option></select></label>}/>
      {introduction && <p>{introduction}</p>}
    </div>
    <aside className="catalog-filter-sidebar" aria-label={`Filter ${kind}`}>
      <h2>Filters</h2>
      <CatalogFilterTags label={labels.category} values={entries.map(entry => entry.category)} selected={category} onChange={value => { setCategory(value); setPage(1); }}/>
      <CatalogFilterTags label={labels.format} values={entries.map(entry => entry.format)} selected={format} onChange={value => { setFormat(value); setPage(1); }}/>
      {hasFilters && <button className="catalog-filter-reset" type="button" onClick={reset}>Clear filters</button>}
      <a className="catalog-share-link" href={shareUrl}>{shareLabel} <span aria-hidden="true">↗</span></a>
    </aside>
    <div className="catalog-results">
      <div className="model-grid">{pagination.items.map(entry => <CatalogCard key={entry.id} entry={entry} kind={kind}/>)}</div>
      <Pagination {...pagination} onChange={setPage}/>
      {visible.length === 0 && <EmptyState title={entries.length ? `No matching ${kind}` : `No ${kind} yet`} onReset={hasFilters ? reset : undefined}>{entries.length ? 'Try a different keyword or clear your filters.' : labels.empty}</EmptyState>}
    </div>
  </div>;
}
