#!/usr/bin/env node
/**
 * Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
 *
 * Suggest a sanitized archive name (best-effort).
 * Prints the recommended filename to stdout.
 *
 * Usage:
 *   node archive-namer.js "My File (1).zip"
 */
const path = require('path');

function sanitize(name) {
  let base = path.basename(name);
  base = base.replace(/\s+/g, '-');
  base = base.replace(/[()\[\]]+/g, '');
  base = base.replace(/--+/g, '-');
  base = base.replace(/^-+|-+$/g, '');
  return base;
}

const arg = process.argv[2];
if (!arg) {
  console.error('usage: node archive-namer.js "<file.zip>"');
  process.exit(2);
}
process.stdout.write(sanitize(arg));
