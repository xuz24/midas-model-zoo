type Props = { value: string; onChange: (value: string) => void; label?: string; placeholder?: string };

export function SearchBar({ value, onChange, label = "Search research by title, description, or tags", placeholder = "Search ideas, projects, or keywords…" }: Props) {
  return <div className="search-field">
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>
    <label className="sr-only" htmlFor="research-search">{label}</label>
    <input id="research-search" type="search" value={value} onChange={event => onChange(event.target.value)} placeholder={placeholder} aria-describedby="search-help" />
    {value && <button className="clear-search" type="button" onClick={() => onChange('')}>Clear</button>}
  </div>;
}
