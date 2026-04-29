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
          <div className="edu-card reveal">
            <h3>{degree.title}</h3>
            <p className="edu-school">{degree.school}</p>
            <p className="edu-period">{degree.period}</p>
            <p>{degree.note}</p>
          </div>

          <div className="edu-card reveal">
            <h3>Certifications</h3>
            <ul>
              {certifications.map((c) => (
                <li key={c}>{c}</li>
              ))}
            </ul>
          </div>

          <div className="edu-card reveal">
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
