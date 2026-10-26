export type Model = {
  detail_url: string;
  id: string;
  name: string;
  owner: string;
  description: string;
  task: string;
  framework: string;
  tags: string[];
  updated: string;
};
export type ModelFilters = { query: string; task: string; framework: string; sort: 'updated' | 'name' };

export function filterModels(models: Model[], filters: ModelFilters): Model[] {
  const terms = filters.query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  return models.filter(model => {
    const text = [model.name, model.owner, model.description, model.task, ...model.tags].join(' ').toLowerCase();
    return terms.every(term => text.includes(term)) &&
      (!filters.task || model.task === filters.task) &&
      (!filters.framework || model.framework === filters.framework);
  }).sort((a, b) => filters.sort === 'name'
    ? a.name.localeCompare(b.name)
    : b.updated.localeCompare(a.updated) || a.name.localeCompare(b.name));
}
