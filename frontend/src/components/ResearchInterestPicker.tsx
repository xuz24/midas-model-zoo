import { useState } from 'react';

export function ResearchInterestPicker({ options, initial }: { options: string[]; initial: string[] }) {
  const [selected, setSelected] = useState(initial);
  const [query, setQuery] = useState('');
  const [error, setError] = useState('');
  const term = query.trim();
  const matches = options.filter(option => option.toLowerCase().includes(term.toLowerCase()) && !selected.some(value => value.toLowerCase() === option.toLowerCase()));
  const add = (value: string) => {
    const tag = value.trim().replace(/\s+/g, ' ');
    if (!tag || tag.length > 80 || /[,\u0000-\u001f\u007f]/.test(tag)) {
      setError('Use 1–80 characters without commas or control characters.');
      return;
    }
    if (selected.length >= 20) { setError('Choose up to 20 interests.'); return; }
    if (!selected.some(item => item.toLowerCase() === tag.toLowerCase())) setSelected([...selected, tag]);
    setQuery('');
    setError('');
  };
  return <>
    <ul className="profile-selected-interests" aria-label="Selected research interests">
      {selected.map(interest => <li key={interest}>
        <input type="hidden" name="research_interests" value={interest} />
        <span>{interest}</span><button type="button" aria-label={`Remove ${interest}`} onClick={() => { setSelected(selected.filter(value => value !== interest)); setError(''); }}>×</button>
      </li>)}
    </ul>
    <label htmlFor="interest-search">Search research interests</label>
    <input id="interest-search" type="search" value={query} maxLength={80} placeholder="Search topics or type your own…" autoComplete="off" aria-describedby="interests-help interest-picker-status" onChange={event => { setQuery(event.target.value); setError(''); }} onKeyDown={event => {
      if (event.key === 'Enter') { event.preventDefault(); if (term) add(options.find(option => option.toLowerCase() === term.toLowerCase()) || term); }
    }} />
    <div className="profile-interest-suggestions" aria-label="Suggested research interests">
      {matches.map(interest => <button type="button" key={interest} onClick={() => add(interest)}>+ {interest}</button>)}
    </div>
    {term && !options.some(option => option.toLowerCase() === term.toLowerCase()) && !selected.some(value => value.toLowerCase() === term.toLowerCase()) && <button className="profile-interest-other" type="button" onClick={() => add(term)}>Other: add “{term}”</button>}
    <p id="interest-picker-status" className={error ? 'profile-error' : 'submission-help'} role="status">{error || `${selected.length} selected. ${matches.length} suggested topics available.`}</p>
  </>;
}
