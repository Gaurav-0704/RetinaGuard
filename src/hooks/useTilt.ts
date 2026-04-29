import { useEffect, useRef } from "react";

// Lightweight 3D tilt-on-hover. Tracks the mouse over the element and
// rotates it on the X/Y axes in proportion to cursor position. Returns to
// rest smoothly when the cursor leaves. Skips entirely on touch devices
// and when the user prefers reduced motion.
export function useTilt<T extends HTMLElement = HTMLDivElement>(
  maxTiltDeg = 7,
  glare = true,
) {
  const ref = useRef<T>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (window.matchMedia("(pointer: coarse)").matches) return;

    let raf = 0;
    let tx = 0, ty = 0;
    let cx = 0, cy = 0;
    let gx = 50, gy = 50;
    let active = false;

    const onMove = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect();
      const px = (e.clientX - rect.left) / rect.width;
      const py = (e.clientY - rect.top) / rect.height;
      tx = (py - 0.5) * -2 * maxTiltDeg;
      ty = (px - 0.5) *  2 * maxTiltDeg;
      gx = px * 100;
      gy = py * 100;
      active = true;
    };

    const onLeave = () => {
      tx = 0; ty = 0;
      active = false;
    };

    const tick = () => {
      cx += (tx - cx) * 0.12;
      cy += (ty - cy) * 0.12;
      el.style.transform =
        `perspective(900px) rotateX(${cx.toFixed(2)}deg) rotateY(${cy.toFixed(2)}deg)`;
      if (glare) {
        el.style.setProperty("--glare-x", `${gx.toFixed(1)}%`);
        el.style.setProperty("--glare-y", `${gy.toFixed(1)}%`);
        el.style.setProperty("--glare-opacity", active ? "0.55" : "0");
      }
      raf = requestAnimationFrame(tick);
    };

    el.addEventListener("mousemove", onMove);
    el.addEventListener("mouseleave", onLeave);
    raf = requestAnimationFrame(tick);

    return () => {
      el.removeEventListener("mousemove", onMove);
      el.removeEventListener("mouseleave", onLeave);
      cancelAnimationFrame(raf);
    };
  }, [maxTiltDeg, glare]);

  return ref;
}
