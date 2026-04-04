#!/usr/bin/env node
import { spawnSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const root = path.resolve(__dirname, '..')
const antoraBin = path.join(root, 'node_modules', '@antora', 'cli', 'bin', 'antora.js')

if (!fs.existsSync(antoraBin)) {
  console.error('[documentating] Local Antora CLI is not installed.')
  console.error('[documentating] Run `npm install` in the repository root first, then re-run the build command.')
  process.exit(1)
}

const result = spawnSync(process.execPath, [antoraBin, 'antora-playbook.yml', '--fetch'], {
  cwd: root,
  stdio: 'inherit',
  env: process.env,
})

if (result.error) {
  console.error(`[documentating] Failed to start Antora CLI: ${result.error.message}`)
  process.exit(1)
}

process.exit(result.status ?? 1)
