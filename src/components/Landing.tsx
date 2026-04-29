import { Suspense, lazy, useEffect, useRef } from "react";
import gsap from "gsap";
import { personal } from "../data/personal";

const Hero3D = lazy(() => import("./Hero3D"));

export default function Landing() {
  const root = useRef<HTMLElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from(".hero-meta-top", { y: -20, opacity: 0, duration: 0.8, delay: 0.3, ease: "power3.out" });
      gsap.from(".hero-name",     { y: 30,  opacity: 0, duration: 1.1, delay: 0.5, ease: "power4.out" });
      gsap.from(".hero-role",     { y: 20,  opacity: 0, duration: 0.9, delay: 0.75, ease: "power3.out" });
      gsap.from(".hero-scroll",   {         opacity: 0, duration: 1.2, delay: 1.1, ease: "power2.out" });
      gsap.from(".globe-canvas",  {         opacity: 0, duration: 1.8, delay: 0.1, ease: "power2.out" });
    }, root);
    return () => ctx.revert();
  }, []);

  return (
    <section ref={root} className="landing" id="top">
      <div className="globe-wrapper">
        <Suspense fallback={<div className="hero-fallback" aria-hidden />}>
          <Hero3D />
        </Suspense>
      </div>

      <div className="hero-overlay">
        <div className="hero-meta-top">
          <span className="hero-tag">
            <span className="status-dot" /> {personal.availability}
          </span>
        </div>

        <div className="hero-center">
          <h1 className="hero-name">
            {personal.firstName}
            <span className="accent">.</span>
          </h1>
          <p className="hero-role">{personal.role}</p>
        </div>

        <a className="hero-scroll" href="#intro" aria-label="Scroll to intro">
          <span className="hero-scroll-line" />
          <span className="hero-scroll-label">scroll</span>
        </a>
      </div>
    </section>
  );
}
