import { useEffect, useMemo, useState } from 'react';
import { recentResearch, type Research } from '../research';
import { ResearchCard } from './ResearchCard';

export function ResearchCarousel({ projects }: { projects: Research[] }) {
  const slides = useMemo(() => recentResearch(projects), [projects]);
  const [index, setIndex] = useState(0);
  const [paused, setPaused] = useState(() => window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const [hovering, setHovering] = useState(false);
  const [hidden, setHidden] = useState(document.hidden);
  const rotating = slides.length > 1 && !paused && !hovering && !hidden;
  const activeIndex = index % Math.max(slides.length, 1);

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const onMotionChange = () => { if (media.matches) setPaused(true); };
    const onVisibilityChange = () => setHidden(document.hidden);
    media.addEventListener('change', onMotionChange);
    document.addEventListener('visibilitychange', onVisibilityChange);
    return () => {
      media.removeEventListener('change', onMotionChange);
      document.removeEventListener('visibilitychange', onVisibilityChange);
    };
  }, []);

  useEffect(() => {
    if (!rotating) return;
    const timer = window.setInterval(() => setIndex(current => (current + 1) % slides.length), 6000);
    return () => window.clearInterval(timer);
  }, [rotating, slides.length]);

  function select(next: number) {
    setPaused(true);
    setIndex((next + slides.length) % slides.length);
  }

  if (!slides.length) return <div className="recent-empty"><h2>Recently updated</h2><p>Research will appear here as records are added.</p></div>;
  return <section className="research-carousel" aria-label="Recently updated research" aria-roledescription="carousel"
    onMouseEnter={() => setHovering(true)} onMouseLeave={() => setHovering(false)}
    onFocusCapture={event => {
      if (!(event.target instanceof HTMLElement) || !event.target.closest('[data-rotation-control]')) setPaused(true);
    }}>
    <div className="carousel-heading"><div><h2>Latest from the Community</h2></div>
      {slides.length > 1 && <button type="button" className="carousel-control" data-rotation-control aria-label={paused ? 'Start automatic rotation' : 'Pause automatic rotation'} onClick={() => setPaused(current => !current)}>{paused ? 'Play' : 'Pause'}</button>}
    </div>
    <div className="carousel-stage" aria-live={rotating ? 'off' : 'polite'} aria-atomic="true">
      <div className="carousel-track">
        {slides.map((project, position) => {
          const distance = (position - activeIndex + slides.length) % slides.length;
          const placement = distance === 0 ? 'active' : distance === 1 ? 'next' : distance === slides.length - 1 ? 'previous' : 'back';
          return <div key={project.id} className={`carousel-slide carousel-slide--${placement}`}
          role="group" aria-roledescription="slide" aria-label={`${position + 1} of ${slides.length}`}
          aria-hidden={position !== activeIndex} inert={position !== activeIndex}>
          <ResearchCard project={project}/>
          <p className="carousel-date">Updated <time dateTime={project.updated}>{new Date(`${project.updated}T00:00:00Z`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' })}</time></p>
        </div>;
        })}
      </div>
    </div>
    {slides.length > 1 && <div className="carousel-navigation">
      <button type="button" className="carousel-control" aria-label="Previous research" onClick={() => select(activeIndex - 1)}>←</button>
      <div className="carousel-dots" role="group" aria-label="Choose a research card">{slides.map((slide, position) => <button type="button" key={slide.id} aria-label={`Show ${slide.title}`} aria-current={position === activeIndex ? 'true' : undefined} onClick={() => select(position)}><span/></button>)}</div>
      <span className="carousel-count">{activeIndex + 1} / {slides.length}</span>
      <button type="button" className="carousel-control" aria-label="Next research" onClick={() => select(activeIndex + 1)}>→</button>
    </div>}
  </section>;
}
