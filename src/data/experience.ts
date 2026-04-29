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
    title: "Java Developer Intern",
    company: "GVS IT Solutions",
    location: "Hyderabad, India",
    period: "Sep 2023 – Sep 2024",
    bullets: [
      "Built, deployed, and maintained Java-based applications on an agile team, contributing features across multiple release cycles.",
      "Integrated applications with SQL and NoSQL databases, writing optimized queries to retrieve and transform large volumes of business data.",
      "Partnered with QA, product, and design teammates to translate stakeholder requirements into shipped features and resolve production issues.",
      "Improved code efficiency and reduced post-release defects through code reviews, refactoring, and unit / system testing.",
    ],
    stack: ["Java", "SQL", "NoSQL", "Git", "Agile"],
  },
];
