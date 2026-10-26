import type { CatalogEntry, CatalogKind } from '../catalog';

export function CatalogCard({ entry, kind }: { entry: CatalogEntry; kind: CatalogKind }) {
  const singular = kind === 'software' ? 'software' : kind === 'datasets' ? 'dataset' : 'paper';
  return <article className="model-card">
    <div className="model-card-top"><span className="category-marker" aria-hidden="true">{kind === 'software' ? '</>' : kind === 'datasets' ? '▦' : '≡'}</span><span>{entry.owner}</span></div>
    <h3><a href={entry.detail_url}>{entry.title}<span aria-hidden="true">↗</span></a></h3>
    <p className="model-description">{entry.description}</p>
    <div className="model-specs"><span>{entry.category}</span><span>{entry.format}</span></div>
    <ul className="tags" aria-label={`${singular} tags`}>{entry.tags.map(tag => <li key={tag}>{tag}</li>)}</ul>
    <div className="model-card-footer"><span>Updated <time dateTime={entry.updated}>{new Date(`${entry.updated}T00:00:00Z`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' })}</time></span><span>{kind === 'software' ? 'Software' : kind === 'datasets' ? 'Dataset' : 'Paper'} details</span></div>
  </article>;
}
