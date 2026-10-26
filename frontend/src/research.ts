export type Category = string;
export type Research = {
  id: string; title: string; description: string; category: Category;
  researcher: string; tags: string[]; artifacts: ('Paper' | 'Model' | 'Dataset' | 'Code')[];
  detail_url: string;
  updated: string;
};

export function filterResearch(projects: Research[], query: string, category: Category | 'All') {
  const terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  return projects.filter(project => {
    const searchable = [project.title, project.description, ...project.tags].join(' ').toLowerCase();
    return (category === 'All' || category === project.category) && terms.every(term => searchable.includes(term));
  });
}

export function recentResearch(projects: Research[], limit = 6): Research[] {
  return [...projects].sort((a, b) => b.updated.localeCompare(a.updated) || a.title.localeCompare(b.title)).slice(0, limit);
}
