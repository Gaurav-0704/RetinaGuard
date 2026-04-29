// The skill grid.
// Each skill has a 0-100 level. Set them honestly — interviewers can tell.

export type Skill = { name: string; level: number };

export type SkillGroup = {
  title: string;
  items: Skill[];
};

export const skillGroups: SkillGroup[] = [
  {
    title: "Programming & Query",
    items: [
      { name: "Python (Pandas, NumPy, Scikit-learn)", level: 88 },
      { name: "SQL", level: 90 },
      { name: "R", level: 70 },
      { name: "Java", level: 78 },
    ],
  },
  {
    title: "Data & BI Tools",
    items: [
      { name: "Tableau", level: 88 },
      { name: "Power BI", level: 75 },
      { name: "Excel — PivotTables, VLOOKUP, Power Query", level: 92 },
      { name: "SPSS", level: 70 },
      { name: "Jupyter Notebook", level: 88 },
    ],
  },
  {
    title: "Analytics & Methods",
    items: [
      { name: "Data Cleaning & Wrangling", level: 92 },
      { name: "Exploratory Data Analysis", level: 88 },
      { name: "Regression & Statistical Modeling", level: 80 },
      { name: "Data Visualization", level: 88 },
      { name: "A/B Testing", level: 70 },
      { name: "Machine Learning Fundamentals", level: 75 },
    ],
  },
  {
    title: "Cloud & Other",
    items: [
      { name: "AWS Cloud Foundations", level: 65 },
      { name: "Git / GitHub", level: 85 },
      { name: "MS Office Suite", level: 95 },
    ],
  },
  {
    title: "Soft Skills",
    items: [
      { name: "Analytical Thinking", level: 92 },
      { name: "Stakeholder Communication", level: 90 },
      { name: "Cross-functional Collaboration", level: 88 },
      { name: "Leadership", level: 85 },
      { name: "Presentation", level: 90 },
    ],
  },
];
