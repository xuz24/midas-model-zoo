import { type Category } from '../research';

type Props = { categories: string[]; selected: Category | 'All'; onChange: (category: Category | 'All') => void };
export function CategoryFilter({ categories, selected, onChange }: Props) {
  return <div className="categories">
    <h3>Explore by Topic</h3>
    <div className="category-options" role="group" aria-label="Filter research by category">
      {(['All', ...categories] as const).map(category => <button type="button" key={category} aria-pressed={selected === category} onClick={() => onChange(category)}>{category === 'All' ? 'All research' : category}</button>)}
    </div>
  </div>;
}
