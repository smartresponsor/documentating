#!/usr/bin/env node
/**
 * Copyright (c) 2025 Oleksandr Tishchenko / Marketing America Corp
 */

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const out = { path: '.', write: true, report: 'report/layer-mirror-check.json' };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--path') out.path = argv[++i] || '.';
    else if (a === '--report') out.report = argv[++i] || out.report;
    else if (a === '--no-write') out.write = false;
    else if (a === '--write') out.write = true;
  }
  return out;
}

function listPhp(dir) {
  const out = [];
  const stack = [dir];
  while (stack.length) {
    const cur = stack.pop();
    const entries = fs.readdirSync(cur, { withFileTypes: true });
    for (const e of entries) {
      if (e.name === 'vendor' || e.name === 'node_modules' || e.name === '.git') continue;
      const p = path.join(cur, e.name);
      if (e.isDirectory()) stack.push(p);
      else if (e.isFile() && e.name.endsWith('.php')) out.push(p);
    }
  }
  return out;
}

function ensureDir(p) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const root = path.resolve(args.path);

  const pairs = [
    { impl: 'src/Service', api: 'src/ServiceInterface', suffix: 'Interface' },
    { impl: 'src/Infra', api: 'src/InfraInterface', suffix: 'Interface' },
    { impl: 'src/Http', api: 'src/HttpInterface', suffix: 'Interface' },
  ];

  const report = {
    root,
    ok: true,
    missing: [],
    note: 'Checks that Service/Infra/Http PHP classes have matching *Interface.php in mirrored Interface layer.',
  };

  for (const pair of pairs) {
    const implDir = path.join(root, pair.impl);
    const apiDir = path.join(root, pair.api);
    if (!fs.existsSync(implDir)) continue;

    const files = listPhp(implDir);
    for (const f of files) {
      const rel = path.relative(implDir, f);
      const base = path.basename(rel, '.php');

      // Skip obvious non-contract files.
      if (base.endsWith('Test')) continue;
      if (base.endsWith('Trait')) continue;
      if (base.endsWith('Exception')) continue;
      if (base.endsWith('Interface')) continue;

      const expected = path.join(apiDir, path.dirname(rel), `${base}${pair.suffix}.php`);
      if (!fs.existsSync(expected)) {
        report.ok = false;
        report.missing.push({
          impl: path.join(pair.impl, rel).replace(/\\/g, '/'),
          expected: path.relative(root, expected).replace(/\\/g, '/'),
        });
      }
    }
  }

  if (args.write) {
    const outPath = path.join(root, args.report);
    ensureDir(outPath);
    fs.writeFileSync(outPath, JSON.stringify(report, null, 2) + '\n', 'utf8');
  }

  if (!report.ok) {
    console.error('FAIL: layer mirror check failed. See ' + args.report);
    process.exit(2);
  }

  console.log('OK: layer mirror check passed.');
  process.exit(0);
}

main();
