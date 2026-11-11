import { compareRecent, matchesSearch, searchTerms } from './collection.ts';

export type CatalogEntry = {
  detail_url: string;
  id: string; title: string; owner: string; description: string;
  category: string; format: string; tags: string[]; updated: string;
};
// Keep model facets separate from the topic category used on the homepage.
export function modelCatalogEntry(entry: CatalogEntry & { name: string; task: string; framework: string }): CatalogEntry {
  return { ...entry, title: entry.name, category: entry.task, format: entry.framework };
}

export type CatalogKind = 'models' | 'datasets' | 'papers' | 'software';
export type CatalogFilters = { query: string; category: string; format: string; sort: 'updated' | 'title' };

export function filterCatalog(entries: CatalogEntry[], filters: CatalogFilters): CatalogEntry[] {
  const terms = searchTerms(filters.query);
  return entries.filter(entry => {
    return matchesSearch([entry.title, entry.owner, entry.description, entry.category, ...entry.tags], terms) &&
      (!filters.category || entry.category === filters.category) &&
      (!filters.format || entry.format === filters.format);
  }).sort((a, b) => filters.sort === 'title'
    ? a.title.localeCompare(b.title)
    : compareRecent(a, b));
}

export const catalogLabels = {
  models: { singular: 'Model', icon: '◇', category: 'Tasks', format: 'Frameworks', title: 'Name', details: 'View model details', empty: 'Models will appear here once researchers can upload their work.' },
  datasets: { singular: 'Dataset', icon: '▦', category: 'Tasks', format: 'Modalities', title: 'Title', details: 'Dataset details', empty: 'Research will appear here once researchers can submit their work.' },
  papers: { singular: 'Paper', icon: '≡', category: 'Venues', format: 'Years', title: 'Title', details: 'Paper details', empty: 'Research will appear here once researchers can submit their work.' },
  software: { singular: 'Software', icon: '</>', category: 'Registries', format: 'Languages', title: 'Title', details: 'Software details', empty: 'Research will appear here once researchers can submit their work.' },
} satisfies Record<CatalogKind, { singular: string; icon: string; category: string; format: string; title: string; details: string; empty: string }>;
