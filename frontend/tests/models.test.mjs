import assert from 'node:assert/strict';
import test from 'node:test';
import { filterModels } from '../src/models.ts';

const models = [
  { id: 'a', name: 'Alpha', owner: 'Vision Lab', description: 'Satellite imagery', task: 'Segmentation', framework: 'PyTorch', tags: ['Climate'], updated: '2026-10-01' },
  { id: 'b', name: 'Beta', owner: 'Language Lab', description: 'Text analysis', task: 'Classification', framework: 'TensorFlow', tags: ['NLP'], updated: '2026-10-12' },
];
const defaults = { query: '', task: '', framework: '', sort: 'updated' };
test('models search names, labs, descriptions and tags case-insensitively', () => {
  for (const query of [' alpha ', 'VISION LAB', 'satellite', 'climate']) {
    assert.deepEqual(filterModels(models, { ...defaults, query }).map(m => m.id), ['a']);
  }
});
test('task and framework filters combine with search', () => {
  assert.equal(filterModels(models, { ...defaults, query: 'climate', task: 'Segmentation', framework: 'PyTorch' }).length, 1);
  assert.equal(filterModels(models, { ...defaults, query: 'climate', framework: 'TensorFlow' }).length, 0);
  assert.equal(filterModels(models, { ...defaults, task: 'Regression' }).length, 0);
  assert.deepEqual(filterModels([], defaults), []);
});
test('sorting does not mutate the source catalog', () => {
  assert.deepEqual(filterModels(models, defaults).map(m => m.id), ['b', 'a']);
  assert.deepEqual(filterModels(models, { ...defaults, sort: 'name' }).map(m => m.id), ['a', 'b']);
  assert.deepEqual(models.map(m => m.id), ['a', 'b']);
});
