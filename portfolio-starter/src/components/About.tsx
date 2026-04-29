import { useReveal } from "../hooks/useReveal";
import { stats } from "../data/about";

// Replace the section title and the three paragraphs below with your own copy.
// Keep paragraphs short — readers are skimming.
export default function About() {
  const ref = useReveal<HTMLElement>(".reveal");

  return (
    <section ref={ref} className="section about" id="about">
      <div className="section-inner">
        <p className="eyebrow reveal">01 — About</p>
        <h2 className="section-title reveal">
          A short, memorable headline about{" "}
          <span className="accent">what you do</span>.
        </h2>

        <div className="about-grid">
          <p className="reveal">
            One sentence about who you are, where you study or work, and the
            kind of problems you focus on. Keep it concrete.
          </p>
          <p className="reveal">
            One sentence about what you&apos;re building <strong>right
            now</strong> — the project a recruiter should ask you about first.
          </p>
          <p className="reveal">
            A single line that captures how you think.{" "}
            <em>&quot;A short personal motto fits well here.&quot;</em>
          </p>

          <div className="stats reveal">
            {stats.map((s) => (
              <div key={s.label} className="stat">
                <div className="stat-num">{s.num}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
