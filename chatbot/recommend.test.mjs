import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { recommend, skillsFromText } from "./recommend.js";

const cases = JSON.parse(readFileSync(new URL("../tests/ranking_cases.json", import.meta.url)));

for (const c of cases.cases) {
  test(c.name, () => {
    const got = recommend(cases.projects, { have: c.have, want: c.want, category: c.category });
    assert.deepEqual(got.map((r) => r.project.project), c.expected);
  });
}

test("free text maps to known skills through aliases", () => {
  const found = skillsFromText("I do arduino and javascript programming", ["Arduino", "JavaScript", "Programming"],
    { "javascript programming": ["JavaScript"] });
  assert.deepEqual(found, ["Arduino", "JavaScript", "Programming"]);
});
