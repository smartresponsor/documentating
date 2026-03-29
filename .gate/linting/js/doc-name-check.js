#!/usr/bin/env node
/**
 * Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
 *
 * Doc file naming contract checker: {domain}-{subdomain}-{kind}-{name}.{ext}
 *
 * Usage:
 *   node owner/lint/doc-name-check.js --root . --domain canon
 * Options:
 *   --root <path>     repo root (default: .)
 *   --domain <name>   expected domain segment (default: canon)
 *   --dir <path>      doc directory relative to root (auto: doc or docs)
 */
'use strict';

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);

function getArg(name, def) {
  const i = args.indexOf(name);
  if (i === -1) return def;
  const v = args[i + 1];
  return v ?? def;
}
function hasFlag(name) {
  return args.includes(name);
}

const rootDir = path.resolve(getArg('--root', '.'));
const expectedDomain = String(getArg('--domain', 'canon')).trim();
let docDirRel = getArg('--dir', '').trim();

function detectDocDir() {
  const a = path.join(rootDir, 'doc');
  if (fs.existsSync(a) && fs.statSync(a).isDirectory()) return 'doc';
  const b = path.join(rootDir, 'docs');
  if (fs.existsSync(b) && fs.statSync(b).isDirectory()) return 'docs';
  return '';
}

if (!docDirRel) docDirRel = detectDocDir();
if (!docDirRel) {
  console.log('doc-name-check: no doc/ or docs/ directory found; skip');
  process.exit(0);
}

const docDirAbs = path.join(rootDir, docDirRel);

const ignoreDir = new Set(['.git', 'node_modules', 'vendor', 'var', '.idea', '.vscode', 'cache', 'build', 'dist', 'fixture']);

function walk(dirAbs, relBase, out) {
  const items = fs.readdirSync(dirAbs, { withFileTypes: true });
  for (const it of items) {
    if (it.name.startsWith('.')) continue;
    const abs = path.join(dirAbs, it.name);
    const rel = path.posix.join(relBase, it.name);
    if (it.isDirectory()) {
      if (ignoreDir.has(it.name)) continue;
      walk(abs, rel, out);
      continue;
    }
    if (!it.isFile()) continue;
    out.push(rel);
  }
}

function isLowerAlphaNumUnderscore(seg) {
  return /^[a-z0-9][a-z0-9_]*$/.test(seg);
}

function hasBadChars(s) {
  return /[\s()]/.test(s) || s.includes('--');
}

function validateFileName(fileRel) {
  const base = path.posix.basename(fileRel);
  if (base.startsWith('.')) return null;

  if (hasBadChars(base)) {
    return 'contains spaces/parentheses or double hyphen';
  }

  const ext = path.posix.extname(base);
  if (!ext || ext.length < 2) {
    return 'missing extension';
  }
  const extName = ext.slice(1);
  if (!/^[a-z0-9]+$/.test(extName)) {
    return 'extension must be lowercase alnum';
  }

  const stem = base.slice(0, -ext.length);
  if (stem.length === 0) return 'empty stem';

  if (/[A-Z]/.test(stem)) {
    return 'stem must be lowercase (A-Z detected)';
  }

  const parts = stem.split('-').filter(Boolean);
  if (parts.length < 4) {
    return 'expected at least 4 hyphen-separated segments';
  }

  const domain = parts[0];
  const subdomain = parts[1];
  const kind = parts[2];
  const nameParts = parts.slice(3);

  if (expectedDomain && domain !== expectedDomain) {
    return `domain must be '${expectedDomain}'`;
  }
  if (!isLowerAlphaNumUnderscore(domain)) return 'invalid domain segment';
  if (!isLowerAlphaNumUnderscore(subdomain)) return 'invalid subdomain segment';
  if (!isLowerAlphaNumUnderscore(kind)) return 'invalid kind segment';

  for (const p of nameParts) {
    if (!isLowerAlphaNumUnderscore(p)) return 'invalid name segment';
  }
  return null;
}

const files = [];
walk(docDirAbs, docDirRel.replace(/\\/g, '/'), files);

const violations = [];
for (const rel of files) {
  const reason = validateFileName(rel);
  if (reason) violations.push({ file: rel, reason });
}

if (violations.length > 0) {
  console.log(`Doc name contract violations: ${violations.length}`);
  for (const v of violations) {
    console.log(`- ${v.file}: ${v.reason}`);
  }
  process.exit(2);
}

console.log('doc-name-check: OK');
process.exit(0);
