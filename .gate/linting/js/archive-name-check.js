#!/usr/bin/env node
/**
 * Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
 *
 * Archive name linter (owner + industrial canon).
 *
 * Rules (practical):
 * - no spaces
 * - no double hyphen "--"
 * - allow underscores for versions (01_0, v1_2, suite_33)
 * - allow numeric prefix form: 001_ui-...zip (also 001_<tag>-...zip)
 * - otherwise: starts with a known domain (case-insensitive), then "-" + message
 *
 * Usage:
 *   node archive-name-lint.js <file1.zip> <file2.zip> ...
 */
const fs = require('fs');
const path = require('path');

const here = __dirname;
const cfgPath = path.join(here, 'archive-domains.json');
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));

const domains = new Set((cfg.domains || []).map(d => String(d).toLowerCase()));
const aliases = cfg.aliases || {};

function isOkChar(name) {
  return /^[A-Za-z0-9._-]+$/.test(name);
}

function normalizeDomain(d) {
  const low = String(d).toLowerCase();
  if (domains.has(low)) return low;
  if (aliases[low] && domains.has(String(aliases[low]).toLowerCase())) return String(aliases[low]).toLowerCase();
  return null;
}

function lintOne(filePath) {
  const base = path.basename(filePath);
  if (!base.toLowerCase().endsWith('.zip')) return `extension must be .zip`;
  if (base.includes(' ')) return `contains spaces`;
  if (!isOkChar(base)) return `contains invalid characters`;
  if (base.includes('--')) return `contains double hyphen "--"`;

  // numeric prefix form (commit stream)
  if (/^\d{3}_[A-Za-z0-9]+-[A-Za-z0-9].*\.zip$/.test(base)) return null;

  const parts = base.replace(/\.zip$/i, '').split('-');
  if (parts.length < 2) return `must have at least "domain-message"`;
  const domRaw = parts[0];
  const dom = normalizeDomain(domRaw);
  if (!dom) return `unknown domain "${domRaw}"`;
  return null;
}

let bad = 0;
for (const p of process.argv.slice(2)) {
  const err = lintOne(p);
  if (err) {
    bad++;
    console.error(`✗ ${path.basename(p)}: ${err}`);
  } else {
    console.log(`✓ ${path.basename(p)}`);
  }
}

if (process.argv.length <= 2) {
  console.error('usage: node archive-name-lint.js <file1.zip> <file2.zip> ...');
  process.exit(2);
}
process.exit(bad ? 2 : 0);
