import { useState } from 'react';
import { filterResearch, type Category, type Research } from '../research';
import { SearchBar } from './SearchBar';
import { CategoryFilter } from './CategoryFilter';
import { ResearchCard } from './ResearchCard';

export function ResearchExplorer({ projects }: { projects: Research[] }) {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState<Category | 'All'>('All');
  const categories = [...new Set(projects.map(project => project.category))].sort();
  const filtered = filterResearch(projects, query, category);
  return <>
    <div className="discovery-heading"><div><p className="eyebrow">FIND YOUR NEXT CONNECTION</p><h2>A world of ideas. Start exploring.</h2></div><span className="preview-label"><span className="status-dot"/> Platform preview</span></div>
    <SearchBar value={query} onChange={setQuery}/>
    <p className="search-help" id="search-help">Search by title, description, or tags. Try “climate”, “language models”, or “open data”.</p>
    <CategoryFilter categories={categories} selected={category} onChange={setCategory}/>
    <div className="section-heading"><h2>Featured Research</h2><span role="status" aria-live="polite">{`${filtered.length} of ${projects.length} records`}</span></div>
    <p className="demo-notice"><span aria-hidden="true">ⓘ</span> Explore models, datasets, papers, and software from the research catalog.</p>
    <div className="research-grid">{filtered.map(project => <ResearchCard key={project.id} project={project}/>)}</div>
    {filtered.length === 0 && <div className="empty-state"><h3>No matching projects</h3><p>Try another keyword or explore a different category.</p><button className="button button-secondary" onClick={() => { setQuery(''); setCategory('All'); }}>Clear all filters</button></div>}
  </>;
}
