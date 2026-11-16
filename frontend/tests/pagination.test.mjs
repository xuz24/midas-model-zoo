import assert from 'node:assert/strict';
import test from 'node:test';
import { paginate } from '../src/pagination.ts';
import { filterCatalog } from '../src/catalog.ts';
import { filterResearch } from '../src/research.ts';

const entries = Array.from({ length: 49 }, (_, i) => ({
  id: String(i), title: `Record ${String(i).padStart(2, '0')}`,
  description: i >= 24 ? 'Climate research' : 'Language research',
  owner: 'Demo lab', category: i >= 24 ? 'Climate' : 'Language',
  format: 'Python', tags: [], updated: '2026-11-15',
}));

test('pages cover every record once, with a partial final page and accurate ranges', () => {
  const pages = [1, 2, 3].map(page => paginate(entries, page));
  assert.deepEqual(pages.map(p => [p.start, p.end, p.pages, p.total]), [
    [1, 24, 3, 49], [25, 48, 3, 49], [49, 49, 3, 49],
  ]);
  assert.deepEqual(pages.flatMap(p => p.items), entries);
  assert.equal(paginate(entries.slice(0, 24), 1).pages, 1);
  assert.equal(paginate(entries.slice(0, 48), 2).pages, 2);
});

test('empty results and out-of-range pages remain valid', () => {
  assert.deepEqual(paginate([], 8), { items: [], page: 1, pages: 1, start: 0, end: 0, total: 0 });
  for (const requested of [-1, 0, NaN, Infinity]) {
    assert.equal(paginate(entries, requested).page, 1);
  }
  assert.equal(paginate(entries, 100).page, 3);
});

test('catalog search, filters, and sorting apply across pages before slicing', () => {
  const filtered = filterCatalog(entries, {
    query: 'climate', category: 'Climate', format: 'Python', sort: 'title',
  });
  const first = paginate(filtered, 1);
  const second = paginate(filtered, 2);
  assert.equal(first.total, 25);
  assert.deepEqual(first.items.map(e => e.id), entries.slice(24, 48).map(e => e.id));
  assert.deepEqual(second.items.map(e => e.id), ['48']);
  assert.equal(entries[0].id, '0');
});

test('homepage search and categories find matches beyond the first page', () => {
  const filtered = filterResearch(entries, 'climate', 'Climate');
  assert.equal(paginate(filtered, 1).total, 25);
  assert.equal(paginate(filtered, 1).items[0].id, '24');
  assert.deepEqual(paginate(filtered, 2).items.map(e => e.id), ['48']);
  assert.equal(paginate(filterResearch(entries, 'missing', 'All'), 2).total, 0);
});
