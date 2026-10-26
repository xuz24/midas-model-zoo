import type { Research } from '../research';

export function ResearchCard({ project }: { project: Research }) {
  return <article className="research-card">
    <div className="card-heading"><span className={`category-marker marker-${project.id}`} aria-hidden="true">{project.category === 'Engineering' ? '⌁' : project.category === 'Medicine & Health' ? '+' : project.category === 'Computer Vision' ? '◎' : project.category === 'Social Sciences' ? '⋈' : project.category === 'Data Science' ? '▦' : '✳'}</span><span className="card-category">{project.category}</span></div>
    <h3><a href={project.detail_url}>{project.title}<span className="card-arrow" aria-hidden="true">↗</span></a></h3>
    <p className="card-description">{project.description}</p>
    <p className="researcher"><span aria-hidden="true">◉</span>{project.researcher}</p>
    <ul className="tags" aria-label="Tags">{project.tags.map(tag => <li key={tag}>{tag}</li>)}</ul>
    <div className="card-bottom"><ul className="artifacts" aria-label="Research artifacts">{project.artifacts.map(artifact => <li key={artifact}><span aria-hidden="true">{artifact === 'Code' ? '⌘' : artifact === 'Dataset' ? '▦' : artifact === 'Model' ? '◇' : '≡'}</span> {artifact}</li>)}</ul></div>
  </article>;
}
