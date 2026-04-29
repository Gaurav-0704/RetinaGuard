import { useState } from "react";
import { FaLinkedin, FaGithub, FaEnvelope, FaPhone, FaFilePdf, FaPaperPlane } from "react-icons/fa";
import { useReveal } from "../hooks/useReveal";
import { personal } from "../data/personal";

const FORM_ENDPOINT = (import.meta as { env?: Record<string, string | undefined> }).env
  ?.VITE_CONTACT_ENDPOINT;

export default function Contact() {
  const ref = useReveal<HTMLElement>(".reveal");
  const [status, setStatus] = useState<"idle" | "sending" | "ok" | "error">("idle");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);
    const name = String(data.get("name") || "");
    const fromEmail = String(data.get("email") || "");
    const message = String(data.get("message") || "");

    if (!FORM_ENDPOINT) {
      const subject = encodeURIComponent(`Portfolio enquiry from ${name || "(no name)"}`);
      const body = encodeURIComponent(
        `${message}\n\n— ${name}${fromEmail ? `\n${fromEmail}` : ""}`,
      );
      window.location.href = `mailto:${personal.email}?subject=${subject}&body=${body}`;
      return;
    }

    try {
      setStatus("sending");
      const res = await fetch(FORM_ENDPOINT, {
        method: "POST",
        headers: { Accept: "application/json" },
        body: data,
      });
      if (res.ok) {
        setStatus("ok");
        form.reset();
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  }

  return (
    <section ref={ref} className="section contact" id="contact">
      <div className="section-inner contact-inner">
        <p className="eyebrow reveal">07 — Contact</p>
        <h2 className="section-title reveal">
          Let&apos;s build something that{" "}
          <span className="accent">moves the number</span>.
        </h2>
        <p className="contact-sub reveal">
          Open to Summer 2026 analytics internships and full-time Data /
          Business Analyst roles. Quickest way to reach me is below &mdash; or
          pull the resume for the full picture.
        </p>

        <div className="contact-cta-row reveal">
          <a className="btn btn-primary" href="/resume.pdf" download>
            <FaFilePdf style={{ marginRight: 8 }} />
            Download Resume
          </a>
          <a className="btn btn-ghost" href={`mailto:${personal.email}`}>
            <FaEnvelope style={{ marginRight: 8 }} />
            {personal.email}
          </a>
        </div>

        <form className="contact-form reveal" onSubmit={onSubmit} noValidate>
          <div className="contact-form-row">
            <label className="contact-field">
              <span>Your name</span>
              <input name="name" type="text" required autoComplete="name" />
            </label>
            <label className="contact-field">
              <span>Your email</span>
              <input name="email" type="email" required autoComplete="email" />
            </label>
          </div>
          <label className="contact-field">
            <span>Message</span>
            <textarea name="message" rows={5} required />
          </label>
          <button
            type="submit"
            className="btn btn-primary contact-submit"
            disabled={status === "sending"}
          >
            <FaPaperPlane style={{ marginRight: 8 }} />
            {status === "sending"
              ? "Sending..."
              : status === "ok"
              ? "Sent — thank you"
              : "Send message"}
          </button>
          {status === "error" && (
            <p className="contact-error" role="alert">
              Couldn&apos;t deliver the message &mdash; try emailing me directly at{" "}
              <a href={`mailto:${personal.email}`}>{personal.email}</a>.
            </p>
          )}
          {!FORM_ENDPOINT && (
            <p className="contact-note">
              <span className="muted">
                Tip: set <code>VITE_CONTACT_ENDPOINT</code> in <code>.env</code>{" "}
                to a Formspree URL to enable in-page submission.
              </span>
            </p>
          )}
        </form>

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
