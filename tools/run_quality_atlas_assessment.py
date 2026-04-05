#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_FILE = ROOT / '.sync' / 'quality-atlas' / 'repositories' / 'ecosystem-repositories.yaml'
CARDS_FILE = ROOT / '.sync' / 'quality-atlas' / 'cards' / 'assessment-cards.yaml'
OUTBOX_DIR = ROOT / '.sync' / 'quality-atlas' / 'generated' / 'assessment-runs'


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    return proc.returncode, (proc.stdout + '\n' + proc.stderr).strip()


def repo_facts(repo_dir: Path) -> dict[str, object]:
    facts = {'repo_root': str(repo_dir), 'timestamp_utc': datetime.now(timezone.utc).isoformat()}
    for command, key in [(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 'git_branch'), (['git', 'rev-parse', 'HEAD'], 'git_commit')]:
        try:
            rc, out = run(command, repo_dir)
            if rc == 0:
                facts[key] = out.splitlines()[-1].strip()
        except Exception:
            pass
    for file_name in ['composer.json', 'package.json', 'phpstan.neon', 'phpunit.xml', 'phpunit.xml.dist']:
        facts[f'has_{file_name.replace(".", "_")}'] = (repo_dir / file_name).exists()
    for label, cmd in [('git_status', ['git', 'status', '--short']), ('php_version', ['php', '-v'])]:
        rc, out = run(cmd, repo_dir)
        facts[label] = {'exit_code': rc, 'output': out[:4000]}
    return facts


def build_prompt(component: dict[str, object], cards: dict[str, object], facts: dict[str, object]) -> str:
    enabled_cards = cards['cards']
    return f"""You are updating a Smartresponsor Quality Atlas snapshot.\n\nComponent registry entry:\n{json.dumps(component, ensure_ascii=False, indent=2)}\n\nAssessment cards:\n{json.dumps(enabled_cards, ensure_ascii=False, indent=2)}\n\nDeterministic repository facts:\n{json.dumps(facts, ensure_ascii=False, indent=2)}\n\nReturn strict JSON with keys: component, summary, risks, next_actions, notes, suggested_score_overrides. suggested_score_overrides may be empty but must be an object. Do not return markdown."""


def call_openai(prompt: str, model: str) -> dict[str, object]:
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY is not set')
    payload = {
        'model': model,
        'input': [{'role': 'user', 'content': [{'type': 'input_text', 'text': prompt}]}],
        'text': {'format': {'type': 'json_object'}},
    }
    req = urllib.request.Request(
        'https://api.openai.com/v1/responses',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        data = json.loads(response.read().decode('utf-8'))
    text = ''.join(
        item.get('text', '')
        for output in data.get('output', [])
        for item in output.get('content', [])
        if item.get('type') == 'output_text'
    )
    return json.loads(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--registry', default=str(REGISTRY_FILE))
    parser.add_argument('--cards', default=str(CARDS_FILE))
    parser.add_argument('--model', default=os.environ.get('QUALITY_ATLAS_OPENAI_MODEL', 'gpt-5'))
    parser.add_argument('--mode', choices=['dry-run', 'responses'], default='dry-run')
    parser.add_argument('--repo-root', default=str(ROOT))
    args = parser.parse_args()

    registry = load_yaml(Path(args.registry))
    cards = load_yaml(Path(args.cards))
    repo_root = Path(args.repo_root).resolve()
    run_dir = OUTBOX_DIR / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run_dir.mkdir(parents=True, exist_ok=True)

    assessments = []
    for component in registry['repositories']:
        if not component.get('enabled'):
            continue
        local_path = component.get('local_path') or '.'
        target_repo = (repo_root / local_path).resolve()
        facts = repo_facts(target_repo)
        prompt = build_prompt(component, cards, facts)
        if args.mode == 'responses':
            verdict = call_openai(prompt, args.model)
        else:
            verdict = {
                'component': component['component_id'],
                'summary': 'Dry-run placeholder. Connect OPENAI_API_KEY and enable repositories to receive live assessments.',
                'risks': ['Dry-run mode does not score the repository.'],
                'next_actions': ['Enable repository entries and rerun in responses mode.'],
                'notes': [f"Prompt length: {len(prompt)} characters."],
                'suggested_score_overrides': {},
            }
        item = {'registry_entry': component, 'facts': facts, 'verdict': verdict}
        assessments.append(item)
        slug = component['component_id']
        (run_dir / f'{slug}.json').write_text(json.dumps(item, indent=2, ensure_ascii=False), encoding='utf-8')

    (run_dir / 'index.json').write_text(json.dumps({'date': date.today().isoformat(), 'mode': args.mode, 'count': len(assessments)}, indent=2), encoding='utf-8')
    print(json.dumps({'run_dir': str(run_dir), 'count': len(assessments), 'mode': args.mode}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise
