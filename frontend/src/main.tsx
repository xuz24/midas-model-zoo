import 'vite/modulepreload-polyfill';
import { createRoot } from 'react-dom/client';
import { ResearchExplorer } from './components/ResearchExplorer';
import { CatalogExplorer } from './components/CatalogExplorer';
import { modelCatalogEntry, type CatalogEntry } from './catalog';
import { ResearchCarousel } from './components/ResearchCarousel';
import './styles.css';
import { ResearchInterestPicker } from './components/ResearchInterestPicker';
import { ResearcherSearch } from './components/ResearcherSearch';

const researchKind = document.querySelector<HTMLSelectElement>('#research-kind');
if (researchKind) {
  const sections = document.querySelectorAll<HTMLElement>('[data-research-kind]');
  const hint = document.getElementById('research-type-hint');
  const updateResearchFields = () => {
    sections.forEach(section => {
      const active = section.dataset.researchKind === researchKind.value;
      section.hidden = !active;
      section.querySelectorAll<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>('input, select, textarea')
        .forEach(field => { field.disabled = !active; });
    });
    if (hint) hint.hidden = researchKind.value !== '';
  };
  researchKind.addEventListener('change', updateResearchFields);
  window.addEventListener('pageshow', updateResearchFields);
  updateResearchFields();
}

const explorer = document.getElementById('research-explorer');
const researchData = document.getElementById('research-data');
if (researchData) {
  const projects = JSON.parse(researchData.textContent || '[]');
  if (explorer) createRoot(explorer).render(<ResearchExplorer projects={projects} />);
  const carousel = document.getElementById('research-carousel');
  if (carousel) createRoot(carousel).render(<ResearchCarousel projects={projects} />);
}

const catalogExplorer = document.getElementById('catalog-explorer');
const catalogData = document.getElementById('catalog-data');
const kind = catalogExplorer?.dataset.kind;
if (catalogExplorer && catalogData && (kind === 'models' || kind === 'datasets' || kind === 'papers' || kind === 'software')) {
  const data = JSON.parse(catalogData.textContent || '[]');
  const entries: CatalogEntry[] = kind === 'models' ? data.map(modelCatalogEntry) : data;
  createRoot(catalogExplorer).render(<CatalogExplorer entries={entries} kind={kind} title={catalogExplorer.dataset.title || kind} introduction={catalogExplorer.dataset.introduction || ''} shareLabel={catalogExplorer.dataset.shareLabel || 'Share research'} shareUrl={catalogExplorer.dataset.shareUrl || '/submit'} />);
}

const interestPicker = document.getElementById('research-interest-picker');
const researcherSearch = document.getElementById('researcher-catalog-heading');
if (researcherSearch) {
  createRoot(researcherSearch).render(<ResearcherSearch initialQuery={researcherSearch.dataset.query || ''}
    total={Number(researcherSearch.dataset.total)} directoryTotal={Number(researcherSearch.dataset.directoryTotal)}
    initialSort={researcherSearch.dataset.sort || 'name'} filters={JSON.parse(researcherSearch.dataset.filters || '{}')}/>);
}

const interestData = document.getElementById('research-interest-data');
if (interestPicker && interestData) {
  const data = JSON.parse(interestData.textContent || '{}');
  createRoot(interestPicker).render(<ResearchInterestPicker options={data.options} initial={data.selected} />);
}

const additionalLinks = document.getElementById('additional-profile-links');
const addLink = document.getElementById('add-profile-link');
const linkTemplate = document.querySelector<HTMLTemplateElement>('#additional-profile-link-template');
if (additionalLinks && addLink && linkTemplate) {
  const status = document.getElementById('profile-link-status');
  const enableRemove = () => {
    additionalLinks.querySelectorAll<HTMLButtonElement>('[data-remove-link]').forEach(button => {
      button.hidden = false;
    });
  };
  enableRemove();
  addLink.hidden = false;
  addLink.addEventListener('click', () => {
    additionalLinks.append(linkTemplate.content.cloneNode(true));
    enableRemove();
    additionalLinks.lastElementChild?.querySelector('input')?.focus();
    if (status) status.textContent = 'Link added.';
  });
  additionalLinks.addEventListener('click', event => {
    const button = (event.target as HTMLElement).closest('[data-remove-link]');
    if (!button) return;
    button.closest('[data-additional-link]')?.remove();
    addLink.focus();
    if (status) status.textContent = 'Link removed.';
  });
}

// Keep initials visible until the remote image has loaded successfully.
document.querySelectorAll<HTMLImageElement>('[data-profile-picture]').forEach(picture => {
  const showPicture = () => picture.classList.toggle('is-loaded', picture.naturalWidth > 0);
  picture.addEventListener('load', showPicture);
  picture.addEventListener('error', () => picture.classList.remove('is-loaded'));
  if (picture.complete) showPicture();
});
