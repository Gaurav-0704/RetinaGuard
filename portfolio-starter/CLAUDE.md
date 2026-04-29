# Instructions for Claude (or any AI coding assistant)

You are helping the owner of this repo turn a generic 3D portfolio starter into **their own** portfolio. Read this entire file before making any changes.

## Hard rules

1. **Do not ship the starter as-is.** This template was sanitized — every data file is filled with placeholder text. The user will give you their resume / LinkedIn / project list. Replace every placeholder with their real info.

2. **Build a 3D hero that is visually different from the starter's `TechGlobe`.** The starter ships with a wireframe sphere of orbiting tech labels. **Pick something different.** Suggested directions (let the user choose, or pick based on their domain):

   - **Particle system** — thousands of points that swirl, react to the cursor, optionally form shapes.
   - **Neural network graph** — nodes in 3-4 layers with animated signal pulses (good for ML/AI engineers).
   - **Floating geometric shapes** — torus knots, icosahedrons, twisted ribbons with shader effects.
   - **Wireframe terrain / mesh** — animated topographic landscape (good for data/infra people).
   - **Custom 3D model** — load a .glb (their logo, monogram, an object related to their field).
   - **Distorted blob / shader sphere** — single mesh with a custom GLSL displacement shader.

   Replace `src/components/TechGlobe.tsx` with the new scene. Keep the file name or rename it (e.g., `Hero3D.tsx`) and update the import in `Landing.tsx`. The 3D scene should fill the hero, slowly idle-animate, and respond subtly to the mouse.

3. **Pick a different color theme.** The starter uses cyan + amber on a midnight background. Pick a palette that fits the user. Edit the CSS custom properties at the top of `src/styles/global.css`. Suggested palettes:

   - **Warm sunset** — `--bg: #18120e`, `--accent: #ff8a4c`, `--warm: #ffd166`
   - **Mint forest** — `--bg: #07131a`, `--accent: #4ade80`, `--warm: #22d3ee`
   - **Magenta neon** — `--bg: #0e0820`, `--accent: #ff3ec9`, `--warm: #a78bfa`
   - **Monochrome paper** — `--bg: #f7f6f1`, `--fg: #181412`, `--accent: #c75c2e` (light theme — flip text/bg as needed)
   - **Royal blue** — `--bg: #050a1a`, `--accent: #4f8cff`, `--warm: #ffd166`

   Update the matching THREE.Color constants in the new 3D scene to match.

4. **Replace ALL content in `src/data/`** with the user's real data. The file structure is:
   - `personal.ts` — name, email, phone, location, links
   - `navigation.ts` — section labels in the navbar
   - `techs.ts` — labels for the 3D scene (or remove if your new scene doesn't need them)
   - `skills.ts` — skill groups
   - `experience.ts` — work history (most recent first)
   - `projects.ts` — projects (each can have an optional `github` link)
   - `education.ts` — degree, certifications, leadership
   - `about.ts` — three stat cards

5. **Edit `src/components/About.tsx`** — it has three short hardcoded paragraphs (the only narrative copy not driven by data). Rewrite them in the user's voice from their resume.

6. **Edit `index.html`** — set a real `<title>` and `<meta name="description">`.

7. **Keep the structure intact unless asked otherwise.** Sections in order: Landing (hero) → Intro → About → Skills → Experience → Projects → Education → Contact. Don't delete sections without confirming.

## Workflow

When the user starts the conversation:

1. Ask for their resume, LinkedIn, or a brain-dump of their projects and experience.
2. Ask which **3D scene direction** they want from rule #2 (or propose one based on their field).
3. Ask which **color palette** they want from rule #3 (or propose one).
4. Update `src/data/*` with their content.
5. Build the new 3D scene component, replace `TechGlobe`, wire it into `Landing.tsx`.
6. Update the theme tokens in `src/styles/global.css`.
7. Edit `About.tsx` paragraphs.
8. Edit `index.html` title and description.
9. Run `npm run build` to verify everything compiles.
10. Walk the user through pushing to GitHub and deploying on Vercel.

## Things you should not do

- **Do not** keep the starter's tech globe as the hero. Replace it.
- **Do not** keep the cyan + amber palette. Pick something else that fits the user.
- **Do not** invent fake achievements, degrees, or projects. Use only what the user gives you.
- **Do not** add a strict "no copying" license. The starter ships with MIT — leave it permissive unless the user explicitly asks for something stricter.
- **Do not** add tracking, analytics, or social-share buttons unless the user asks.

## Run instructions for the user

```bash
npm install
npm run dev
```

Open the URL Vite prints. Hot reload picks up every save.

To deploy: push to GitHub → import in Vercel → done.
