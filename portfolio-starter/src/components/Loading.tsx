import { useEffect, useState } from "react";
import { personal } from "../data/personal";

// Fake progress bar shown on first paint so the page never flashes empty
// while the 3D scene's Three.js assets warm up.
export default function Loading({ onDone }: { onDone: () => void }) {
  // Initials derived from your name in src/data/personal.ts
  const initials = personal.name
    .split(/\s+/)
    .map((w) => w[0]?.toUpperCase() ?? "")
    .join("")
    .slice(0, 3) || "YOU";

  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let p = 0;
    const id = setInterval(() => {
      p += Math.random() * 12 + 4;
      if (p >= 100) {
        setProgress(100);
        clearInterval(id);
        setTimeout(onDone, 400);
      } else {
        setProgress(Math.floor(p));
      }
    }, 120);
    return () => clearInterval(id);
  }, [onDone]);

  return (
    <div className="loader">
      <div className="loader-inner">
        <div className="loader-brand">{initials}</div>
        <div className="loader-bar">
          <div className="loader-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="loader-pct">{progress}%</div>
      </div>
    </div>
  );
}
