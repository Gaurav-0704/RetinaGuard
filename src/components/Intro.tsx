import { useReveal } from "../hooks/useReveal";
import { personal } from "../data/personal";

// Punchy intro under the hero.
export default function Intro() {
  const ref = useReveal<HTMLElement>(".reveal");

  return (
    <section ref={ref} className="intro" id="intro">
      <div className="intro-inner">
        <p className="eyebrow reveal">00 — Hello</p>
        <h2 className="intro-title reveal">
          Data into <span className="accent">decisions</span> —{" "}
          <span className="muted">not just dashboards.</span>
        </h2>
        <p className="intro-sub reveal">
          I&apos;m <strong>{personal.name}</strong>, a Business Analytics
          graduate student with a software-engineering background. I clean,
          model, and visualize data in Python, SQL, and Tableau — and I care
          most about the part where the numbers turn into a recommendation
          someone can actually use.
        </p>
        <div className="intro-ctas reveal">
          <a className="btn btn-primary" href="#projects">See my work</a>
          <a className="btn btn-ghost" href="#contact">Get in touch</a>
        </div>
      </div>
    </section>
  );
}
