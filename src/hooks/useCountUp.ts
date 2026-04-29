import { useEffect, useRef, useState } from "react";

// Counts a number up from 0 to `target` once the element scrolls into view.
// Returns a ref to attach + the current display value as a string.
//
// `target` may be a number with optional unit (e.g. "4+", "1 yr", "100+").
// Anything non-numeric is preserved on the way through.
export function useCountUp(rawTarget: string, durationMs: number = 1100) {
  const ref = useRef<HTMLDivElement>(null);
  const [value, setValue] = useState<string>(() => {
    // Initial state: the same string but with the digits zeroed out so the
    // layout doesn't jump when the animation kicks in.
    return rawTarget.replace(/\d+(\.\d+)?/, (m) => "0".repeat(m.length));
  });

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const match = rawTarget.match(/(\d+(\.\d+)?)/);
    if (!match) {
      setValue(rawTarget);
      return;
    }
    const targetNum = parseFloat(match[1]);
    const decimals = match[2] ? match[2].length - 1 : 0;
    const prefix = rawTarget.slice(0, match.index);
    const suffix = rawTarget.slice((match.index ?? 0) + match[1].length);

    let started = false;
    const obs = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting && !started) {
            started = true;
            const start = performance.now();
            const tick = (now: number) => {
              const t = Math.min(1, (now - start) / durationMs);
              // Ease-out for a satisfying "settle" at the end.
              const eased = 1 - Math.pow(1 - t, 3);
              const cur = targetNum * eased;
              setValue(`${prefix}${cur.toFixed(decimals)}${suffix}`);
              if (t < 1) requestAnimationFrame(tick);
              else setValue(rawTarget);
            };
            requestAnimationFrame(tick);
            obs.disconnect();
          }
        }
      },
      { threshold: 0.4 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [rawTarget, durationMs]);

  return { ref, value };
}
