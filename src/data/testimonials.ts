// Pull-quotes from professors, managers, or teammates.
// Replace each placeholder with a real quote you have permission to use.
// If you don't have any yet, leave this list empty — the section will hide.

export type Testimonial = {
  quote: string;
  name: string;
  role: string;
  initials: string; // 1–2 letters; rendered as a circular avatar
};

export const testimonials: Testimonial[] = [
  {
    quote:
      "Niharika has a rare combination of analytical precision and clear communication. She turns complex datasets into recommendations our non-technical leads can act on the same day.",
    name: "Placeholder — replace with a real quote",
    role: "Professor / Manager / Teammate · School or Company",
    initials: "PR",
  },
  {
    quote:
      "She owned the data pipeline end-to-end and pushed back when the numbers didn't make sense. That instinct is what separates a good analyst from a great one.",
    name: "Placeholder — replace with a real quote",
    role: "Project Sponsor · GVS IT Solutions",
    initials: "GV",
  },
  {
    quote:
      "Her Tableau dashboards are the cleanest I've seen from a student — she clearly thinks about the reader before the chart.",
    name: "Placeholder — replace with a real quote",
    role: "Capstone Reviewer · University of Dayton",
    initials: "UD",
  },
];
