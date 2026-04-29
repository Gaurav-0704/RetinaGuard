// Projects shown on the portfolio.
// Order here = order on the page.

export type Project = {
  name: string;
  tagline: string;
  description: string;
  highlights: string[];
  stack: string[];
  tag: string;
  github?: string; // optional — renders a "View on GitHub" link on the card
};

export const projects: Project[] = [
  {
    name: "Project One",
    tagline: "One-line description of what it does",
    description:
      "Replace with 2–3 sentences. Focus on the problem, your approach, and the outcome. Write so a smart non-engineer can follow it.",
    highlights: [
      "What was technically interesting about this build?",
      "What was the measurable impact?",
      "Add 3–5 bullets per project. Quantify where possible.",
    ],
    stack: ["Tech 1", "Tech 2", "Tech 3"],
    tag: "Production",
    github: "https://github.com/your-handle/project-one",
  },
  {
    name: "Project Two",
    tagline: "Another short one-line description",
    description:
      "2–3 sentence description for project two. Pick projects that show range — different stacks, different domains, different scales.",
    highlights: [
      "First highlight.",
      "Second highlight.",
      "Third highlight.",
    ],
    stack: ["Tech 1", "Tech 2"],
    tag: "Side project",
  },
  {
    name: "Project Three",
    tagline: "Short description",
    description:
      "Another project. For a portfolio, 4–6 well-described projects beat 12 thinly-described ones.",
    highlights: [
      "Highlight one.",
      "Highlight two.",
    ],
    stack: ["Tech 1", "Tech 2"],
    tag: "Research",
  },
];
