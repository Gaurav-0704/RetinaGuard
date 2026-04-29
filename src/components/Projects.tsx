import { FaGithub } from "react-icons/fa";
import { useReveal } from "../hooks/useReveal";
import { useTilt } from "../hooks/useTilt";
import { projects, type Project } from "../data/projects";

export default function Projects() {
  const ref = useReveal<HTMLElement>(".reveal");

  return (
    <section ref={ref} className="section projects" id="projects">
      <div className="section-inner">
        <p className="eyebrow reveal">04 — Selected Work</p>
        <h2 className="section-title reveal">Projects</h2>
        <div className="project-grid">
          {projects.map((p, i) => (
            <ProjectCard key={i} project={p} />
          ))}
        </div>
      </div>
    </section>
  );
}

function ProjectCard({ project: p }: { project: Project }) {
  const ref = useTilt<HTMLElement>(6);
  return (
    <article ref={ref as React.RefObject<HTMLElement>} className="project-card reveal">
      <div className="project-card-glare" aria-hidden />
      <div className="project-tag">{p.tag}</div>
      <h3 className="project-name">{p.name}</h3>
      <p className="project-tagline">{p.tagline}</p>
      <p className="project-desc">{p.description}</p>
      <ul className="project-highlights">
        {p.highlights.map((h, j) => (
          <li key={j}>{h}</li>
        ))}
      </ul>
      <div className="stack">
        {p.stack.map((s) => (
          <span key={s} className="chip">{s}</span>
        ))}
      </div>
      {p.github && (
        <a
          className="project-link"
          href={p.github}
          target="_blank"
          rel="noreferrer"
          aria-label={`${p.name} on GitHub`}
        >
          <FaGithub /> View on GitHub
        </a>
      )}
    </article>
  );
}
