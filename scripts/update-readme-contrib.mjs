import fs from "node:fs/promises";

const README_PATH = new URL("../README.md", import.meta.url);

function requireEnv(name) {
  const v = process.env[name];
  if (!v) throw new Error(`Missing env var: ${name}`);
  return v;
}

const count = Number(requireEnv("LAST_YEAR_CONTRIB"));
if (!Number.isFinite(count) || count < 0) {
  throw new Error(`Invalid LAST_YEAR_CONTRIB value: ${process.env.LAST_YEAR_CONTRIB}`);
}

const start = "<!-- LAST_YEAR_CONTRIB:START -->";
const end = "<!-- LAST_YEAR_CONTRIB:END -->";

const readme = await fs.readFile(README_PATH, "utf8");
const pattern = new RegExp(`${start}[\\s\\S]*?${end}`, "m");

if (!pattern.test(readme)) {
  throw new Error("Contribution placeholder not found in README.md");
}

const updated = readme.replace(pattern, `${start}${count}${end}`);
await fs.writeFile(README_PATH, updated, "utf8");
