import { useEffect, useRef, useState } from "react";
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
                {g.items.map((s) => (
                  <SkillBar key={s.name} name={s.name} level={s.level} />
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function SkillBar({ name, level }: { name: string; level: number }) {
  const ref = useRef<HTMLLIElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            setVisible(true);
            obs.disconnect();
          }
        }
      },
      { threshold: 0.3 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  return (
    <li ref={ref} className="skill-item">
      <div className="skill-row">
        <span className="skill-name">{name}</span>
        <span className="skill-pct" aria-hidden>{visible ? level : 0}%</span>
      </div>
      <div
        className="skill-bar"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={level}
        aria-label={name}
      >
        <div
          className="skill-bar-fill"
          style={{ width: visible ? `${level}%` : "0%" }}
        />
      </div>
    </li>
  );
}
