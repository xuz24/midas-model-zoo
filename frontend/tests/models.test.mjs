import assert from 'node:assert/strict';
import test from 'node:test';
import { filterCatalog, modelCatalogEntry } from '../src/catalog.ts';

const models = [
  { id: 'a', title: 'Alpha', owner: 'Vision Lab', description: 'Satellite imagery', category: 'Segmentation', format: 'PyTorch', tags: ['Climate'], updated: '2026-10-01' },
  { id: 'b', title: 'Beta', owner: 'Language Lab', description: 'Text analysis', category: 'Classification', format: 'TensorFlow', tags: ['NLP'], updated: '2026-10-12' },
];
const defaults = { query: '', category: '', format: '', sort: 'updated' };
test('models search names, labs, descriptions and tags case-insensitively', () => {
  for (const query of [' alpha ', 'VISION LAB', 'satellite', 'climate']) {
    assert.deepEqual(filterCatalog(models, { ...defaults, query }).map(m => m.id), ['a']);
  }
});
test('task and framework filters combine with search', () => {
  assert.equal(filterCatalog(models, { ...defaults, query: 'climate', category: 'Segmentation', format: 'PyTorch' }).length, 1);
  assert.equal(filterCatalog(models, { ...defaults, query: 'climate', format: 'TensorFlow' }).length, 0);
  assert.equal(filterCatalog(models, { ...defaults, category: 'Regression' }).length, 0);
  assert.deepEqual(filterCatalog([], defaults), []);
});
test('sorting does not mutate the source catalog', () => {
  assert.deepEqual(filterCatalog(models, defaults).map(m => m.id), ['b', 'a']);
  assert.deepEqual(filterCatalog(models, { ...defaults, sort: 'title' }).map(m => m.id), ['a', 'b']);
  assert.deepEqual(models.map(m => m.id), ['a', 'b']);
});

test('model facets use task and framework without changing research topics', () => {
  const source = { ...models[0], name: 'Model name', category: 'Medicine', format: 'Images', task: 'Segmentation', framework: 'PyTorch' };
  const entry = modelCatalogEntry(source);
  assert.equal(entry.title, 'Model name');
  assert.deepEqual(filterCatalog([entry], { ...defaults, category: 'Segmentation', format: 'PyTorch' }), [entry]);
  assert.equal(filterCatalog([entry], { ...defaults, category: 'Medicine' }).length, 0);
  assert.equal(source.category, 'Medicine');
  assert.equal(source.format, 'Images');
});
