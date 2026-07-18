#!/usr/bin/env node
import { spawnSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const root = path.resolve(__dirname, '..')
const requirementsPath = path.join(root, 'requirements.txt')
const dependencyDir = process.env.DOCUMENTATING_PYTHON_DEPS || path.join(os.tmpdir(), 'documentating-python-deps')

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

  const pythonEnv = {
    ...process.env,
    PYTHONPATH: [dependencyDir, process.env.PYTHONPATH].filter(Boolean).join(path.delimiter),
  }

  const dependencyProbe = spawnSync(candidate.command, [...candidate.args, '-c', 'import yaml'], {
    cwd: root,
    encoding: 'utf8',
    env: pythonEnv,
  })

  if (dependencyProbe.error || dependencyProbe.status !== 0) {
    if (!fs.existsSync(requirementsPath)) {
      failures.push(`${candidate.command}: missing requirements.txt for Python dependency bootstrap`)
      continue
    }

    fs.mkdirSync(dependencyDir, { recursive: true })
    console.error(`[documentating] Installing pinned Python build dependencies into ${dependencyDir}`)
    const install = spawnSync(
      candidate.command,
      [...candidate.args, '-m', 'pip', 'install', '--disable-pip-version-check', '--no-warn-script-location', '--target', dependencyDir, '--requirement', requirementsPath],
      {
        cwd: root,
        stdio: 'inherit',
        env: process.env,
      },
    )

    if (install.error || install.status !== 0) {
      failures.push(formatFailure(candidate.command, candidate.args, install))
      continue
    }
  }

  const result = spawnSync(candidate.command, [...candidate.args, scriptPath, ...scriptArgs], {
    cwd: root,
    stdio: 'inherit',
    env: pythonEnv,
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
