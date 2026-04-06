#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY_FILE = ROOT / '.sync' / 'quality-atlas' / 'schedules' / 'assessment-policy.yaml'
REGISTRY_FILE = ROOT / '.sync' / 'quality-atlas' / 'repositories' / 'ecosystem-repositories.yaml'
COMPONENTS_DIR = ROOT / '.sync' / 'quality-atlas' / 'components'
GENERATED_DIR = ROOT / '.sync' / 'quality-atlas' / 'generated'
PLAN_FILE = GENERATED_DIR / 'selection-plan.json'
QUALITY_DIR = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'pages' / 'quality-atlas'
NAV_FILE = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'nav.adoc'
HOME_FILE = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'pages' / 'index.adoc'


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + '\n', encoding='utf-8')


def load_snapshot_summary(component_id: str) -> dict:
    current = COMPONENTS_DIR / component_id / 'current.yaml'
    if not current.exists():
        return {}
    payload = load_yaml(current)
    snapshot = payload.get('snapshot') or {}
    basis = snapshot.get('assessment_basis') or {}
    metrics = payload.get('metrics') or {}
    return {
        'snapshot_date': snapshot.get('date'),
        'snapshot_label': snapshot.get('label'),
        'overall': ((metrics.get('overall') or {}).get('score')),
        'assessed_commit': basis.get('assessed_commit'),
        'assessed_tag': basis.get('assessed_tag'),
        'trigger_reason': basis.get('trigger_reason'),
    }


def build_payload() -> dict:
    policy = load_yaml(POLICY_FILE)
    registry = load_yaml(REGISTRY_FILE)
    plan = json.loads(PLAN_FILE.read_text(encoding='utf-8')) if PLAN_FILE.exists() else {'selected_components': [], 'items': []}
    plan_index = {item['component']: item for item in plan.get('items') or []}
    components = []
    for item in registry.get('repositories') or []:
        if not item.get('enabled'):
            continue
        component_id = item['component_id']
        snapshot = load_snapshot_summary(component_id)
        override = (policy.get('component_overrides') or {}).get(component_id, {})
        cadence_group = override.get('cadence_group') or item.get('cadence_group') or policy['defaults']['cadence_group']
        components.append({
            'component': component_id,
            'title': item.get('component_title'),
            'cadence_group': cadence_group,
            'repository': item.get('github_repository') or item.get('local_path') or '',
            'snapshot': snapshot,
            'selection': plan_index.get(component_id, {}),
        })
    return {'policy': policy, 'plan': plan, 'components': components}


def build_html(payload: dict) -> str:
    plan_json = json.dumps(payload, ensure_ascii=False)
    return f"""<div id=\"qa-schedule\">
<style>
#qa-schedule{{font-family:system-ui,-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif;color:#1d2433;}}
.qas-grid{{display:grid;grid-template-columns:360px 1fr;gap:22px;}}
.qas-panel,.qas-main,.qas-box{{background:#fff;border:1px solid #d9dde8;border-radius:18px;box-shadow:0 16px 44px rgba(16,24,40,.06);}}
.qas-panel{{padding:18px;position:sticky;top:84px;height:fit-content;}}
.qas-main{{padding:20px;display:grid;gap:18px;}}
.qas-kpis{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;}}
.qas-kpi{{border:1px solid #d9dde8;border-radius:16px;padding:14px;background:linear-gradient(180deg,#fff,#f8faff);}}
.qas-kpi .big{{font-size:26px;font-weight:700;margin-top:4px;}}
.qas-table{{display:grid;gap:10px;}}
.qas-row{{display:grid;grid-template-columns:1.2fr .7fr .7fr 1.1fr;gap:12px;border:1px solid #d9dde8;border-radius:14px;padding:12px;background:#fcfdff;}}
.qas-meta{{font-size:12px;color:#66708a;}}
.qas-pill{{display:inline-flex;align-items:center;border-radius:999px;padding:3px 8px;font-size:11px;font-weight:700;background:#eef3ff;color:#3154d6;}}
.qas-pill.skip{{background:#f1f3f9;color:#6b7286;}} .qas-pill.select{{background:#e9f9f2;color:#128157;}}
.qas-box{{padding:18px;}}
@media (max-width:1100px){{.qas-grid{{grid-template-columns:1fr;}}.qas-kpis{{grid-template-columns:repeat(2,minmax(0,1fr));}}.qas-panel{{position:static;}}.qas-row{{grid-template-columns:1fr;}}}}
</style>
<div class=\"qas-grid\">
  <div class=\"qas-panel\">
    <h2 style=\"margin-top:0;\">Assessment schedule</h2>
    <p style=\"color:#5d6781;line-height:1.55;\">This page explains why the scheduler selected or skipped components. It protects API spend by requiring meaningful changes, tags, or age-based refresh windows before a full AI assessment runs.</p>
    <p class=\"qas-meta\">Policy source: <code>.sync/quality-atlas/schedules/assessment-policy.yaml</code></p>
    <p class=\"qas-meta\">Latest plan: <code>.sync/quality-atlas/generated/selection-plan.json</code></p>
  </div>
  <div class=\"qas-main\">
    <div class=\"qas-kpis\">
      <div class=\"qas-kpi\"><div>Enabled components</div><div class=\"big\" id=\"qas-enabled\"></div></div>
      <div class=\"qas-kpi\"><div>Selected this plan</div><div class=\"big\" id=\"qas-selected\"></div></div>
      <div class=\"qas-kpi\"><div>Plan status</div><div class=\"big\" id=\"qas-status\"></div></div>
      <div class=\"qas-kpi\"><div>Event</div><div class=\"big\" id=\"qas-event\"></div></div>
    </div>
    <div class=\"qas-box\"><h3 style=\"margin-top:0;\">Current selection plan</h3><div class=\"qas-table\" id=\"qas-table\"></div></div>
  </div>
</div>
<script>
const QAS = {plan_json};
document.getElementById('qas-enabled').textContent = QAS.components.length;
document.getElementById('qas-selected').textContent = (QAS.plan.selected_components || []).length;
document.getElementById('qas-status').textContent = QAS.plan.status || 'n/a';
document.getElementById('qas-event').textContent = QAS.plan.event_name || 'n/a';
const table = document.getElementById('qas-table');
QAS.components.forEach((item) => {{
  const sel = item.selection || {{}};
  const div = document.createElement('div');
  div.className = 'qas-row';
  div.innerHTML = `<div><strong>${{item.title}}</strong><div class=\"qas-meta\">${{item.repository || 'local'}} · cadence ${{item.cadence_group}}</div><div class=\"qas-meta\">last snapshot ${{item.snapshot.snapshot_date || 'n/a'}} · commit ${{item.snapshot.assessed_commit || 'n/a'}}</div></div><div><span class=\"qas-pill ${{sel.selected ? 'select' : 'skip'}}\">${{sel.selected ? 'selected' : 'skipped'}}</span><div class=\"qas-meta\">reason: ${{sel.reason || 'n/a'}}</div></div><div><div class=\"qas-meta\">head ${{sel.current_head_commit || 'n/a'}}</div><div class=\"qas-meta\">tag ${{sel.current_head_tag || 'n/a'}}</div></div><div><div class=\"qas-meta\">meaningful: ${{(sel.meaningful_changes || []).join(', ') || 'none'}}</div><div class=\"qas-meta\">noise: ${{(sel.noise_changes || []).join(', ') || 'none'}}</div></div>`;
  table.appendChild(div);
}});
</script></div>"""


def patch_nav() -> None:
    text = NAV_FILE.read_text(encoding='utf-8')
    anchor = '* xref:quality-atlas/index.adoc[Quality Atlas]\n'
    child = '** xref:quality-atlas/schedule.adoc[Schedule]\n'
    if child not in text and anchor in text:
        text = text.replace(anchor, anchor + child)
        write(NAV_FILE, text)


def patch_home() -> None:
    text = HOME_FILE.read_text(encoding='utf-8')
    bullet = '* xref:quality-atlas/schedule.adoc[Schedule] — cadence, meaningful-change selection, and current assessment plan.\n'
    if bullet not in text and '== Pre-RC Quality Atlas\n' in text:
        text = text.replace('== Pre-RC Quality Atlas\n\n', '== Pre-RC Quality Atlas\n\n' + bullet + '\n')
        write(HOME_FILE, text)


def main() -> None:
    payload = build_payload()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    (GENERATED_DIR / 'selection-plan-dataset.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    write(QUALITY_DIR / 'schedule.adoc', f'''= Quality Atlas Schedule
:description: Assessment cadence, meaningful-change policy, and latest selection plan.

This page is generated from `.sync/quality-atlas/schedules/assessment-policy.yaml`, the repository registry, and the latest selection plan.

* xref:quality-atlas/index.adoc[Back to Quality Atlas]
* xref:quality-atlas/internal.adoc[Open internal cockpit]

++++
{build_html(payload)}
++++
''')
    patch_nav()
    patch_home()


if __name__ == '__main__':
    main()
