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
    name: "Data Integration & Analysis",
    tagline: "Turning messy multi-source data into one analysis-ready story",
    description:
      "Combined and cleaned several large, real-world datasets into a single unified table, then ran exploratory analysis to surface the patterns that mattered for downstream business decisions.",
    highlights: [
      "Merged disparate sources with Pandas and SQL joins, handling nulls, duplicates, and schema mismatches end-to-end.",
      "Performed EDA to surface outliers, segment behaviour, and key trends that drove the headline recommendations.",
      "Documented the full pipeline and findings in a reproducible Jupyter Notebook for stakeholder review.",
    ],
    stack: ["Python", "Pandas", "SQL", "Jupyter"],
    tag: "Analytics",
  },
  {
    name: "Interactive Tableau Dashboards",
    tagline: "Self-serve BI that lets non-technical leaders drill into their own questions",
    description:
      "Designed interactive dashboards that translate raw operational data into clear, story-driven KPIs. Built specifically for business users — they can filter, drill down, and reach a conclusion without ever asking an analyst.",
    highlights: [
      "Modeled KPIs and built filters, calculated fields, and parameters so users can slice by category, time, and region.",
      "Applied visualization best practices — consistent encodings, ranked dimensions, clean layout — for executive readability.",
      "Translated raw data into narrative visuals that supported concrete, data-informed business recommendations.",
    ],
    stack: ["Tableau", "Data Modeling", "BI"],
    tag: "Dashboard",
  },
  {
    name: "Supply Chain Analysis Case Study",
    tagline: "Cutting holding costs and stock-outs by re-examining replenishment policy",
    description:
      "Audited inventory and replenishment strategy for a case-study retailer using PivotTables, VLOOKUP, and scenario analysis. Output was an executive-style brief — not a wall of formulas — with concrete next steps.",
    highlights: [
      "Built scenario models in Excel to compare reorder policies under different demand assumptions.",
      "Identified specific SKUs driving overstock and stock-outs, and quantified the holding-cost impact.",
      "Summarized findings for non-technical leadership with clear, prioritized recommendations.",
    ],
    stack: ["Excel", "PivotTables", "Scenario Analysis"],
    tag: "Case Study",
  },
  {
    name: "Diabetic Retinopathy Severity Classifier",
    tagline: "End-to-end ML pipeline that grades retinal scans for early detection",
    description:
      "Capstone project applying supervised learning and image processing to classify diabetic retinopathy severity from retinal images — showing how data science can support earlier, faster medical screening.",
    highlights: [
      "Preprocessed images with normalization and augmentation to improve robustness and model accuracy.",
      "Trained a multi-class classifier and benchmarked it against baseline models on held-out data.",
      "Delivered a complete ML workflow — data prep → training → evaluation → presentation — as a capstone.",
    ],
    stack: ["Python", "Scikit-learn", "Image Processing", "ML"],
    tag: "Capstone",
  },
];
