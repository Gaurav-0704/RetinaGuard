import { useReveal } from "../hooks/useReveal";
import { degree, certifications, leadership } from "../data/education";

export default function Education() {
  const ref = useReveal<HTMLElement>(".reveal");

  return (
    <section ref={ref} className="section education" id="education">
      <div className="section-inner">
        <p className="eyebrow reveal">05 — Education &amp; Credentials</p>
        <h2 className="section-title reveal">Background</h2>
        <div className="edu-grid">
          <div className="edu-card edu-card-degree reveal">
            <div className="edu-crest" aria-hidden>
              <span>UD</span>
            </div>
            <h3>{degree.title}</h3>
            <p className="edu-school">{degree.school}</p>
            <p className="edu-period">{degree.period}</p>
            <p>{degree.note}</p>
          </div>

          <div className="edu-card reveal">
            <div className="edu-card-icon" aria-hidden>
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.6">
                <circle cx="12" cy="12" r="9" />
                <path d="M8 12l3 3 5-6" />
              </svg>
            </div>
            <h3>Certifications</h3>
            <ul>
              {certifications.map((c) => (
                <li key={c}>{c}</li>
              ))}
            </ul>
          </div>

          <div className="edu-card reveal">
            <div className="edu-card-icon" aria-hidden>
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.6">
                <path d="M12 3l9 4-9 4-9-4 9-4z" />
                <path d="M3 12l9 4 9-4" />
                <path d="M3 17l9 4 9-4" />
              </svg>
            </div>
            <h3>Leadership</h3>
            <ul>
              {leadership.map((l) => (
                <li key={l}>{l}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
