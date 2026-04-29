import { FaLinkedin, FaGithub, FaEnvelope, FaPhone } from "react-icons/fa";
import { useReveal } from "../hooks/useReveal";
import { personal } from "../data/personal";

export default function Contact() {
  const ref = useReveal<HTMLElement>(".reveal");

  return (
    <section ref={ref} className="section contact" id="contact">
      <div className="section-inner contact-inner">
        <p className="eyebrow reveal">06 — Contact</p>
        <h2 className="section-title reveal">
          Let&apos;s build something that <span className="accent">ships</span>.
        </h2>
        <p className="contact-sub reveal">
          Open to Summer 2026 and full-time roles in Applied AI, ML Engineering,
          Data Science, and Full-Stack AI development.
        </p>

        <a className="contact-email reveal" href={`mailto:${personal.email}`}>
          {personal.email}
        </a>

        <div className="contact-links reveal">
          <a href={`mailto:${personal.email}`} aria-label="Email">
            <FaEnvelope /> Email
          </a>
          <a href={`tel:${personal.phone}`} aria-label="Phone">
            <FaPhone /> {personal.phoneDisplay}
          </a>
          <a href={personal.linkedin} target="_blank" rel="noreferrer" aria-label="LinkedIn">
            <FaLinkedin /> LinkedIn
          </a>
          <a href={personal.github} target="_blank" rel="noreferrer" aria-label="GitHub">
            <FaGithub /> GitHub
          </a>
        </div>

        <footer className="footer">
          <span>{personal.location}</span>
          <span>© {new Date().getFullYear()} {personal.name}</span>
        </footer>
      </div>
    </section>
  );
}
