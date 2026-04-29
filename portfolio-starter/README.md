# Portfolio Starter — 3D React + Vite

A working starter for a personal portfolio website with a 3D hero scene, smooth section reveals, custom cursor, and a clean data-driven structure. **Use it as a starting point — don't ship it as-is.** Read [`CLAUDE.md`](./CLAUDE.md) before you begin.

## Stack

- React 18 + TypeScript + Vite
- Three.js via `@react-three/fiber` + `@react-three/drei`
- GSAP for entrance animations
- `react-icons`

## Quick start

You need Node 18+.

```bash
npm install
npm run dev
```

Open http://localhost:5173.

Build for production:

```bash
npm run build
npm run preview
```

## Project layout

```
src/
├── App.tsx              # composes all sections
├── main.tsx             # React entry
├── components/          # UI components (hero, sections, navbar, cursor, loader)
├── data/                # ALL CONTENT — edit these files first
├── hooks/               # useReveal hook
└── styles/
    └── global.css       # theme tokens at the very top
```

All content (projects, experience, skills, personal info) lives in `src/data/`. Edit the data files — never hardcode personal info inside JSX.

| To change                       | Edit                                 |
| ------------------------------- | ------------------------------------ |
| Name, email, phone, links       | `src/data/personal.ts`               |
| Nav bar items                   | `src/data/navigation.ts`             |
| Tech labels in the hero scene   | `src/data/techs.ts`                  |
| Skills grid                     | `src/data/skills.ts`                 |
| Work experience                 | `src/data/experience.ts`             |
| Projects                        | `src/data/projects.ts`               |
| Education, certs, leadership    | `src/data/education.ts`              |
| About stat cards                | `src/data/about.ts`                  |
| About section copy              | `src/components/About.tsx` (3 short paragraphs) |
| Colors & theme tokens           | `src/styles/global.css` (top of file)|
| 3D scene                        | `src/components/TechGlobe.tsx` ← **REPLACE THIS** |

## Deploy to Vercel

1. Push this folder to a GitHub repo (public or private).
2. Sign in to https://vercel.com with GitHub.
3. **Add New → Project → Import** the repo. Vercel auto-detects Vite → click **Deploy**.

Every future `git push` redeploys the live URL automatically.

## License

MIT — see [LICENSE](./LICENSE). Do whatever you want with the code.
