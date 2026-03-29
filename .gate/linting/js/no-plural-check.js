#!/usr/bin/env node
/**
 * Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
 *
 * No-plural linter for class and method names (heuristic).
 * Usage:
 *   node owner/lint/no-plural-check.js --path src
 */
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
function getArg(name, def) {
  const i = args.indexOf(name);
  if (i === -1) return def;
  const v = args[i + 1];
  return v ?? def;
}
const root = path.resolve(getArg('--path', '.'));
const ignoreDir = new Set(['.git', 'node_modules', 'vendor', 'var', '.idea', '.vscode', 'cache', 'build', 'dist', 'fixture']);
const allowExact = new Set([
  'Analytics', 'Ops', 'News', 'Status', 'Bus', 'Address'
]);

function isPluralish(name) {
  if (!name) return false;
  if (allowExact.has(name)) return false;
  const n = name.trim();
  if (n.length < 4) return false;
  const low = n.toLowerCase();
  if (low.endsWith('ss')) return false;          // Address, Class
  if (low.endsWith('us')) return false;          // Status
  if (low.endsWith('is')) return false;          // Analysis
  if (low.endsWith('ops')) return false;         // Ops
  if (!low.endsWith('s')) return false;
  return true;
}

function walk(dir, out) {
  const list = fs.readdirSync(dir, { withFileTypes: true });
  for (const ent of list) {
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) {
      if (ignoreDir.has(ent.name)) continue;
      walk(p, out);
      continue;
    }
    out.push(p);
  }
}

function scanPhp(file) {
  const txt = fs.readFileSync(file, 'utf8');
  const issues = [];

  const classRe = /\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\b/g;
  let m;
  while ((m = classRe.exec(txt)) !== null) {
    const name = m[1];
    if (isPluralish(name)) issues.push({ kind: 'class', name });
  }

  const fnRe = /\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
  while ((m = fnRe.exec(txt)) !== null) {
    const name = m[1];
    if (name.startsWith('__')) continue; // magic
    if (isPluralish(name)) issues.push({ kind: 'method', name });
  }
  return issues;
}

const files = [];
walk(root, files);

let bad = 0;
for (const f of files) {
  if (!f.endsWith('.php')) continue;
  let issues;
  try {
    issues = scanPhp(f);
  } catch (e) {
    continue;
  }
  if (issues.length === 0) continue;
  bad += issues.length;
  const rel = path.relative(process.cwd(), f);
  for (const it of issues) {
    console.log(`${rel}: ${it.kind} name looks plural: ${it.name}`);
  }
}

if (bad > 0) {
  console.error(`FAIL: ${bad} potential plural name(s) found.`);
  process.exit(2);
}
console.log('OK: no plural-looking class/method names found.');
