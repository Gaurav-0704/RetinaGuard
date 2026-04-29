import { useReveal } from "../hooks/useReveal";
import { roles } from "../data/experience";

export default function Experience() {
  const ref = useReveal<HTMLElement>(".reveal");

  return (
    <section ref={ref} className="section experience" id="experience">
      <div className="section-inner">
        <p className="eyebrow reveal">03 — Experience</p>
        <h2 className="section-title reveal">Where I&apos;ve shipped</h2>

        <div className="timeline timeline-deco">
          <div className="timeline-spine" aria-hidden />
          {roles.map((r, i) => (
            <article key={i} className="timeline-item reveal">
              <div className="timeline-dot" aria-hidden>
                <span className="timeline-dot-pulse" />
              </div>
              <div className="timeline-content">
                <div className="timeline-header">
                  <h3>{r.title}</h3>
                  <span className="period">{r.period}</span>
                </div>
                <p className="timeline-company">
                  {r.company} <span className="timeline-sep">&middot;</span>{" "}
                  <span>{r.location}</span>
                </p>
                <ul>
                  {r.bullets.map((b, j) => (
                    <li key={j}>{b}</li>
                  ))}
                </ul>
                <div className="stack">
                  {r.stack.map((s) => (
                    <span key={s} className="chip">{s}</span>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
