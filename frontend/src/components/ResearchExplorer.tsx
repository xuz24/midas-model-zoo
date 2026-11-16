import { useState } from 'react';
import { filterResearch, type Category, type Research } from '../research';
import { SearchBar } from './SearchBar';
import { CategoryFilter } from './CategoryFilter';
import { ResearchCard } from './ResearchCard';
import { EmptyState } from './EmptyState';
import { paginate } from '../pagination';
import { Pagination } from './Pagination';

export function ResearchExplorer({ projects }: { projects: Research[] }) {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState<Category | 'All'>('All');
  const [page, setPage] = useState(1);
  const categories = [...new Set(projects.map(project => project.category))].sort();
  const filtered = filterResearch(projects, query, category);
  const pagination = paginate(filtered, page);
  return <>
    <div className="discovery-heading"><h2>Explore research</h2></div>
    <SearchBar value={query} onChange={value => { setQuery(value); setPage(1); }}/>
    <p className="search-help" id="search-help">Search by title, description, or tags. Try “climate”, “language models”, or “open data”.</p>
    <CategoryFilter categories={categories} selected={category} onChange={value => { setCategory(value); setPage(1); }}/>
    <div className="section-heading"><span role="status" aria-live="polite">{`${filtered.length} of ${projects.length} records`}</span></div>
    <div className="research-grid">{pagination.items.map(project => <ResearchCard key={project.id} project={project}/>)}</div>
    <Pagination {...pagination} onChange={setPage}/>
    {filtered.length === 0 && <EmptyState title={projects.length ? 'No matching research' : 'No research yet'} onReset={query || category !== 'All' ? () => { setQuery(''); setCategory('All'); setPage(1); } : undefined}>{projects.length ? 'Try another keyword or explore a different category.' : 'Research will appear here as records are added.'}</EmptyState>}
  </>;
}
