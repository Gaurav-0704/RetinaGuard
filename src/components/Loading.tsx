import { useEffect, useState } from "react";
import { personal } from "../data/personal";

// Loading screen: types out the user's name letter by letter while a thin
// progress bar fills underneath. Reads as intentional craftsmanship rather
// than a dead "please wait" state.
export default function Loading({ onDone }: { onDone: () => void }) {
  const fullName = personal.name;
  const [typed, setTyped] = useState("");
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let i = 0;
    const id = setInterval(() => {
      i += 1;
      setTyped(fullName.slice(0, i));
      if (i >= fullName.length) clearInterval(id);
    }, 70);
    return () => clearInterval(id);
  }, [fullName]);

  useEffect(() => {
    let p = 0;
    const id = setInterval(() => {
      p += Math.random() * 11 + 3;
      if (p >= 100) {
        setProgress(100);
        clearInterval(id);
        setTimeout(onDone, 500);
      } else {
        setProgress(Math.floor(p));
      }
    }, 130);
    return () => clearInterval(id);
  }, [onDone]);

  return (
    <div className="loader" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
      <div className="loader-inner">
        <div className="loader-name">
          <span className="loader-name-text">{typed}</span>
          <span className="loader-caret" aria-hidden>|</span>
        </div>
        <div className="loader-bar">
          <div className="loader-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="loader-pct">{progress}%</div>
      </div>
    </div>
  );
}
