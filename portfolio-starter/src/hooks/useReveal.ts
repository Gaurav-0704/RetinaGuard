import { useEffect, useRef } from "react";

// Reveals elements when they scroll into view.
// Each matching child gets a stagger delay and gets a `.revealed` class
// once it crosses the viewport threshold. Works with CSS transitions.
export function useReveal<T extends HTMLElement = HTMLElement>(
  selector: string = ".reveal",
  options: IntersectionObserverInit = {
    threshold: 0.15,
    rootMargin: "0px 0px -40px 0px",
  }
) {
  const ref = useRef<T>(null);

  useEffect(() => {
    const root = ref.current;
    if (!root) return;
    const items = root.querySelectorAll<HTMLElement>(selector);
    if (!items.length) return;

    items.forEach((el, i) => {
      el.style.setProperty("--reveal-delay", `${i * 90}ms`);
    });

    const obs = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("revealed");
          obs.unobserve(entry.target);
        }
      });
    }, options);

    items.forEach((item) => obs.observe(item));
    return () => obs.disconnect();
  }, [selector, options]);

  return ref;
}
