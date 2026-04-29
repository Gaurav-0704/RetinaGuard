import { useReveal } from "../hooks/useReveal";
import { skillGroups } from "../data/skills";

export default function Skills() {
  const ref = useReveal<HTMLElement>(".reveal");

  return (
    <section ref={ref} className="section skills" id="skills">
      <div className="section-inner">
        <p className="eyebrow reveal">02 — Skills</p>
        <h2 className="section-title reveal">My stack</h2>
        <div className="skill-grid">
          {skillGroups.map((g) => (
            <div key={g.title} className="skill-group reveal">
              <h3>{g.title}</h3>
              <ul>
                {g.items.map((i) => (
                  <li key={i}>{i}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
