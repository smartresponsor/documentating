#!/usr/bin/env node
import { spawnSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const root = path.resolve(__dirname, '..')

const script = process.argv[2]
const scriptArgs = process.argv.slice(3)

if (!script) {
  console.error('[documentating] Missing Python script path.')
  process.exit(1)
}

const scriptPath = path.resolve(root, script)

const candidates = process.platform === 'win32'
  ? [
      { command: 'py', args: ['-3'] },
      { command: 'python3', args: [] },
      { command: 'python', args: [] },
    ]
  : [
      { command: 'python3', args: [] },
      { command: 'python', args: [] },
    ]

const failures = []

for (const candidate of candidates) {
  const probe = spawnSync(candidate.command, [...candidate.args, '--version'], {
    cwd: root,
    encoding: 'utf8',
  })

  const probeOutput = `${probe.stdout ?? ''}${probe.stderr ?? ''}`
  const isPythonLauncherPlaceholder = probe.status === 0
    && !/Python\s+3\./i.test(probeOutput)
    && /Python/i.test(probeOutput)

  if (probe.error || probe.status !== 0 || isPythonLauncherPlaceholder) {
    failures.push(formatFailure(candidate.command, candidate.args, probe))
    continue
  }

  const result = spawnSync(candidate.command, [...candidate.args, scriptPath, ...scriptArgs], {
    cwd: root,
    stdio: 'inherit',
    env: process.env,
  })

  if (result.error) {
    failures.push(formatFailure(candidate.command, candidate.args, result))
    continue
  }

  process.exit(result.status ?? 1)
}

console.error('[documentating] Could not find a working Python 3 executable.')
for (const failure of failures) {
  console.error(`- ${failure}`)
}
process.exit(1)

function formatFailure(command, args, result) {
  const executable = [command, ...args].join(' ')
  if (result.error) {
    return `${executable}: ${result.error.message}`
  }
  const output = `${result.stdout ?? ''}${result.stderr ?? ''}`.trim()
  return output ? `${executable}: exit ${result.status}; ${output}` : `${executable}: exit ${result.status}`
}
