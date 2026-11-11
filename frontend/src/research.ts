import { compareRecent, matchesSearch, searchTerms } from './collection.ts';

export type Category = string;
export type Research = {
  id: string; title: string; description: string; category: Category;
  researcher: string; tags: string[]; artifacts: ('Paper' | 'Model' | 'Dataset' | 'Code')[];
  detail_url: string;
  updated: string;
};

export function filterResearch(projects: Research[], query: string, category: Category | 'All') {
  const terms = searchTerms(query);
  return projects.filter(project => {
    return (category === 'All' || category === project.category) &&
      matchesSearch([project.title, project.description, ...project.tags], terms);
  });
}

export function recentResearch(projects: Research[], limit = 6): Research[] {
  return [...projects].sort(compareRecent).slice(0, limit);
}
