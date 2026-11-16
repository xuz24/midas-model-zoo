export const PAGE_SIZE = 24;

export function paginate<T>(items: T[], requestedPage: number) {
  const pages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
  const page = Math.min(pages, Math.max(1, Number.isFinite(requestedPage) ? Math.floor(requestedPage) : 1));
  const offset = (page - 1) * PAGE_SIZE;
  return {
    items: items.slice(offset, offset + PAGE_SIZE), page, pages,
    start: items.length ? offset + 1 : 0,
    end: Math.min(offset + PAGE_SIZE, items.length), total: items.length,
  };
}
