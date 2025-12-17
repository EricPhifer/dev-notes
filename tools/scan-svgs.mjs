import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const ROOT = process.cwd();
const SKIP = new Set(["vendor", "storage", "node_modules", ".git"]);
const SUSPECT_RE = /<script|onload=|onerror=|onclick=|onmouseover=|href=|xlink:href=|javascript:|data:|base64,|<iframe|<foreignObject|http:|https:|<!DOCTYPE|<!ENTITY/i;

function walk(dir, out = []) {
  for (const name of fs.readdirSync(dir)) {
    if (SKIP.has(name)) continue;
    const full = path.join(dir, name);
    const st = fs.statSync(full);
    if (st.isDirectory()) walk(full, out);
    else if (st.isFile() && name.toLowerCase().endsWith(".svg")) out.push(full);
  }
  return out;
}

function xmllintOK(file) {
  try {
    execSync(`xmllint --noout "${file.replace(/"/g, '\\"')}"`, { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

const files = walk(ROOT);
const report = { total: files.length, xmlFail: [], suspect: [] };

for (const f of files) {
  const rel = path.relative(ROOT, f);
  const content = fs.readFileSync(f, "utf8");

  if (!xmllintOK(f)) report.xmlFail.push(rel);
  if (SUSPECT_RE.test(content)) {
    // show the first matching line for quick review
    const lines = content.split(/\r?\n/);
    const idx = lines.findIndex((l) => SUSPECT_RE.test(l));
    report.suspect.push({ file: rel, line: idx + 1, snippet: lines[idx]?.slice(0, 200) ?? "" });
  }
}

console.log(JSON.stringify(report, null, 2));
