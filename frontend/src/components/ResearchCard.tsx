import type { Research } from '../research';
import { CatalogCard } from './CatalogCard';
import type { CatalogEntry, CatalogKind } from '../catalog';

const artifactKinds: Record<Research['artifacts'][number], CatalogKind> = {
  Model: 'models', Dataset: 'datasets', Paper: 'papers', Code: 'software',
};

export function ResearchCard({ project }: { project: Research }) {
  const kind = artifactKinds[project.artifacts[0]] ?? 'models';
  const entry: CatalogEntry = {
    ...project,
    owner: project.researcher,
    format: project.artifacts.join(', '),
  };
  return <CatalogCard entry={entry} kind={kind}/>;
}
