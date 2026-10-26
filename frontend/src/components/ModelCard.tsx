import type { Model } from '../models';

export function ModelCard({ model }: { model: Model }) {
  return <article className="model-card">
    <div className="model-card-top"><span className="category-marker" aria-hidden="true">◇</span><span>{model.owner}</span></div>
    <h3><a href={model.detail_url}>{model.name}<span aria-hidden="true">↗</span></a></h3>
    <p className="model-description">{model.description}</p>
    <div className="model-specs"><span>{model.task}</span><span>{model.framework}</span></div>
    <ul className="tags" aria-label="Model tags">{model.tags.map(tag => <li key={tag}>{tag}</li>)}</ul>
    <div className="model-card-footer"><span>Updated <time dateTime={model.updated}>{new Date(`${model.updated}T00:00:00Z`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' })}</time></span><span>View model details</span></div>
  </article>;
}
