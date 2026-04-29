import { useReveal } from "../hooks/useReveal";
import { testimonials } from "../data/testimonials";

// A simple grid of pull-quote cards. Hides itself if the testimonials
// array is empty — better than rendering an awkward placeholder.
export default function Testimonials() {
  const ref = useReveal<HTMLElement>(".reveal");
  if (testimonials.length === 0) return null;

  return (
    <section ref={ref} className="section testimonials" id="testimonials">
      <div className="section-inner">
        <p className="eyebrow reveal">— Voices</p>
        <h2 className="section-title reveal">Words from people I&apos;ve worked with</h2>
        <div className="testimonial-grid">
          {testimonials.map((t, i) => (
            <figure key={i} className="testimonial-card reveal">
              <svg
                className="quote-mark"
                viewBox="0 0 24 24"
                width="22"
                height="22"
                fill="currentColor"
                aria-hidden
              >
                <path d="M7 4c-3 0-5 2-5 5s2 5 5 5h1l-2 6h4l3-9V4H7zm10 0c-3 0-5 2-5 5s2 5 5 5h1l-2 6h4l3-9V4h-6z" />
              </svg>
              <blockquote>
                <p>&ldquo;{t.quote}&rdquo;</p>
              </blockquote>
              <figcaption>
                <span className="testimonial-avatar" aria-hidden>{t.initials}</span>
                <span>
                  <strong>{t.name}</strong>
                  <span className="testimonial-role">{t.role}</span>
                </span>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
