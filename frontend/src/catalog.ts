export type CatalogEntry = {
  detail_url: string;
  id: string; title: string; owner: string; description: string;
  category: string; format: string; tags: string[]; updated: string;
};
export type CatalogKind = 'datasets' | 'papers' | 'software';
export type CatalogFilters = { query: string; category: string; format: string; sort: 'updated' | 'title' };

export function filterCatalog(entries: CatalogEntry[], filters: CatalogFilters): CatalogEntry[] {
  const terms = filters.query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  return entries.filter(entry => {
    const text = [entry.title, entry.owner, entry.description, entry.category, ...entry.tags].join(' ').toLowerCase();
    return terms.every(term => text.includes(term)) &&
      (!filters.category || entry.category === filters.category) &&
      (!filters.format || entry.format === filters.format);
  }).sort((a, b) => filters.sort === 'title'
    ? a.title.localeCompare(b.title)
    : b.updated.localeCompare(a.updated) || a.title.localeCompare(b.title));
}
