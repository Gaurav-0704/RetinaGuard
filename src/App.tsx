import { useState } from "react";

import Navbar from "./components/Navbar";
import Cursor from "./components/Cursor";
import Loading from "./components/Loading";

import Landing from "./components/Landing";
import Intro from "./components/Intro";
import About from "./components/About";
import Skills from "./components/Skills";
import Experience from "./components/Experience";
import Projects from "./components/Projects";
import Testimonials from "./components/Testimonials";
import Education from "./components/Education";
import Contact from "./components/Contact";

export default function App() {
  const [loaded, setLoaded] = useState(false);

  return (
    <>
      {!loaded && <Loading onDone={() => setLoaded(true)} />}
      <Cursor />
      <Navbar />
      <main id="main" className={loaded ? "app-ready" : "app-booting"}>
        <Landing />
        <Intro />
        <About />
        <Skills />
        <Experience />
        <Projects />
        <Testimonials />
        <Education />
        <Contact />
      </main>
    </>
  );
}
