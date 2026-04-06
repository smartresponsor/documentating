#!/usr/bin/env python3
from __future__ import annotations

import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROBE_FAMILIES_FILE = ROOT / '.sync' / 'quality-atlas' / 'contract' / 'probe-families.yaml'
EXCLUDED_DIRS = {
    '.git', 'vendor', 'node_modules', '.idea', '.commanding', '.watchdog', '.sandbox',
    '.antora-src', '.sync/quality-atlas/generated', 'var', 'cache', 'build', 'dist',
}
TEXT_SUFFIXES = {'.php', '.md', '.adoc', '.yml', '.yaml', '.json', '.txt', '.xml', '.neon'}
PHP_SUFFIX = '.php'
BASE_FAMILY_IDS = [
    'canon_structure',
    'architecture_boundaries',
    'runtime_surface',
    'qa_behavior',
    'documentation_suite',
    'delivery_observability',
    'solid_refactoring',
]


def load_probe_families() -> list[dict[str, Any]]:
    data = yaml.safe_load(PROBE_FAMILIES_FILE.read_text(encoding='utf-8'))
    return data.get('families', [])


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding='utf-8')


def normalize_text_name(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', value.lower())


def component_tokens(component: dict[str, Any]) -> set[str]:
    values = [str(component.get('component_id') or ''), str(component.get('component_title') or '')]
    tokens: set[str] = set()
    for value in values:
        norm = normalize_text_name(value)
        if not norm:
            continue
        tokens.add(norm)
        if norm.endswith('ing') and len(norm) > 5:
            tokens.add(norm[:-3])
        if len(norm) > 6:
            tokens.add(norm[:-4])
        if len(norm) > 7:
            tokens.add(norm[:-5])
    return {token for token in tokens if token}


def should_skip_path(path: Path) -> bool:
    lowered = path.as_posix().lower()
    if '/.git/' in lowered or lowered.endswith('/.git'):
        return True
    for part in path.parts:
        if part in {'.git', 'vendor', 'node_modules', '.idea', '.commanding', '.watchdog', '.sandbox', 'var', 'cache', 'build', 'dist'}:
            return True
    return False


def iter_files(repo_dir: Path, suffixes: set[str] | None = None, limit: int | None = None) -> list[Path]:
    files: list[Path] = []
    for path in repo_dir.rglob('*'):
        if not path.is_file() or should_skip_path(path.relative_to(repo_dir)):
            continue
        if suffixes is not None and path.suffix.lower() not in suffixes:
            continue
        files.append(path)
        if limit is not None and len(files) >= limit:
            break
    return files


def rel(path: Path, repo_dir: Path) -> str:
    return path.relative_to(repo_dir).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore')


def finding(severity: str, finding_id: str, detail: str, path: str | None = None) -> dict[str, Any]:
    payload = {'severity': severity, 'id': finding_id, 'detail': detail}
    if path:
        payload['path'] = path
    return payload


def family_result(title: str, findings: list[dict[str, Any]], evidence: list[str], summary: str | None = None, na: bool = False) -> dict[str, Any]:
    fail_count = sum(1 for item in findings if item['severity'] == 'fail')
    warn_count = sum(1 for item in findings if item['severity'] == 'warn')
    info_count = sum(1 for item in findings if item['severity'] == 'info')
    if na:
        status = 'not_applicable'
        score = None
    else:
        status = 'fail' if fail_count else ('warn' if warn_count else 'pass')
        score = max(0.0, round(10.0 - fail_count * 2.5 - warn_count * 1.0 - info_count * 0.25, 2))
    blockers = [item['detail'] for item in findings if item['severity'] in {'fail', 'warn'}][:5]
    if summary is None:
        if na:
            summary = 'Probe family is currently not applicable for this repository surface.'
        elif fail_count or warn_count or info_count:
            summary = f'{fail_count} fail, {warn_count} warn, {info_count} info findings detected.'
        else:
            summary = 'No material probe findings detected in this family.'
    return {
        'title': title,
        'status': status,
        'score': score,
        'summary': summary,
        'blockers': blockers,
        'findings': findings,
        'evidence': sorted(set(evidence)),
    }


def summarize_probe_snapshot(probe_snapshot: dict[str, Any]) -> dict[str, Any]:
    counts = {'pass': 0, 'warn': 0, 'fail': 0, 'not_applicable': 0}
    families_summary: dict[str, Any] = {}
    top_blockers: list[str] = []
    for family_id, family in (probe_snapshot.get('families') or {}).items():
        status = family.get('status', 'warn')
        counts[status] = counts.get(status, 0) + 1
        families_summary[family_id] = {
            'title': family.get('title', family_id),
            'status': status,
            'score': family.get('score'),
            'summary': family.get('summary', ''),
            'blockers': family.get('blockers', [])[:3],
        }
        for blocker in family.get('blockers', [])[:2]:
            top_blockers.append(f"{family.get('title', family_id)} — {blocker}")
    overall_status = 'fail' if counts['fail'] else ('warn' if counts['warn'] else 'pass')
    score_values = [family.get('score') for family in (probe_snapshot.get('families') or {}).values() if isinstance(family.get('score'), (int, float))]
    average_score = round(sum(score_values) / len(score_values), 2) if score_values else None
    return {
        'overall_status': overall_status,
        'average_score': average_score,
        'status_counts': counts,
        'top_blockers': top_blockers[:8],
        'families': families_summary,
    }


def seed_probe_snapshot(component: dict[str, Any], snapshot_date: str, label: str) -> dict[str, Any]:
    component_id = str(component.get('component_id') or component.get('component') or '')
    title = str(component.get('component_title') or component.get('title') or component_id)
    families: dict[str, Any] = {}
    for family in load_probe_families():
        families[family['id']] = family_result(
            family['title'],
            [finding('warn', 'seed_pending', 'Seed probe pending first deterministic repository assessment.')],
            [],
            summary='Seed probe pending first deterministic repository assessment.',
        )
    summary = summarize_probe_snapshot({'families': families})
    return {
        'component': component_id,
        'title': title,
        'snapshot': {
            'date': snapshot_date,
            'label': label,
            'origin': 'quality-atlas probe seed',
            'generated_at': datetime.now(timezone.utc).isoformat(),
        },
        'repo_target': {
            'github_repository': component.get('github_repository') or component.get('repo_full_name') or '',
            'local_path': component.get('local_path') or '',
            'default_branch': component.get('default_branch', 'master'),
        },
        'families': families,
        'summary': summary,
    }


def write_probe_files(component_id: str, probe_snapshot: dict[str, Any]) -> tuple[Path, Path]:
    component_dir = ROOT / '.sync' / 'quality-atlas' / 'components' / component_id / 'probes'
    label = probe_snapshot['snapshot']['label']
    snap_date = probe_snapshot['snapshot']['date']
    history_path = component_dir / 'history' / f'{snap_date}-{label}.yaml'
    current_path = component_dir / 'current.yaml'
    if not history_path.exists():
        write_yaml(history_path, probe_snapshot)
    write_yaml(current_path, probe_snapshot)
    return current_path, history_path


def _php_namespaces(php_files: list[Path]) -> list[str]:
    namespaces: list[str] = []
    ns_re = re.compile(r'^namespace\s+([^;]+);', re.MULTILINE)
    for path in php_files:
        match = ns_re.search(read_text(path))
        if match:
            namespaces.append(match.group(1).strip())
    return namespaces


def _docblock_ratio(php_files: list[Path]) -> tuple[int, int]:
    methods = 0
    documented = 0
    method_re = re.compile(r'(^|\n)\s*(public|protected)\s+function\s+[A-Za-z0-9_]+\s*\(', re.MULTILINE)
    for path in php_files:
        lines = read_text(path).splitlines()
        for idx, line in enumerate(lines):
            if re.search(r'\b(public|protected)\s+function\s+[A-Za-z0-9_]+\s*\(', line):
                methods += 1
                context = '\n'.join(lines[max(0, idx - 3):idx])
                if '/**' in context:
                    documented += 1
    return methods, documented


def _constructor_param_count(text: str) -> int:
    match = re.search(r'__construct\s*\((.*?)\)', text, re.S)
    if not match:
        return 0
    raw = match.group(1).strip()
    if not raw:
        return 0
    return raw.count('$')


def collect_repo_probes(repo_dir: Path, component: dict[str, Any]) -> dict[str, Any]:
    component_id = str(component.get('component_id') or '')
    title = str(component.get('component_title') or component_id)
    if not repo_dir.exists():
        placeholder = seed_probe_snapshot(component, date.today().isoformat(), 'repo-missing')
        placeholder['summary']['overall_status'] = 'warn'
        return placeholder

    php_files = iter_files(repo_dir, {PHP_SUFFIX})
    text_files = iter_files(repo_dir, TEXT_SUFFIXES, limit=500)
    family_contract = {item['id']: item for item in load_probe_families()}
    families: dict[str, Any] = {}

    # Canon & Structure
    canon_findings: list[dict[str, Any]] = []
    canon_evidence: list[str] = []
    legacy_re = re.compile(r'^(legacy|deprecated|obsolete|backup|bak|old)$', re.I)
    for path in repo_dir.rglob('*'):
        if should_skip_path(path.relative_to(repo_dir)):
            continue
        if legacy_re.match(path.name):
            canon_findings.append(finding('warn', 'legacy_marker', 'Legacy/deprecated marker found in tree.', rel(path, repo_dir)))
            canon_evidence.append(rel(path, repo_dir))
    tokens = component_tokens(component)
    for path in repo_dir.rglob('*'):
        if not path.is_dir() or should_skip_path(path.relative_to(repo_dir)):
            continue
        rel_path = path.relative_to(repo_dir)
        norm_name = normalize_text_name(path.name)
        if norm_name not in tokens:
            continue
        parts = rel_path.parts
        if len(parts) == 1 or (parts and parts[0] == 'src' and len(parts) in {2, 3}):
            canon_findings.append(finding('fail', 'forbidden_domain_depth', 'Repository/domain-named directory is too close to root for owner canon.', rel_path.as_posix()))
            canon_evidence.append(rel_path.as_posix())
    if php_files:
        for path in php_files:
            text = read_text(path)
            match = re.search(r'^namespace\s+([^;]+);', text, re.MULTILINE)
            if match and not match.group(1).startswith('App\\'):
                canon_findings.append(finding('warn', 'namespace_drift', 'PHP namespace does not use the default App\\ root.', rel(path, repo_dir)))
                canon_evidence.append(rel(path, repo_dir))
                break
    mysql_hits = [rel(path, repo_dir) for path in text_files if re.search(r'\b(mysql|mariadb)\b', read_text(path), re.I)]
    pg_hits = [rel(path, repo_dir) for path in text_files if re.search(r'\b(postgres|postgresql|pgsql)\b', read_text(path), re.I)]
    if mysql_hits and pg_hits:
        canon_findings.append(finding('warn', 'dialect_mixing', 'Both MySQL and PostgreSQL dialect markers are present; keep dialect trees clearly separated.', mysql_hits[0]))
        canon_evidence.extend(mysql_hits[:1] + pg_hits[:1])
    families['canon_structure'] = family_result(family_contract['canon_structure']['title'], canon_findings, canon_evidence)

    # Architecture & Boundaries
    arch_findings: list[dict[str, Any]] = []
    arch_evidence: list[str] = []
    boundary_files = [rel(path, repo_dir) for path in text_files if 'boundary' in path.name.lower() or 'bounded' in path.name.lower()]
    if not boundary_files:
        arch_findings.append(finding('warn', 'boundary_descriptors_missing', 'No obvious boundary descriptor files were detected.'))
    else:
        arch_evidence.extend(boundary_files[:5])
    entity_use_re = re.compile(r'use\s+App\\Entity\\', re.M)
    for path in php_files:
        if '/Entity/' in path.as_posix() or path.as_posix().endswith('/Entity'):
            continue
        if entity_use_re.search(read_text(path)):
            arch_findings.append(finding('warn', 'entity_leakage_signal', 'Non-entity PHP file imports App\\Entity directly; review vertical leakage.', rel(path, repo_dir)))
            arch_evidence.append(rel(path, repo_dir))
            if len(arch_findings) >= 5:
                break
    for expected in ['src', 'tests']:
        if not (repo_dir / expected).exists():
            arch_findings.append(finding('warn', 'missing_vertical_segment', f'Missing expected repository segment: {expected}/.'))
    families['architecture_boundaries'] = family_result(family_contract['architecture_boundaries']['title'], arch_findings, arch_evidence)

    # Runtime surface
    runtime_findings: list[dict[str, Any]] = []
    runtime_evidence: list[str] = []
    docker_paths = [rel(path, repo_dir) for path in repo_dir.rglob('*') if path.name in {'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml'}]
    if not docker_paths:
        runtime_findings.append(finding('warn', 'docker_surface_missing', 'No Docker or compose files were detected.'))
    else:
        runtime_evidence.extend(docker_paths[:5])
    health_hits = [rel(path, repo_dir) for path in text_files if re.search(r'\b(health|readiness|liveness|ready)\b', read_text(path), re.I)]
    if not health_hits:
        runtime_findings.append(finding('info', 'health_surface_not_found', 'No obvious health/readiness markers were detected.'))
    else:
        runtime_evidence.extend(health_hits[:3])
    families['runtime_surface'] = family_result(family_contract['runtime_surface']['title'], runtime_findings, runtime_evidence)

    # QA & behavioral assurance
    qa_findings: list[dict[str, Any]] = []
    qa_evidence: list[str] = []
    tests_exists = (repo_dir / 'tests').exists()
    fixtures_hits = [rel(path, repo_dir) for path in repo_dir.rglob('*') if path.is_dir() and path.name.lower() == 'fixtures']
    playwright_hits = [rel(path, repo_dir) for path in text_files if 'playwright' in read_text(path).lower()]
    panther_hits = [rel(path, repo_dir) for path in text_files if 'panther' in read_text(path).lower()]
    if not tests_exists:
        qa_findings.append(finding('fail', 'tests_missing', 'tests/ directory is missing.'))
    else:
        qa_evidence.append('tests/')
    if not fixtures_hits:
        qa_findings.append(finding('warn', 'fixtures_missing', 'No fixtures directories were detected.'))
    else:
        qa_evidence.extend(fixtures_hits[:3])
    if not playwright_hits and not panther_hits:
        qa_findings.append(finding('warn', 'browser_behavior_missing', 'Neither Playwright nor Symfony Panther markers were detected.'))
    else:
        qa_evidence.extend(playwright_hits[:2] + panther_hits[:2])
    families['qa_behavior'] = family_result(family_contract['qa_behavior']['title'], qa_findings, qa_evidence)

    # Documentation suite
    docs_findings: list[dict[str, Any]] = []
    docs_evidence: list[str] = []
    for required in ['README.md', 'CHANGELOG.md']:
        if not (repo_dir / required).exists():
            docs_findings.append(finding('warn', 'missing_doc_asset', f'Missing expected documentation asset: {required}.'))
        else:
            docs_evidence.append(required)
    methods, documented = _docblock_ratio(php_files)
    if methods:
        ratio = documented / methods
        if ratio < 0.6:
            docs_findings.append(finding('warn', 'docblock_coverage_low', f'Public/protected docblock coverage is {documented}/{methods} ({ratio:.0%}).'))
        docs_evidence.append(f'php-docblock-ratio:{documented}/{methods}')
    nelmio_hits = [rel(path, repo_dir) for path in text_files if re.search(r'nelmio|openapi', read_text(path), re.I)]
    if not nelmio_hits:
        docs_findings.append(finding('info', 'nelmio_openapi_not_detected', 'No obvious Nelmio/OpenAPI markers were detected.'))
    else:
        docs_evidence.extend(nelmio_hits[:5])
    gh_suite = [path for path in ['.github/workflows', '.github/ISSUE_TEMPLATE', '.github/PULL_REQUEST_TEMPLATE.md'] if (repo_dir / path).exists()]
    if not gh_suite:
        docs_findings.append(finding('warn', 'github_suite_sparse', 'GitHub Suite support files appear sparse.'))
    else:
        docs_evidence.extend(gh_suite)
    families['documentation_suite'] = family_result(family_contract['documentation_suite']['title'], docs_findings, docs_evidence, na=not php_files and not (repo_dir / 'README.md').exists())

    # Delivery & observability
    delivery_findings: list[dict[str, Any]] = []
    delivery_evidence: list[str] = []
    workflow_files = [rel(path, repo_dir) for path in (repo_dir / '.github' / 'workflows').glob('*.yml')] if (repo_dir / '.github' / 'workflows').exists() else []
    if not workflow_files:
        delivery_findings.append(finding('warn', 'workflows_missing', 'No GitHub workflow files were detected.'))
    else:
        delivery_evidence.extend(workflow_files[:10])
    prom_hits = [rel(path, repo_dir) for path in text_files if re.search(r'prometheus|grafana', read_text(path), re.I)]
    if not prom_hits:
        delivery_findings.append(finding('info', 'observability_markers_missing', 'No Prometheus/Grafana markers were detected.'))
    else:
        delivery_evidence.extend(prom_hits[:5])
    deploy_hits = [rel(path, repo_dir) for path in text_files if re.search(r'kubernetes|helm|docker|compose|deployment', read_text(path), re.I)]
    if not deploy_hits:
        delivery_findings.append(finding('warn', 'deploy_markers_sparse', 'Deploy or packaging markers appear sparse.'))
    else:
        delivery_evidence.extend(deploy_hits[:5])
    families['delivery_observability'] = family_result(family_contract['delivery_observability']['title'], delivery_findings, delivery_evidence)

    # SOLID & refactoring pressure
    solid_findings: list[dict[str, Any]] = []
    solid_evidence: list[str] = []
    if not php_files:
        families['solid_refactoring'] = family_result(family_contract['solid_refactoring']['title'], [], [], summary='Repository has no PHP surface; SOLID heuristics are not applicable here.', na=True)
    else:
        for path in php_files:
            text = read_text(path)
            lines = len(text.splitlines())
            public_methods = len(re.findall(r'\bpublic\s+function\b', text))
            constructor_params = _constructor_param_count(text)
            if lines > 450:
                solid_findings.append(finding('fail', 'large_class', f'PHP file is very large ({lines} lines); review SRP and refactoring pressure.', rel(path, repo_dir)))
                solid_evidence.append(rel(path, repo_dir))
            elif lines > 320:
                solid_findings.append(finding('warn', 'class_size_pressure', f'PHP file is large ({lines} lines); review SRP pressure.', rel(path, repo_dir)))
                solid_evidence.append(rel(path, repo_dir))
            if public_methods > 12:
                solid_findings.append(finding('warn', 'public_api_pressure', f'Class exposes {public_methods} public methods; review interface segregation and SRP.', rel(path, repo_dir)))
                solid_evidence.append(rel(path, repo_dir))
            if constructor_params > 6:
                solid_findings.append(finding('warn', 'constructor_injection_pressure', f'Constructor injects {constructor_params} parameters; review dependency inversion and class responsibilities.', rel(path, repo_dir)))
                solid_evidence.append(rel(path, repo_dir))
            if len(solid_findings) >= 12:
                break
        provenance_patterns = [r'copied from', r'adapted from', r'stackoverflow', r'github\.com/', r'original author', r'ported from']
        for path in text_files[:200]:
            text = read_text(path).lower()
            if any(re.search(pattern, text) for pattern in provenance_patterns):
                solid_findings.append(finding('info', 'copy_paste_origin_marker', 'Possible copy-paste provenance marker detected; review SOLID and ownership fit.', rel(path, repo_dir)))
                solid_evidence.append(rel(path, repo_dir))
                if len(solid_evidence) >= 10:
                    break
        families['solid_refactoring'] = family_result(family_contract['solid_refactoring']['title'], solid_findings, solid_evidence)

    probe_snapshot = {
        'component': component_id,
        'title': title,
        'snapshot': {
            'date': date.today().isoformat(),
            'label': 'live-probe' if component.get('enabled') else 'probe',
            'origin': 'quality-atlas deterministic probes',
            'generated_at': datetime.now(timezone.utc).isoformat(),
        },
        'repo_target': {
            'github_repository': component.get('github_repository') or component.get('repo_full_name') or '',
            'local_path': component.get('local_path') or '',
            'default_branch': component.get('default_branch', 'master'),
        },
        'families': families,
    }
    probe_snapshot['summary'] = summarize_probe_snapshot(probe_snapshot)
    return probe_snapshot
