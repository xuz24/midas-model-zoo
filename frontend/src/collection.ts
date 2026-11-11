export function searchTerms(query: string): string[] {
  return query.trim().toLowerCase().split(/\s+/).filter(Boolean);
}

export function matchesSearch(fields: string[], terms: string[]): boolean {
  const text = fields.join(' ').toLowerCase();
  return terms.every(term => text.includes(term));
}

export function compareRecent(a: { updated: string; title: string }, b: { updated: string; title: string }): number {
  return b.updated.localeCompare(a.updated) || a.title.localeCompare(b.title);
}
