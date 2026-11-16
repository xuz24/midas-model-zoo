type Props = {
  page: number; pages: number; start: number; end: number; total: number;
  onChange: (page: number) => void;
};

export function Pagination({ page, pages, start, end, total, onChange }: Props) {
  if (pages <= 1) return null;
  return <nav className="catalog-pagination" aria-label="Results pages">
    <button className="button button-secondary" type="button" disabled={page === 1} onClick={() => onChange(page - 1)}>← Previous</button>
    <span role="status" aria-live="polite">Page {page} of {pages}<small>Showing {start}–{end} of {total}</small></span>
    <button className="button button-secondary" type="button" disabled={page === pages} onClick={() => onChange(page + 1)}>Next →</button>
  </nav>;
}
