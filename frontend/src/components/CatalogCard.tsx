import { catalogLabels, type CatalogEntry, type CatalogKind } from '../catalog';
import { formatDate } from '../dates';

export function CatalogCard({ entry, kind }: { entry: CatalogEntry; kind: CatalogKind }) {
  const labels = catalogLabels[kind];
  return <article className="model-card">
    <div className="model-card-top"><span className="category-marker" aria-hidden="true">{labels.icon}</span><span>{entry.owner}</span></div>
    <h3><a href={entry.detail_url}>{entry.title}<span aria-hidden="true">↗</span></a></h3>
    <p className="model-description">{entry.description}</p>
    <div className="model-specs"><span>{entry.category}</span><span>{entry.format}</span></div>
    <ul className="tags" aria-label={`${kind === 'models' ? labels.singular : labels.singular.toLowerCase()} tags`}>{entry.tags.map(tag => <li key={tag}>{tag}</li>)}</ul>
    <div className="model-card-footer"><span>Updated <time dateTime={entry.updated}>{formatDate(entry.updated)}</time></span><span>{labels.details}</span></div>
  </article>;
}
