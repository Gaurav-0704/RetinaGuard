// The skill grid.
// Add a new object to the array to add a new group.

export type SkillGroup = {
  title: string;
  items: string[];
};

export const skillGroups: SkillGroup[] = [
  { title: "Languages",      items: ["JavaScript", "TypeScript", "Python", "Java"] },
  { title: "Frontend",       items: ["React", "Next.js", "Vite", "Tailwind CSS", "HTML", "CSS"] },
  { title: "Backend",        items: ["Node.js", "Express", "REST APIs", "GraphQL"] },
  { title: "Data",           items: ["PostgreSQL", "MongoDB", "Redis", "SQL"] },
  { title: "Cloud & DevOps", items: ["AWS", "Docker", "Git", "GitHub Actions", "Linux"] },
  { title: "Domains",        items: ["Domain 1", "Domain 2", "Domain 3"] },
];
