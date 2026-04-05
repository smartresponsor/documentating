#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

from quality_atlas_probe_lib import seed_probe_snapshot, summarize_probe_snapshot, write_probe_files, write_yaml

ROOT = Path(__file__).resolve().parents[1]
DATASET_FILE = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'pages' / 'quality-atlas' / 'dataset.json'
SNAPSHOT_ROOT = ROOT / '.sync' / 'quality-atlas' / 'components'
DEFAULT_LABEL = 'pre-rc-seed'
TODAY = date.today().isoformat()

SUMMARY_BY_AXIS = {
    'product': 'Component identity and market-facing shape are materially present.',
    'architecture': 'Symfony-oriented architecture shape is materially present.',
    'runtime': 'Runtime and application surface are materially present.',
    'qa': 'Testing and QA posture are materially present but remain pre-RC.',
    'ops': 'Operational, governance, and security posture are materially present but remain pre-RC.',
    'market': 'Business-facing and portfolio-facing alignment is materially present.',
    'overall': 'Overall release-candidate direction is visible, but the component remains in pre-RC life.',
}

AXIS_TO_GROUPS = {
    'product': ['product_market'],
    'architecture': ['domain_architecture'],
    'runtime': ['runtime_performance'],
    'qa': ['quality_testing'],
    'ops': ['delivery_operations', 'security_governance'],
    'market': ['product_market'],
    'overall': ['product_market', 'domain_architecture', 'runtime_performance', 'quality_testing', 'delivery_operations', 'security_governance'],
}


def slugify(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def maturity_for(score: float) -> str:
    if score < 2.5:
        return 'missing'
    if score < 5.0:
        return 'weak'
    if score < 7.5:
        return 'partial'
    if score < 8.75:
        return 'solid'
    return 'strong'


def load_dataset() -> list[dict[str, object]]:
    return json.loads(DATASET_FILE.read_text(encoding='utf-8'))


def metric_block(axis: str, score: float) -> dict[str, object]:
    summary = SUMMARY_BY_AXIS[axis]
    return {
        'relevant': True,
        'maturity': maturity_for(score),
        'score': round(score, 2),
        'summary': summary,
        'risks': ['Assessment seeded from current pre-RC atlas and should be enriched by regular repository scans.'],
        'improvements': ['Refresh this metric from a scheduled repository assessment run.'],
        'implemented': ['Current component report contributes to the Quality Atlas dataset.'],
        'partial': ['Narrative evidence and automated probe evidence should be expanded over time.'],
        'absent': [],
        'intentionally_not_needed': [],
        'tradeoffs': ['Current snapshot is lightweight and optimized for portfolio generation rather than exhaustive per-metric evidence.'],
        'evidence': [{'path': '.antora-src/modules/ROOT/pages/quality-atlas/dataset.json', 'note': 'Current atlas dataset seed.'}],
    }


def build_snapshot(item: dict[str, object], snapshot_date: str, label: str) -> tuple[dict[str, object], dict[str, object]]:
    title = str(item['component'])
    slug = slugify(title)
    scores = {k: float(item[k]) for k in ['product', 'architecture', 'runtime', 'qa', 'ops', 'market', 'overall']}
    profile_axes = {
        'engineering': {
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
        'owner': {
            'identity': scores['product'],
            'consistency': scores['architecture'],
            'delivery': scores['ops'],
            'quality': scores['qa'],
            'governance': scores['ops'],
            'fit': round((scores['market'] + scores['product']) / 2, 2),
            'debt': round(10.0 - max(0.0, (scores['architecture'] + scores['qa']) / 2 - 1.0), 2),
            'overall': scores['overall'],
        },
        'investor': {
            'product': scores['product'],
            'architecture': scores['architecture'],
            'delivery': scores['ops'],
            'reliability': round((scores['runtime'] + scores['qa']) / 2, 2),
            'governance': scores['ops'],
            'clarity': round((scores['product'] + scores['market']) / 2, 2),
            'overall': scores['overall'],
        },
        'operations': {
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
    component = {
        'component_id': slug,
        'component_title': title,
        'default_branch': 'master',
        'github_repository': '',
        'report_path': f'.antora-src/modules/ROOT/pages/component/{slug}/report/index.adoc',
    }
    probe_snapshot = seed_probe_snapshot(component, snapshot_date, label)
    development_driving = summarize_probe_snapshot(probe_snapshot)
    snapshot = {
        'component': slug,
        'title': title,
        'snapshot': {
            'date': snapshot_date,
            'label': label,
            'ref': 'master',
            'origin': 'quality-atlas seed',
        },
        'report_status': 'draft',
        'groups': {group: {'score': round(scores[axis], 2), 'source_axis': axis} for axis, groups in AXIS_TO_GROUPS.items() for group in groups},
        'profile_axes': profile_axes,
        'metrics': {axis: metric_block(axis, score) for axis, score in scores.items()},
        'development_driving': development_driving,
        'strengths': [
            f"Highest current axis: {max(scores, key=scores.get)} {max(scores.values()):.1f}/10",
            'Component is already represented in the current pre-RC Atlas.',
        ],
        'risks': [
            'Snapshot was seeded from the current atlas and does not yet contain repository-scan deltas.',
            'Structured metrics should be refreshed by the scheduled assessment workflow.',
        ],
        'recommended_next_actions': [
            'Run scheduled repository assessment and enrich narrative evidence.',
            'Regenerate component report blocks from the current snapshot contract.',
        ],
        'evidence': [
            {'path': f'.antora-src/modules/ROOT/pages/component/{slug}/report/index.adoc', 'note': 'Current component report page if present.'},
            {'path': '.antora-src/modules/ROOT/pages/quality-atlas/dataset.json', 'note': 'Seeded atlas dataset source.'},
            {'path': f'.sync/quality-atlas/components/{slug}/probes/current.yaml', 'note': 'Deterministic development-driving probe layer.'},
        ],
    }
    return snapshot, probe_snapshot


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=TODAY)
    parser.add_argument('--label', default=DEFAULT_LABEL)
    args = parser.parse_args()

    for item in load_dataset():
        snapshot, probe_snapshot = build_snapshot(item, args.date, args.label)
        component_dir = SNAPSHOT_ROOT / snapshot['component']
        history_path = component_dir / 'history' / f"{args.date}-{args.label}.yaml"
        current_path = component_dir / 'current.yaml'
        if not history_path.exists():
            write_yaml(history_path, snapshot)
        write_yaml(current_path, snapshot)
        write_probe_files(snapshot['component'], probe_snapshot)


if __name__ == '__main__':
    main()
