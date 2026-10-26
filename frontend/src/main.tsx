import 'vite/modulepreload-polyfill';
import { createRoot } from 'react-dom/client';
import { ResearchExplorer } from './components/ResearchExplorer';
import { ModelExplorer } from './components/ModelExplorer';
import type { Model } from './models';
import { CatalogExplorer } from './components/CatalogExplorer';
import type { CatalogEntry } from './catalog';
import { ResearchCarousel } from './components/ResearchCarousel';
import './styles.css';

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

const modelExplorer = document.getElementById('model-explorer');
const modelData = document.getElementById('model-data');
if (modelExplorer && modelData) {
  const models: Model[] = JSON.parse(modelData.textContent || '[]');
  createRoot(modelExplorer).render(<ModelExplorer models={models} />);
}

const catalogExplorer = document.getElementById('catalog-explorer');
const catalogData = document.getElementById('catalog-data');
const kind = catalogExplorer?.dataset.kind;
if (catalogExplorer && catalogData && (kind === 'datasets' || kind === 'papers' || kind === 'software')) {
  const entries: CatalogEntry[] = JSON.parse(catalogData.textContent || '[]');
  createRoot(catalogExplorer).render(<CatalogExplorer entries={entries} kind={kind} />);
}
