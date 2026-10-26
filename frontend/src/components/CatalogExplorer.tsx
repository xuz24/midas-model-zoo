import { useState } from 'react';
import { filterCatalog, type CatalogEntry, type CatalogKind, type CatalogFilters } from '../catalog';
import { SearchBar } from './SearchBar';
import { CatalogCard } from './CatalogCard';

export function CatalogExplorer({ entries, kind }: { entries: CatalogEntry[]; kind: CatalogKind }) {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [format, setFormat] = useState('');
  const [sort, setSort] = useState<CatalogFilters['sort']>('updated');
  const categories = [...new Set(entries.map(entry => entry.category))].sort();
  const formats = [...new Set(entries.map(entry => entry.format))].sort();
  const visible = filterCatalog(entries, { query, category, format, sort });
  const hasFilters = !!(query || category || format);
  const formatLabel = kind === 'software' ? 'Language' : kind === 'datasets' ? 'Modality' : 'Year';
  const allFormats = kind === 'software' ? 'All languages' : kind === 'datasets' ? 'All modalities' : 'All years';
  function reset() { setQuery(''); setCategory(''); setFormat(''); }

  return <>
    <SearchBar value={query} onChange={setQuery} label={`Search ${kind} by title, lab, description, or tags`} placeholder={`Search ${kind}, labs, or keywords…`}/>
    <p id="search-help" className="search-help">Search by title, lab, description, or tags. Try “climate” or “NLP”.</p>
    <div className="model-toolbar">
      <label>{kind === 'papers' ? 'Venue' : kind === 'software' ? 'Registry' : 'Task'}<select value={category} onChange={event => setCategory(event.target.value)}><option value="">All</option>{categories.map(value => <option key={value}>{value}</option>)}</select></label>
      <label>{formatLabel}<select value={format} onChange={event => setFormat(event.target.value)}><option value="">{allFormats}</option>{formats.map(value => <option key={value}>{value}</option>)}</select></label>
      <label className="model-sort">Sort by<select value={sort} onChange={event => setSort(event.target.value as CatalogFilters['sort'])}><option value="updated">Recently updated</option><option value="title">Title (A–Z)</option></select></label>
    </div>
    <div className="model-results-heading"><h2>All {kind}</h2><span role="status" aria-live="polite">{visible.length} of {entries.length} {kind === 'software' ? 'software projects' : kind}</span>{hasFilters && <button className="clear-search" onClick={reset}>Clear filters</button>}</div>
    <div className="model-grid">{visible.map(entry => <CatalogCard key={entry.id} entry={entry} kind={kind}/>)}</div>
    {visible.length === 0 && <div className="empty-state"><h3>{entries.length ? `No matching ${kind}` : `No ${kind} yet`}</h3><p>{entries.length ? 'Try a different keyword or clear your filters.' : 'Research will appear here once researchers can submit their work.'}</p>{hasFilters && <button className="button button-secondary" onClick={reset}>Clear all filters</button>}</div>}
  </>;
}
