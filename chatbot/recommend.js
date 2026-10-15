// Public Invention's recommendation rules for the browser.
// Mirrors pipeline/ranking.py; tests/ranking_cases.json keeps them in step.

export const EXCLUDED_TITLES = ["Moonrat", "Oxygen Concentrator", "PolyVent", "ADaM", "Librecorder"];
export const STATUS_ORDER = { "Highly Active": 1, "Progress but Inactive": 2, "Ready-to-start": 3 };
const HIDDEN_STATUSES = new Set(["Preliminary"]);
const MIN_README_MATCHES = 2;

export function isEligible(project) {
  const title = (project.project || "").toLowerCase();
  if (EXCLUDED_TITLES.some((name) => title.includes(name.toLowerCase()))) return false;
  if (HIDDEN_STATUSES.has(project.status || "")) return false;
  return project.seeking_volunteers !== "no";
}

export function statusRank(status) {
  return STATUS_ORDER[status] ?? Object.keys(STATUS_ORDER).length + 1;
}

const lower = (list) => new Set((list || []).map((s) => s.toLowerCase()));

/** Rank eligible projects: status first, then skill matches, then the sheet's Order priority. */
export function recommend(projects, { have = [], want = [], category = "", limit = 5 } = {}) {
  const haveSet = lower(have);
  const wantSet = lower(want);
  const ranked = [];
  for (const project of projects) {
    if (!(project.eligible ?? isEligible(project))) continue;
    if (category && (project.category || "").toLowerCase() !== category.toLowerCase()) continue;
    const sheet = project.skills || [];
    const skills = sheet.length ? sheet : project.readme_skills || [];
    const matchedHave = skills.filter((s) => haveSet.has(s.toLowerCase()));
    const matchedWant = skills.filter((s) => wantSet.has(s.toLowerCase()));
    const matches = matchedHave.length + matchedWant.length;
    if ((haveSet.size || wantSet.size) && matches < (sheet.length ? 1 : MIN_README_MATCHES)) continue;
    ranked.push({ project, matchedHave, matchedWant, key: [statusRank(project.status), -matches, -(project.priority || 0), project.project] });
  }
  ranked.sort((a, b) => {
    for (let i = 0; i < a.key.length; i++) {
      if (a.key[i] < b.key[i]) return -1;
      if (a.key[i] > b.key[i]) return 1;
    }
    return 0;
  });
  return ranked.slice(0, limit);
}

/** Pick known skills out of free text like "I do Arduino and some 3D printing". */
export function skillsFromText(text, skills, aliases = {}) {
  const low = ` ${(text || "").toLowerCase()} `;
  const found = new Set();
  for (const skill of skills) {
    if (low.includes(skill.toLowerCase())) found.add(skill);
  }
  for (const [phrase, mapped] of Object.entries(aliases)) {
    if (phrase.startsWith("_") || phrase.length < 4) continue;
    if (low.includes(phrase)) mapped.filter((s) => skills.includes(s)).forEach((s) => found.add(s));
  }
  return [...found].sort();
}
