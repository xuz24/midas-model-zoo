type Props = {
  label: string;
  values: string[];
  selected: string;
  onChange: (value: string) => void;
};

export function CatalogFilterTags({ label, values, selected, onChange }: Props) {
  const counts = new Map<string, number>();
  values.forEach(value => counts.set(value, (counts.get(value) ?? 0) + 1));

  return <div className="catalog-filter-group" role="group" aria-label={`Filter by ${label.toLowerCase()}`}>
    <h3>{label}</h3>
    <div className="catalog-filter-tags">
      <button type="button" aria-pressed={selected === ''} onClick={() => onChange('')}>All <span>{values.length}</span></button>
      {[...counts.keys()].sort((a, b) => a.localeCompare(b)).map(value =>
        <button type="button" key={value} aria-pressed={selected === value} onClick={() => onChange(selected === value ? '' : value)}>{value} <span>{counts.get(value)}</span></button>
      )}
    </div>
  </div>;
}
