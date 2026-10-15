// Public Invention Project Finder: a guided chat that recommends projects from data/projects.json.
// Embed: <div id="pubinv-project-finder"></div><script type="module" src=".../chatbot/widget.js"></script>
// The ranking itself lives in recommend.js; this file only asks questions and renders answers.
import { recommend, skillsFromText } from "./recommend.js";

const DEFAULT_DATA = "https://raw.githubusercontent.com/PubInv/Project-ChatBot/main/data/";
const VOLUNTEER_URL = "https://www.pubinv.org/volunteer/";
const JOINABILITY = { 1: "Easy to join", 2: "Join with a mentor", 3: "You may have to start it yourself" };

const STYLES = `
  :host { all: initial; display: block; font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; color: #142b4d; }
  .box { max-width: 720px; margin: 0 auto; border: 1px solid #ccd7e8; border-radius: 14px; background: #fff; overflow: hidden; }
  .head { padding: 14px 18px; background: #142b4d; color: #fff; font-weight: 700; }
  .log { padding: 16px; display: flex; flex-direction: column; gap: 10px; max-height: 640px; overflow-y: auto; }
  .bot, .me { padding: 10px 14px; border-radius: 12px; max-width: 88%; }
  .bot { background: #eef3ff; align-self: flex-start; }
  .me { background: #2f66dc; color: #fff; align-self: flex-end; }
  .controls { border-top: 1px solid #ccd7e8; padding: 12px 16px; display: flex; flex-direction: column; gap: 10px; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .chip { border: 1px solid #a9bbd6; background: #fff; color: #142b4d; border-radius: 999px; padding: 4px 12px; cursor: pointer; font: inherit; font-size: 14px; }
  .chip[aria-pressed="true"] { background: #2f66dc; border-color: #2f66dc; color: #fff; }
  .row { display: flex; gap: 8px; }
  input { flex: 1; min-width: 0; padding: 8px 12px; border: 1px solid #a9bbd6; border-radius: 8px; font: inherit; }
  .main { display: inline-block; text-decoration: none; background: #2f66dc; color: #fff; border: 0; border-radius: 8px; padding: 8px 16px; font: inherit; font-weight: 600; cursor: pointer; }
  button.ghost { background: none; border: 1px solid #a9bbd6; color: #142b4d; border-radius: 8px; padding: 8px 14px; font: inherit; cursor: pointer; }
  .card { border: 1px solid #ccd7e8; border-radius: 10px; padding: 12px 14px; background: #fff; align-self: stretch; }
  .card h3 { margin: 0 0 4px; font-size: 16px; }
  .card a { color: #2f66dc; }
  .meta { font-size: 13px; color: #5e6f88; margin-bottom: 6px; }
  .why { font-size: 14px; margin-top: 6px; }
  .badge { display: inline-block; font-size: 12px; font-weight: 600; padding: 1px 8px; border-radius: 999px; background: #eaf5ee; color: #2e7a46; margin-right: 6px; }
  .muted { color: #5e6f88; font-size: 13px; }
  @media (max-width: 520px) { .bot, .me { max-width: 100%; } }
`;

class ProjectFinder {
  constructor(host, dataUrl) {
    this.dataUrl = dataUrl.endsWith("/") ? dataUrl : `${dataUrl}/`;
    this.root = host.attachShadow({ mode: "open" });
    this.root.innerHTML = `<style>${STYLES}</style>
      <div class="box" role="region" aria-label="Public Invention project finder">
        <div class="head">Find a Public Invention project</div>
        <div class="log" aria-live="polite"></div>
        <div class="controls"></div>
      </div>`;
    this.log = this.root.querySelector(".log");
    this.controls = this.root.querySelector(".controls");
    this.answers = { have: [], want: [], category: "" };
  }

  async start() {
    try {
      const [projects, skills, aliases] = await Promise.all(
        ["projects.json", "skills.json", "skill_aliases.json"].map((f) => fetch(this.dataUrl + f).then((r) => r.json())),
      );
      this.projects = projects;
      this.skills = skills.skills;
      this.aliases = Object.fromEntries(Object.entries(aliases).filter(([k]) => !k.startsWith("_")).map(([k, v]) => [k.toLowerCase(), v]));
      this.categories = [...new Set(projects.filter((p) => p.eligible && p.category).map((p) => p.category))].sort();
    } catch {
      this.say("Sorry, the project list didn't load. Please try again later, or email read.robert@pubinv.org.");
      return;
    }
    this.askSkills("have", "Hi! I'll match you with an open project. What skills do you already have? Pick a few or type them.", () =>
      this.askSkills("want", "Anything you'd like to learn while you help?", () => this.askCategory()));
  }

  say(text, cls = "bot") {
    const div = document.createElement("div");
    div.className = cls;
    div.textContent = text;
    this.log.append(div);
    this.log.scrollTop = this.log.scrollHeight;
    return div;
  }

  askSkills(field, question, next) {
    this.say(question);
    const picked = new Set();
    this.controls.innerHTML = `
      <div class="row"><input type="text" placeholder="e.g. Arduino, 3D printing, writing" aria-label="Type skills"><button class="ghost add">Add</button></div>
      <div class="chips"></div>
      <div class="row"><button class="main next">Next</button><button class="ghost skip">Skip</button></div>`;
    const chips = this.controls.querySelector(".chips");
    const input = this.controls.querySelector("input");
    const render = () => {
      const popular = this.popularSkills(18);
      const shown = [...new Set([...picked, ...popular])];
      chips.innerHTML = "";
      for (const skill of shown) {
        const chip = document.createElement("button");
        chip.className = "chip";
        chip.textContent = skill;
        chip.setAttribute("aria-pressed", picked.has(skill));
        chip.onclick = () => { picked.has(skill) ? picked.delete(skill) : picked.add(skill); render(); };
        chips.append(chip);
      }
    };
    const addTyped = () => {
      const found = skillsFromText(input.value, this.skills, this.aliases);
      if (input.value.trim() && !found.length) this.say(`I couldn't match "${input.value.trim()}" to a project skill. Try a broader word, like "electronics".`);
      found.forEach((s) => picked.add(s));
      input.value = "";
      render();
    };
    this.controls.querySelector(".add").onclick = addTyped;
    input.onkeydown = (e) => { if (e.key === "Enter") addTyped(); };
    const finish = (skip) => {
      if (!skip && input.value.trim()) addTyped();
      this.answers[field] = skip ? [] : [...picked];
      this.say(this.answers[field].length ? this.answers[field].join(", ") : "Skip", "me");
      next();
    };
    this.controls.querySelector(".next").onclick = () => finish(false);
    this.controls.querySelector(".skip").onclick = () => finish(true);
    render();
    input.focus();
  }

  popularSkills(limit) {
    const counts = new Map();
    for (const p of this.projects) if (p.eligible) for (const s of p.skills) counts.set(s, (counts.get(s) || 0) + 1);
    return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, limit).map(([s]) => s).sort();
  }

  askCategory() {
    this.say("Is there an area you care most about?");
    this.controls.innerHTML = `<div class="chips"></div>`;
    const chips = this.controls.querySelector(".chips");
    for (const category of ["Any area", ...this.categories]) {
      const chip = document.createElement("button");
      chip.className = "chip";
      chip.textContent = category;
      chip.onclick = () => {
        this.answers.category = category === "Any area" ? "" : category;
        this.say(category, "me");
        this.showResults();
      };
      chips.append(chip);
    }
  }

  showResults() {
    let results = recommend(this.projects, this.answers);
    let note = "";
    if (!results.length && this.answers.category) {
      results = recommend(this.projects, { ...this.answers, category: "" });
      note = ` Nothing in ${this.answers.category} matched, so here are the best fits in any area.`;
    }
    if (!results.length) {
      this.say("I couldn't find an open project that uses those skills. Here are the most active projects instead.");
      results = recommend(this.projects, {});
    } else {
      this.say(`Here ${results.length === 1 ? "is the project" : `are ${results.length} projects`} I'd suggest, most active first.${note}`);
    }
    for (const r of results) this.log.append(this.card(r));
    this.log.scrollTop = this.log.scrollHeight;

    const names = results.map((r) => r.project.project).join("; ");
    this.controls.innerHTML = `
      <div class="row"><a class="main" target="_top"></a><button class="ghost again">Start over</button></div>
      <div class="muted">The volunteer form asks which projects interest you. These names are filled in for you.</div>`;
    const link = this.controls.querySelector("a");
    link.textContent = "Volunteer for these projects";
    link.href = `${VOLUNTEER_URL}?projects=${encodeURIComponent(names)}`;
    this.controls.querySelector(".again").onclick = () => {
      this.log.innerHTML = "";
      this.answers = { have: [], want: [], category: "" };
      this.askSkills("have", "What skills do you already have?", () =>
        this.askSkills("want", "Anything you'd like to learn while you help?", () => this.askCategory()));
    };
  }

  card({ project, matchedHave, matchedWant }) {
    const div = document.createElement("div");
    div.className = "card";
    const title = document.createElement("h3");
    const a = document.createElement("a");
    a.href = project.page || project.link || "https://www.pubinv.org/projects/";
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = project.project;
    title.append(a);

    const meta = document.createElement("div");
    meta.className = "meta";
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = project.status || "Status unknown";
    meta.append(badge, [project.category, JOINABILITY[Math.round(project.joinability)], `difficulty ${project.difficulty}/10`].filter(Boolean).join(" · "));

    const summary = document.createElement("div");
    summary.textContent = project.synopsis || project.summary;

    const why = document.createElement("div");
    why.className = "why";
    const reasons = [];
    if (matchedHave.length) reasons.push(`you know ${joinNames(matchedHave)}`);
    if (matchedWant.length) reasons.push(`you'd learn ${joinNames(matchedWant)}`);
    if (project.seeking_volunteers === "yes") reasons.push("it's looking for volunteers now");
    why.textContent = reasons.length ? `Why: ${reasons.join("; ")}.` : "Why: it's one of the most active projects.";

    div.append(title, meta, summary, why);
    return div;
  }
}

function joinNames(names) {
  return names.length > 1 ? `${names.slice(0, -1).join(", ")} and ${names.at(-1)}` : names[0];
}

for (const host of document.querySelectorAll("#pubinv-project-finder, [data-pubinv-project-finder]")) {
  new ProjectFinder(host, host.dataset.src || DEFAULT_DATA).start();
}
