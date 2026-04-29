import { useReveal } from "../hooks/useReveal";
import { personal } from "../data/personal";

// Replace the headline and subheading below with your own copy.
// Keep the headline short and punchy — one or two lines max.
export default function Intro() {
  const ref = useReveal<HTMLElement>(".reveal");

  return (
    <section ref={ref} className="intro" id="intro">
      <div className="intro-inner">
        <p className="eyebrow reveal">00 — Hello</p>
        <h2 className="intro-title reveal">
          A short, punchy <span className="accent">headline</span> about what
          you do —{" "}
          <span className="muted">and what you don&apos;t.</span>
        </h2>
        <p className="intro-sub reveal">
          I&apos;m <strong>{personal.name}</strong>. One or two sentences about
          who you are, where you study or work, and the kind of problems you
          like to solve. Keep it concrete. End with a hook that hints at the
          rest of the page.
        </p>
        <div className="intro-ctas reveal">
          <a className="btn btn-primary" href="#projects">See my work</a>
          <a className="btn btn-ghost" href="#contact">Get in touch</a>
        </div>
      </div>
    </section>
  );
}
