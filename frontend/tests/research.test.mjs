import assert from 'node:assert/strict';
import test from 'node:test';
import { filterResearch } from '../src/research.ts';

const projects = [
  { id: 'model', title: 'Color Prediction', description: 'Classify colored shapes', category: 'classification', tags: ['Vision'], researcher: 'Researcher', artifacts: ['Model'], detail_url: '/models/example' },
  { id: 'paper', title: 'Language Models', description: 'Scientific research', category: 'NLP', tags: ['Pretraining'], researcher: 'Researcher', artifacts: ['Paper'], detail_url: '/papers/example' },
];
test('search matches titles, descriptions, and tags regardless of case or extra spaces', () => {
  assert.equal(filterResearch(projects, ' COLOR ', 'All')[0].id, 'model');
  assert.equal(filterResearch(projects, 'scientific research', 'All')[0].id, 'paper');
  assert.equal(filterResearch(projects, ' VISION ', 'All')[0].id, 'model');
});
test('record-derived topics combine with queries and support empty catalogs', () => {
  assert.equal(filterResearch(projects, 'color', 'classification').length, 1);
  assert.equal(filterResearch(projects, 'color', 'NLP').length, 0);
  assert.equal(filterResearch(projects, 'nonexistent', 'All').length, 0);
  assert.equal(filterResearch(projects, ' ', 'All').length, 2);
  assert.equal(filterResearch([], '', 'All').length, 0);
});

test('recent carousel uses newest records first without changing the catalog', async () => {
  const { recentResearch } = await import('../src/research.ts');
  const dated = [
    { ...projects[0], updated: '2020-01-01' },
    { ...projects[1], updated: '2026-10-21' },
  ];
  assert.deepEqual(recentResearch(dated).map(p => p.id), ['paper', 'model']);
  assert.equal(recentResearch(dated, 1)[0].id, 'paper');
  assert.equal(dated[0].id, 'model');
  assert.deepEqual(recentResearch([]), []);
  assert.equal(recentResearch([dated[0]]).length, 1);
});
