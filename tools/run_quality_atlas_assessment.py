#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import textwrap
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_FILE = ROOT / '.sync' / 'quality-atlas' / 'repositories' / 'ecosystem-repositories.yaml'
CARDS_FILE = ROOT / '.sync' / 'quality-atlas' / 'cards' / 'assessment-cards.yaml'
METRIC_CATALOG_FILE = ROOT / '.sync' / 'quality-atlas' / 'contract' / 'metric-catalog.yaml'
VIEW_PROFILES_FILE = ROOT / '.sync' / 'quality-atlas' / 'contract' / 'view-profiles.yaml'
SCORING_MODEL_FILE = ROOT / '.sync' / 'quality-atlas' / 'contract' / 'scoring-model.yaml'
ASSESSMENT_SCHEMA_FILE = ROOT / '.sync' / 'quality-atlas' / 'contract' / 'assessment-response-schema.yaml'
OUTBOX_DIR = ROOT / '.sync' / 'quality-atlas' / 'generated' / 'assessment-runs'
LATEST_SUMMARY_FILE = ROOT / '.sync' / 'quality-atlas' / 'generated' / 'latest-assessment-summary.json'
SNAPSHOT_ROOT = ROOT / '.sync' / 'quality-atlas' / 'components'

BASE_METRICS = ['product', 'architecture', 'runtime', 'qa', 'ops', 'market', 'overall']
PROFILE_AXIS_BUILDERS = {
    'engineering': lambda scores: {
        'product': scores['product'],
        'architecture': scores['architecture'],
        'data': round((scores['architecture'] + scores['runtime']) / 2, 2),
        'api': round((scores['architecture'] + scores['market']) / 2, 2),
        'runtime': scores['runtime'],
        'reliability': round((scores['runtime'] + scores['ops']) / 2, 2),
        'security': scores['ops'],
        'delivery': scores['ops'],
        'quality': scores['qa'],
        'overall': scores['overall'],
    },
    'owner': lambda scores: {
        'identity': scores['product'],
        'consistency': scores['architecture'],
        'delivery': scores['ops'],
        'quality': scores['qa'],
        'governance': scores['ops'],
        'fit': round((scores['market'] + scores['product']) / 2, 2),
        'debt': round(10.0 - max(0.0, (scores['architecture'] + scores['qa']) / 2 - 1.0), 2),
        'overall': scores['overall'],
    },
    'investor': lambda scores: {
        'product': scores['product'],
        'architecture': scores['architecture'],
        'delivery': scores['ops'],
        'reliability': round((scores['runtime'] + scores['qa']) / 2, 2),
        'governance': scores['ops'],
        'clarity': round((scores['product'] + scores['market']) / 2, 2),
        'overall': scores['overall'],
    },
    'operations': lambda scores: {
        'runtime': scores['runtime'],
        'reliability': round((scores['runtime'] + scores['qa']) / 2, 2),
        'observability': scores['ops'],
        'security': scores['ops'],
        'traffic': round((scores['runtime'] + scores['ops']) / 2, 2),
        'delivery': scores['ops'],
        'recovery': round((scores['qa'] + scores['ops']) / 2, 2),
        'overall': scores['overall'],
    },
}
GROUP_SCORE_MAP = {
    'product_market': lambda scores: round((scores['product'] + scores['market']) / 2, 2),
    'domain_architecture': lambda scores: scores['architecture'],
    'data_persistence': lambda scores: round((scores['architecture'] + scores['runtime']) / 2, 2),
    'api_contracts': lambda scores: round((scores['architecture'] + scores['market']) / 2, 2),
    'runtime_performance': lambda scores: scores['runtime'],
    'reliability_resilience': lambda scores: round((scores['runtime'] + scores['qa'] + scores['ops']) / 3, 2),
    'security_governance': lambda scores: scores['ops'],
    'delivery_operations': lambda scores: scores['ops'],
    'quality_testing': lambda scores: scores['qa'],
}


class AssessmentContractError(RuntimeError):
    pass


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding='utf-8')


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    return proc.returncode, (proc.stdout + '\n' + proc.stderr).strip()


def metric_catalog_summary(metric_catalog: Any) -> list[dict[str, Any]]:
    items = metric_catalog.get('metrics', metric_catalog) if isinstance(metric_catalog, dict) else metric_catalog
    if not isinstance(items, list):
        return []
    summary: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        summary.append({
            'id': item.get('id') or item.get('key') or item.get('metric_id'),
            'title': item.get('title'),
            'group': item.get('group') or item.get('capability_group'),
            'audiences': item.get('audience_tags') or item.get('audiences') or [],
            'default_relevance': item.get('default_relevance'),
        })
    return summary


def repo_facts(repo_dir: Path, component: dict[str, Any]) -> dict[str, Any]:
    facts: dict[str, Any] = {'repo_root': str(repo_dir), 'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'exists': repo_dir.exists()}
    if not repo_dir.exists():
        facts['missing_reason'] = 'Configured local_path does not exist in the current runner workspace.'
        return facts
    for command, key in [(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 'git_branch'), (['git', 'rev-parse', 'HEAD'], 'git_commit')]:
        try:
            rc, out = run(command, repo_dir)
            facts[key] = {'exit_code': rc, 'output': out[:4000]}
        except Exception as exc:  # pragma: no cover
            facts[key] = {'exit_code': 1, 'output': str(exc)}
    tracked_files = ['composer.json', 'package.json', 'phpstan.neon', 'phpstan.neon.dist', 'phpunit.xml', 'phpunit.xml.dist', '.github/workflows', '.antora-src/modules/ROOT/nav.adoc', '.antora-src/modules/ROOT/pages/index.adoc']
    for file_name in tracked_files:
        facts[f'has_{file_name.replace(".", "_").replace("/", "_")}'] = (repo_dir / file_name).exists()
    commands = [
        ('git_status', ['git', 'status', '--short']),
        ('git_recent_commits', ['git', 'log', '--oneline', '-5']),
        ('top_level_tree', ['bash', '-lc', 'find . -maxdepth 2 -mindepth 1 | sort | head -120']),
        ('php_version', ['php', '-v']),
        ('python_version', ['python3', '--version']),
        ('repo_file_count', ['bash', '-lc', 'find . -type f | wc -l']),
    ]
    for label, cmd in commands:
        rc, out = run(cmd, repo_dir)
        facts[label] = {'exit_code': rc, 'output': out[:6000]}
    report_path_value = component.get('report_path')
    if report_path_value:
        report_path = (repo_dir / report_path_value).resolve()
        if report_path.exists():
            report_text = report_path.read_text(encoding='utf-8', errors='ignore')
            facts['report_excerpt'] = textwrap.shorten(report_text.replace('\n', ' '), width=5000, placeholder=' …')
            facts['report_excerpt_source'] = report_path_value
    key_files = {}
    for rel in ['composer.json', 'package.json', '.github/workflows/gh-pages.yml', '.github/workflows/quality-atlas-assessment.yml']:
        fp = repo_dir / rel
        if fp.exists() and fp.is_file():
            key_files[rel] = fp.read_text(encoding='utf-8', errors='ignore')[:4000]
    if key_files:
        facts['key_file_excerpts'] = key_files
    return facts


def build_prompt(component: dict[str, Any], cards: dict[str, Any], metric_catalog: dict[str, Any], view_profiles: dict[str, Any], scoring_model: dict[str, Any], response_schema: dict[str, Any], facts: dict[str, Any], current_snapshot: dict[str, Any] | None) -> str:
    current_metric_context = {}
    if current_snapshot:
        for metric in BASE_METRICS:
            block = (current_snapshot.get('metrics') or {}).get(metric, {})
            current_metric_context[metric] = {
                'score': block.get('score'),
                'summary': block.get('summary'),
                'risks': block.get('risks') or [],
                'improvements': block.get('improvements') or [],
            }

    response_contract = {
        'component': component['component_id'],
        'summary': 'Short owner-facing summary.',
        'strengths': ['list of strengths'],
        'risks': ['list of risks'],
        'next_actions': ['list of concrete next actions'],
        'notes': ['optional notes'],
        'confidence': 'medium',
        'evidence_paths': ['repo-relative/path.ext'],
        'suggested_score_overrides': {'product': 8.4, 'overall': 8.2},
        'metric_updates': {
            metric: {
                'summary': f'Updated one-sentence assessment for {metric}.',
                'risks': [f'{metric} specific risk'],
                'improvements': [f'{metric} specific improvement'],
                'evidence': ['repo-relative/path.ext'],
            }
            for metric in BASE_METRICS
        },
    }
    return (
        'You are updating a Smartresponsor Quality Atlas snapshot. '
        'Use only the provided repository facts and current snapshot. '
        'Do not invent tests, tools, or repo structure that are not evidenced. '
        'Keep scores within 0.0..10.0 and only override base metrics when the facts justify it. '
        'Return complete metric_updates for all base metrics. If evidence is insufficient for a metric, preserve the previous narrative in a minimally refreshed form rather than inventing new facts.\n\n'
        f'Component registry entry:\n{json.dumps(component, ensure_ascii=False, indent=2)}\n\n'
        f'Assessment cards:\n{json.dumps(cards["cards"], ensure_ascii=False, indent=2)}\n\n'
        f'Metric catalog summary:\n{json.dumps(metric_catalog_summary(metric_catalog), ensure_ascii=False, indent=2)}\n\n'
        f'View profiles:\n{json.dumps(view_profiles, ensure_ascii=False, indent=2)}\n\n'
        f'Scoring model:\n{json.dumps(scoring_model, ensure_ascii=False, indent=2)[:12000]}\n\n'
        f'Current snapshot metric context:\n{json.dumps(current_metric_context, ensure_ascii=False, indent=2)}\n\n'
        f'Deterministic repository facts:\n{json.dumps(facts, ensure_ascii=False, indent=2)}\n\n'
        f'Response contract description:\n{json.dumps(response_schema, ensure_ascii=False, indent=2)}\n\n'
        f'Return strict JSON following this shape:\n{json.dumps(response_contract, ensure_ascii=False, indent=2)}\n'
        'Rules: risks/next_actions/strengths must be concise arrays of strings. '
        'metric_updates keys must be exactly product, architecture, runtime, qa, ops, market, overall. '
        'suggested_score_overrides may only include those keys. '
        'Every metric update must stay grounded in provided facts or current snapshot. Do not return markdown.'
    )


def build_response_json_schema() -> dict[str, Any]:
    metric_update_shape = {
        'type': 'object',
        'additionalProperties': False,
        'required': ['summary', 'risks', 'improvements', 'evidence'],
        'properties': {
            'summary': {'type': 'string', 'minLength': 1},
            'risks': {'type': 'array', 'items': {'type': 'string'}},
            'improvements': {'type': 'array', 'items': {'type': 'string'}},
            'evidence': {'type': 'array', 'items': {'type': 'string'}},
        },
    }
    return {
        'name': 'quality_atlas_assessment_verdict',
        'schema': {
            'type': 'object',
            'additionalProperties': False,
            'required': [
                'component', 'summary', 'strengths', 'risks', 'next_actions', 'notes',
                'confidence', 'evidence_paths', 'suggested_score_overrides', 'metric_updates',
            ],
            'properties': {
                'component': {'type': 'string'},
                'summary': {'type': 'string', 'minLength': 1},
                'strengths': {'type': 'array', 'items': {'type': 'string'}},
                'risks': {'type': 'array', 'items': {'type': 'string'}},
                'next_actions': {'type': 'array', 'items': {'type': 'string'}},
                'notes': {'type': 'array', 'items': {'type': 'string'}},
                'confidence': {'type': 'string', 'enum': ['high', 'medium', 'low']},
                'evidence_paths': {'type': 'array', 'items': {'type': 'string'}},
                'suggested_score_overrides': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {metric: {'type': 'number', 'minimum': 0.0, 'maximum': 10.0} for metric in BASE_METRICS},
                },
                'metric_updates': {
                    'type': 'object',
                    'additionalProperties': False,
                    'required': BASE_METRICS,
                    'properties': {metric: metric_update_shape for metric in BASE_METRICS},
                },
            },
        },
        'strict': True,
    }


def call_openai(prompt: str, model: str) -> dict[str, Any]:
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY is not set')
    payload = {
        'model': model,
        'input': [{'role': 'user', 'content': [{'type': 'input_text', 'text': prompt}]}],
        'text': {'format': {'type': 'json_schema', 'name': 'quality_atlas_assessment_verdict', 'schema': build_response_json_schema()['schema'], 'strict': True}},
    }
    req = urllib.request.Request(
        'https://api.openai.com/v1/responses',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            data = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:  # pragma: no cover
        body = exc.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f'OpenAI Responses API request failed with HTTP {exc.code}: {body[:4000]}') from exc

    for output in data.get('output', []):
        for item in output.get('content', []):
            if item.get('type') == 'refusal':
                raise RuntimeError(f"Model refusal: {item.get('refusal') or item.get('text') or 'No reason provided.'}")
            if item.get('type') == 'output_text' and item.get('text'):
                return json.loads(item['text'])

    output_text = data.get('output_text')
    if isinstance(output_text, str) and output_text.strip():
        return json.loads(output_text)
    raise RuntimeError('Responses API did not return structured output text.')


def bootstrap_snapshot(component: dict[str, Any]) -> dict[str, Any]:
    title = component['component_title']
    scores = {metric: 8.0 for metric in BASE_METRICS}
    snapshot = {
        'component': component['component_id'],
        'title': title,
        'snapshot': {
            'date': date.today().isoformat(),
            'label': 'bootstrap-seed',
            'ref': component.get('default_branch', 'master'),
            'origin': 'quality-atlas bootstrap seed',
        },
        'report_status': 'draft',
        'groups': recalc_groups(scores),
        'profile_axes': recalc_profile_axes(scores),
        'metrics': {},
        'strengths': ['Bootstrap snapshot created so the component can join the regular assessment cycle.'],
        'risks': ['Bootstrap snapshot uses neutral placeholder scores until the first live assessment refresh.'],
        'recommended_next_actions': ['Run the assessment workflow to replace bootstrap values with repository-backed verdicts.'],
        'evidence': [],
    }
    for metric, score in scores.items():
        snapshot['metrics'][metric] = {
            'relevant': True,
            'maturity': 'solid',
            'score': score,
            'summary': 'Bootstrap snapshot metric pending first live assessment.',
            'risks': ['Bootstrap metric should be replaced by an assessment verdict.'],
            'improvements': ['Run assessment workflow and refresh narrative evidence.'],
            'implemented': [],
            'partial': ['Bootstrap placeholder only.'],
            'absent': [],
            'intentionally_not_needed': [],
            'tradeoffs': ['Neutral bootstrap values unblock portfolio participation without pretending to be a real audit.'],
            'evidence': [],
        }
    if component.get('report_path'):
        snapshot['evidence'].append({'path': component['report_path'], 'note': 'Configured component report path.'})
    return snapshot


def load_current_snapshot(component_id: str) -> dict[str, Any] | None:
    current_path = SNAPSHOT_ROOT / component_id / 'current.yaml'
    if not current_path.exists():
        return None
    return load_yaml(current_path)


def safe_float(value: Any, default: float) -> float:
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return round(default, 2)


def normalize_verdict(component_id: str, verdict: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        'component': component_id,
        'summary': str(verdict.get('summary') or '').strip(),
        'strengths': [str(item).strip() for item in verdict.get('strengths') or [] if str(item).strip()],
        'risks': [str(item).strip() for item in verdict.get('risks') or [] if str(item).strip()],
        'next_actions': [str(item).strip() for item in verdict.get('next_actions') or [] if str(item).strip()],
        'notes': [str(item).strip() for item in verdict.get('notes') or [] if str(item).strip()],
        'suggested_score_overrides': {},
        'metric_updates': {},
        'confidence': str(verdict.get('confidence') or '').strip(),
        'evidence_paths': [str(item).strip() for item in verdict.get('evidence_paths') or [] if str(item).strip()],
    }
    for key, value in (verdict.get('suggested_score_overrides') or {}).items():
        if key in BASE_METRICS:
            normalized['suggested_score_overrides'][key] = safe_float(value, 0.0)
    for key, value in (verdict.get('metric_updates') or {}).items():
        if key not in BASE_METRICS or not isinstance(value, dict):
            continue
        normalized['metric_updates'][key] = {
            'summary': str(value.get('summary') or '').strip(),
            'risks': [str(item).strip() for item in value.get('risks') or [] if str(item).strip()],
            'improvements': [str(item).strip() for item in value.get('improvements') or [] if str(item).strip()],
            'evidence': [str(item).strip() for item in value.get('evidence') or [] if str(item).strip()],
        }
    return normalized


def validate_verdict(component_id: str, verdict: dict[str, Any]) -> None:
    if verdict.get('component') != component_id:
        raise AssessmentContractError(f"Verdict component mismatch: expected '{component_id}', received '{verdict.get('component')}'.")
    if not verdict.get('summary'):
        raise AssessmentContractError('Verdict summary is empty.')
    if verdict.get('confidence') not in {'high', 'medium', 'low', 'dry-run'}:
        raise AssessmentContractError(f"Verdict confidence is invalid: {verdict.get('confidence')!r}.")
    for metric, value in verdict.get('suggested_score_overrides', {}).items():
        if metric not in BASE_METRICS:
            raise AssessmentContractError(f'Unexpected score override key: {metric}.')
        if not 0.0 <= float(value) <= 10.0:
            raise AssessmentContractError(f'Score override for {metric} is outside 0..10: {value}.')
    metric_updates = verdict.get('metric_updates') or {}
    missing_metrics = [metric for metric in BASE_METRICS if metric not in metric_updates]
    if missing_metrics:
        raise AssessmentContractError(f'Metric updates are missing required keys: {", ".join(missing_metrics)}.')
    for metric in BASE_METRICS:
        block = metric_updates[metric]
        if not block.get('summary'):
            raise AssessmentContractError(f'Metric update for {metric} is missing summary.')


def recalc_groups(scores: dict[str, float]) -> dict[str, dict[str, Any]]:
    return {group: {'score': builder(scores)} for group, builder in GROUP_SCORE_MAP.items()}


def recalc_profile_axes(scores: dict[str, float]) -> dict[str, dict[str, float]]:
    return {profile_id: builder(scores) for profile_id, builder in PROFILE_AXIS_BUILDERS.items()}


def merge_snapshot(current: dict[str, Any] | None, component: dict[str, Any], verdict: dict[str, Any], run_label: str, origin: str) -> dict[str, Any]:
    if current is None:
        raise RuntimeError(f"Current snapshot for {component['component_id']} is missing. Seed snapshots before running the assessment.")
    snapshot = json.loads(json.dumps(current))
    scores = {metric: safe_float(snapshot['metrics'][metric]['score'], 0.0) for metric in BASE_METRICS}
    for key, value in verdict['suggested_score_overrides'].items():
        scores[key] = max(0.0, min(10.0, safe_float(value, scores[key])))
    snapshot['snapshot'] = {
        'date': date.today().isoformat(),
        'label': run_label,
        'ref': component.get('default_branch', 'master'),
        'origin': origin,
    }
    snapshot['report_status'] = 'current'
    snapshot['groups'] = recalc_groups(scores)
    snapshot['profile_axes'] = recalc_profile_axes(scores)
    snapshot['strengths'] = verdict['strengths'] or snapshot.get('strengths', [])
    snapshot['risks'] = verdict['risks'] or snapshot.get('risks', [])
    snapshot['recommended_next_actions'] = verdict['next_actions'] or snapshot.get('recommended_next_actions', [])
    existing_evidence = list(snapshot.get('evidence', []))
    evidence_paths = {item.get('path') for item in existing_evidence if isinstance(item, dict)}
    if component.get('report_path') and component['report_path'] not in evidence_paths:
        existing_evidence.append({'path': component['report_path'], 'note': 'Component report path from repository registry.'})
        evidence_paths.add(component['report_path'])
    for path in verdict.get('evidence_paths', []):
        if path not in evidence_paths:
            existing_evidence.append({'path': path, 'note': 'Assessment evidence path.'})
            evidence_paths.add(path)
    snapshot['evidence'] = existing_evidence
    note_lines = verdict['notes'][:]
    if verdict['summary']:
        note_lines.insert(0, verdict['summary'])
    if note_lines:
        snapshot['assessment_notes'] = note_lines
    if verdict.get('confidence'):
        snapshot['assessment_confidence'] = verdict['confidence']
    for metric, score in scores.items():
        block = snapshot['metrics'][metric]
        block['score'] = score
        update = verdict['metric_updates'].get(metric, {})
        if update.get('summary'):
            block['summary'] = update['summary']
        if update.get('risks'):
            block['risks'] = update['risks']
        if update.get('improvements'):
            block['improvements'] = update['improvements']
        if update.get('evidence'):
            block['evidence'] = [{'path': item, 'note': 'Metric-level assessment evidence.'} for item in update['evidence']]
    return snapshot


def dry_run_verdict(component: dict[str, Any], prompt: str, facts: dict[str, Any], current: dict[str, Any] | None) -> dict[str, Any]:
    title = component['component_title']
    repo_exists = facts.get('exists') is True
    base_overall = safe_float((current or {}).get('metrics', {}).get('overall', {}).get('score'), 8.0)
    return {
        'component': component['component_id'],
        'summary': f'{title} remains on a seeded snapshot because the assessment runner is in dry-run mode.',
        'strengths': [
            'Canonical snapshot/history contracts are present.',
            'This component is wired into the atlas assessment registry.' if repo_exists else 'Registry entry exists but local repository path is not yet available to the runner.',
        ],
        'risks': [
            'Dry-run mode does not perform a live AI verdict.',
            'Repository scan depth is limited to deterministic probes until OPENAI_API_KEY is provided.',
        ],
        'next_actions': [
            'Enable responses mode with OPENAI_API_KEY for live verdict generation.',
            'Expand repository registry coverage and local_path mappings for additional components.',
        ],
        'notes': [
            f'Prompt length: {len(prompt)} characters.',
            f'Base overall score retained at {base_overall:.2f}.',
        ],
        'confidence': 'dry-run',
        'evidence_paths': [path for path in [component.get('report_path')] if path],
        'suggested_score_overrides': {'overall': base_overall},
        'metric_updates': {
            metric: {
                'summary': ((current or {}).get('metrics', {}).get(metric, {}).get('summary') or f'Dry-run retained current narrative for {metric}.'),
                'risks': ((current or {}).get('metrics', {}).get(metric, {}).get('risks') or ['Dry-run mode did not refresh this metric with live AI evidence.']),
                'improvements': ((current or {}).get('metrics', {}).get(metric, {}).get('improvements') or ['Enable responses mode to refresh this metric from repository evidence.']),
                'evidence': [path for path in [component.get('report_path')] if path],
            }
            for metric in BASE_METRICS
        },
    }


def write_snapshot_files(component_id: str, snapshot: dict[str, Any]) -> tuple[Path, Path]:
    component_dir = SNAPSHOT_ROOT / component_id
    label = snapshot['snapshot']['label']
    snap_date = snapshot['snapshot']['date']
    history_path = component_dir / 'history' / f'{snap_date}-{label}.yaml'
    current_path = component_dir / 'current.yaml'
    write_yaml(history_path, snapshot)
    write_yaml(current_path, snapshot)
    return current_path, history_path


def update_latest_summary(run_dir: Path, mode: str, components: list[dict[str, Any]], failures: list[dict[str, Any]]) -> None:
    payload = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'run_dir': str(run_dir),
        'mode': mode,
        'components': components,
        'failures': failures,
        'status': 'failed' if failures else 'ok',
    }
    LATEST_SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    LATEST_SUMMARY_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--registry', default=str(REGISTRY_FILE))
    parser.add_argument('--cards', default=str(CARDS_FILE))
    parser.add_argument('--model', default=os.environ.get('QUALITY_ATLAS_OPENAI_MODEL', 'gpt-5'))
    parser.add_argument('--mode', choices=['dry-run', 'responses'], default='dry-run')
    parser.add_argument('--repo-root', default=str(ROOT))
    parser.add_argument('--label', default=f"assessment-{date.today().isoformat()}")
    args = parser.parse_args()

    registry = load_yaml(Path(args.registry))
    cards = load_yaml(Path(args.cards))
    metric_catalog = load_yaml(METRIC_CATALOG_FILE)
    view_profiles = load_yaml(VIEW_PROFILES_FILE)
    scoring_model = load_yaml(SCORING_MODEL_FILE)
    response_schema = load_yaml(ASSESSMENT_SCHEMA_FILE)
    repo_root = Path(args.repo_root).resolve()
    run_dir = OUTBOX_DIR / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run_dir.mkdir(parents=True, exist_ok=True)

    assessments: list[dict[str, Any]] = []
    latest_components: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for component in registry['repositories']:
        if not component.get('enabled'):
            continue
        local_path = component.get('local_path') or '.'
        target_repo = (repo_root / local_path).resolve()
        facts = repo_facts(target_repo, component)
        current = load_current_snapshot(component['component_id'])
        if current is None:
            current = bootstrap_snapshot(component)
        prompt = build_prompt(component, cards, metric_catalog, view_profiles, scoring_model, response_schema, facts, current)

        try:
            if args.mode == 'responses':
                verdict = call_openai(prompt, args.model)
            else:
                verdict = dry_run_verdict(component, prompt, facts, current)
            normalized = normalize_verdict(component['component_id'], verdict)
            validate_verdict(component['component_id'], normalized)
            snapshot = merge_snapshot(current, component, normalized, args.label, f'quality-atlas {args.mode} assessment')
            current_path, history_path = write_snapshot_files(component['component_id'], snapshot)
            item = {
                'status': 'ok',
                'registry_entry': component,
                'facts': facts,
                'verdict': normalized,
                'snapshot_paths': {'current': str(current_path), 'history': str(history_path)},
            }
            assessments.append(item)
            latest_components.append({
                'component': component['component_id'],
                'title': component['component_title'],
                'overall': snapshot['metrics']['overall']['score'],
                'history_file': str(history_path),
                'summary': normalized['summary'],
            })
            (run_dir / f"{component['component_id']}.json").write_text(json.dumps(item, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception as exc:
            failure = {
                'status': 'error',
                'component': component['component_id'],
                'title': component['component_title'],
                'mode': args.mode,
                'error_type': exc.__class__.__name__,
                'error': str(exc),
                'registry_entry': component,
                'facts': facts,
            }
            failures.append(failure)
            (run_dir / f"{component['component_id']}.error.json").write_text(json.dumps(failure, indent=2, ensure_ascii=False), encoding='utf-8')

    summary = {
        'date': date.today().isoformat(),
        'mode': args.mode,
        'count': len(assessments),
        'failures': len(failures),
        'label': args.label,
        'status': 'failed' if failures else 'ok',
    }
    (run_dir / 'index.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    update_latest_summary(run_dir, args.mode, latest_components, failures)
    print(json.dumps({'run_dir': str(run_dir), 'count': len(assessments), 'failures': len(failures), 'mode': args.mode, 'label': args.label}, indent=2))
    if args.mode == 'responses' and failures:
        raise SystemExit(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise
