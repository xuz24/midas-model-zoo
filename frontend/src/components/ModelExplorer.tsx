import { useState } from 'react';
import { filterModels, type Model, type ModelFilters } from '../models';
import { ModelCard } from './ModelCard';
import { SearchBar } from './SearchBar';

export function ModelExplorer({ models }: { models: Model[] }) {
  const [query, setQuery] = useState('');
  const [task, setTask] = useState('');
  const [framework, setFramework] = useState('');
  const [sort, setSort] = useState<ModelFilters['sort']>('updated');
  const tasks = [...new Set(models.map(model => model.task))].sort();
  const frameworks = [...new Set(models.map(model => model.framework))].sort();
  const visible = filterModels(models, { query, task, framework, sort });
  const hasFilters = !!(query || task || framework);
  function reset() { setQuery(''); setTask(''); setFramework(''); }

  return <>
    <SearchBar value={query} onChange={setQuery} label="Search models by name, lab, description, or tags" placeholder="Search models, labs, or keywords…"/>
    <p id="search-help" className="search-help">Search by name, lab, description, or tags. Try “climate” or “NLP”.</p>
    <div className="model-toolbar">
      <label>Task<select value={task} onChange={event => setTask(event.target.value)}><option value="">All tasks</option>{tasks.map(value => <option key={value}>{value}</option>)}</select></label>
      <label>Framework<select value={framework} onChange={event => setFramework(event.target.value)}><option value="">All frameworks</option>{frameworks.map(value => <option key={value}>{value}</option>)}</select></label>
      <label className="model-sort">Sort by<select value={sort} onChange={event => setSort(event.target.value as ModelFilters['sort'])}><option value="updated">Recently updated</option><option value="name">Name (A–Z)</option></select></label>
    </div>
    <div className="model-results-heading"><h2>All models</h2><span role="status" aria-live="polite">{visible.length} of {models.length} models</span>{hasFilters && <button className="clear-search" onClick={reset}>Clear filters</button>}</div>
    <div className="model-grid">{visible.map(model => <ModelCard key={model.id} model={model}/>)}</div>
    {visible.length === 0 && <div className="empty-state"><h3>{models.length ? 'No matching models' : 'No models yet'}</h3><p>{models.length ? 'Try a different keyword or clear your filters.' : 'Models will appear here once researchers can upload their work.'}</p>{hasFilters && <button className="button button-secondary" onClick={reset}>Clear all filters</button>}</div>}
  </>;
}
