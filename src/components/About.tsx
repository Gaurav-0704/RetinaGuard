import { useReveal } from "../hooks/useReveal";
import { useCountUp } from "../hooks/useCountUp";
import { stats } from "../data/about";

export default function About() {
  const ref = useReveal<HTMLElement>(".reveal");

  return (
    <section ref={ref} className="section about" id="about">
      <div className="section-inner">
        <p className="eyebrow reveal">01 — About</p>
        <h2 className="section-title reveal">
          I turn messy data into{" "}
          <span className="accent">decisions people can act on</span>.
        </h2>

        <div className="about-grid">
          <p className="reveal">
            I&apos;m a Master&apos;s student in Business Analytics at the
            University of Dayton, with a B.Tech in Information Technology and a
            year as a Java developer behind me. That mix means I&apos;m as
            comfortable writing the SQL and the Python as I am presenting the
            findings to a non-technical room.
          </p>
          <p className="reveal">
            Right <strong>now</strong> I&apos;m focused on the work between raw
            data and the decision &mdash; cleaning, modelling, and translating
            it into Tableau dashboards and executive briefs that don&apos;t
            need a translator. Capstone work on a diabetic-retinopathy
            classifier proved out the same loop end-to-end.
          </p>
          <p className="reveal">
            <em>&ldquo;The number on the slide is the easy part &mdash; the
            work is making sure it&apos;s the right number.&rdquo;</em>
          </p>

          <div className="stats reveal">
            {stats.map((s) => (
              <Stat key={s.label} num={s.num} label={s.label} />
            ))}
          </div>
        </div>

        <div className="now-block reveal">
          <div className="now-pulse" aria-hidden>
            <span className="now-dot" />
            <span>Currently</span>
          </div>
          <ul className="now-list">
            <li>
              <strong>Studying</strong> &mdash; Predictive Analytics, Statistical
              Modeling, and Database Management at UD.
            </li>
            <li>
              <strong>Building</strong> &mdash; interactive Tableau dashboards
              and a cleaner write-up of my retinopathy-classifier capstone.
            </li>
            <li>
              <strong>Looking for</strong> &mdash; a Summer 2026 analytics
              internship and a full-time Data / Business Analyst role.
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}

function Stat({ num, label }: { num: string; label: string }) {
  const { ref, value } = useCountUp(num);
  return (
    <div className="stat">
      <div className="stat-num" ref={ref}>{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
