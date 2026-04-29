// Work experience timeline.
// Most recent first.

export type Role = {
  title: string;
  company: string;
  location: string;
  period: string;
  bullets: string[];
  stack: string[];
};

export const roles: Role[] = [
  {
    title: "Your Role Title",
    company: "Company Name",
    location: "City, Country",
    period: "Month YYYY – Present",
    bullets: [
      "Replace each bullet with a one-sentence accomplishment focused on impact, not tasks.",
      "Quantify outcomes wherever possible — % improvements, scale, headcount, revenue.",
      "Aim for 2–4 bullets per role.",
    ],
    stack: ["Tech 1", "Tech 2", "Tech 3"],
  },
  {
    title: "Previous Role Title",
    company: "Previous Company",
    location: "City, Country",
    period: "Month YYYY – Month YYYY",
    bullets: [
      "Bullet describing what you shipped and why it mattered.",
      "Bullet describing a technical or business win.",
    ],
    stack: ["Tech 1", "Tech 2"],
  },
];
