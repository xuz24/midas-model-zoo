import assert from 'node:assert/strict';
import test from 'node:test';
import { filterCatalog } from '../src/catalog.ts';

const entries = [
  { id: 'a', title: 'Alpha', owner: 'Vision Lab', description: 'Satellite imagery', category: 'Vision', format: 'Images', tags: ['Climate'], updated: '2026-10-01' },
  { id: 'b', title: 'Beta', owner: 'Language Lab', description: 'Text analysis', category: 'AI', format: 'Preprint', tags: ['NLP'], updated: '2026-10-12' },
];
const defaults = { query: '', category: '', format: '', sort: 'updated' };
test('catalog search covers title, lab, description, and tags', () => {
  for (const query of [' ALPHA ', 'vision lab', 'satellite', 'CLIMATE']) {
    assert.deepEqual(filterCatalog(entries, { ...defaults, query }).map(e => e.id), ['a']);
  }
});
test('category and format/type filters combine with search', () => {
  assert.equal(filterCatalog(entries, { ...defaults, query: 'climate', category: 'Vision', format: 'Images' }).length, 1);
  assert.equal(filterCatalog(entries, { ...defaults, query: 'climate', format: 'Preprint' }).length, 0);
  assert.equal(filterCatalog(entries, { ...defaults, category: 'AI', format: 'Preprint' }).length, 1);
  assert.deepEqual(filterCatalog([], defaults), []);
});
test('sorting supports dates and titles without mutating data', () => {
  assert.deepEqual(filterCatalog(entries, defaults).map(e => e.id), ['b', 'a']);
  assert.deepEqual(filterCatalog(entries, { ...defaults, sort: 'title' }).map(e => e.id), ['a', 'b']);
  assert.deepEqual(entries.map(e => e.id), ['a', 'b']);
});

test('software language filter combines with category and search', () => {
  const software = [
    { ...entries[0], title: 'Canopy Toolkit', format: 'Python' },
    { ...entries[1], title: 'Language Toolkit', format: 'R' },
  ];
  assert.deepEqual(filterCatalog(software, { ...defaults, query: 'toolkit', category: 'Vision', format: 'Python' }).map(e => e.id), ['a']);
  assert.equal(filterCatalog(software, { ...defaults, query: 'climate', format: 'R' }).length, 0);
});
