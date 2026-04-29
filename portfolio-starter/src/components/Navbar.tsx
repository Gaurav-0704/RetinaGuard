import { useEffect, useState } from "react";
import { navLinks } from "../data/navigation";
import { personal } from "../data/personal";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  // Collapse the bar after the user scrolls past the hero.
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav className={`navbar ${scrolled ? "navbar-scrolled" : ""}`}>
      <a className="navbar-brand" href="#top">
        <span className="brand-dot" />
        {personal.firstName}
        <span className="brand-accent">.</span>
      </a>
      <ul className="navbar-links">
        {navLinks.map((l) => (
          <li key={l.href}>
            <a href={l.href}>{l.label}</a>
          </li>
        ))}
      </ul>
      <a className="navbar-cta" href={`mailto:${personal.email}`}>
        Let&apos;s talk
      </a>
    </nav>
  );
}
