#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS_DIR = ROOT / '.sync' / 'quality-atlas' / 'components'
QUALITY_DIR = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'pages' / 'quality-atlas'
NAV_FILE = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'nav.adoc'
HOME_FILE = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'pages' / 'index.adoc'
GENERATED_DIR = ROOT / '.sync' / 'quality-atlas' / 'generated'


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + '\n', encoding='utf-8')


def load_components() -> list[dict]:
    components: list[dict] = []
    for component_dir in sorted(COMPONENTS_DIR.iterdir()):
        if not component_dir.is_dir():
            continue
        current = component_dir / 'current.yaml'
        probes = component_dir / 'probes' / 'current.yaml'
        if not current.exists() or not probes.exists():
            continue
        snapshot = load_yaml(current)
        probe_snapshot = load_yaml(probes)
        summary = probe_snapshot.get('summary') or {}
        components.append({
            'component': snapshot.get('component'),
            'title': snapshot.get('title'),
            'overall': ((snapshot.get('metrics') or {}).get('overall') or {}).get('score'),
            'snapshot': snapshot.get('snapshot') or {},
            'development_driving': snapshot.get('development_driving') or {},
            'probe_summary': summary,
            'families': probe_snapshot.get('families') or {},
        })
    return components


def build_payload() -> dict:
    components = load_components()
    family_ids: list[str] = []
    for component in components:
        for family_id in component['families'].keys():
            if family_id not in family_ids:
                family_ids.append(family_id)
    family_stats = []
    for family_id in family_ids:
        titles = [component['families'][family_id]['title'] for component in components if family_id in component['families']]
        scores = [component['families'][family_id]['score'] for component in components if isinstance(component['families'][family_id].get('score'), (int, float))]
        statuses = {'pass': 0, 'warn': 0, 'fail': 0, 'not_applicable': 0}
        for component in components:
            family = component['families'].get(family_id)
            if family:
                statuses[family['status']] = statuses.get(family['status'], 0) + 1
        family_stats.append({
            'id': family_id,
            'title': titles[0] if titles else family_id,
            'average_score': round(mean(scores), 2) if scores else None,
            'statuses': statuses,
        })
    blockers = []
    for component in components:
        for blocker in (component['probe_summary'].get('top_blockers') or [])[:5]:
            blockers.append({'component': component['title'], 'detail': blocker, 'status': component['probe_summary'].get('overall_status', 'warn')})
    blockers = blockers[:30]
    return {'components': components, 'family_stats': family_stats, 'blockers': blockers}


def build_html(payload: dict) -> str:
    return f"""<div id=\"qa-internal\">\n<style>\n#qa-internal{{font-family:system-ui,-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif;color:#1d2433;}}\n.qai-grid{{display:grid;grid-template-columns:340px 1fr;gap:22px;}}\n.qai-panel,.qai-main,.qai-box{{background:#fff;border:1px solid #d9dde8;border-radius:18px;box-shadow:0 16px 44px rgba(16,24,40,.06);}}\n.qai-panel{{padding:18px;position:sticky;top:84px;height:fit-content;}}\n.qai-main{{padding:20px;display:grid;gap:18px;}}\n.qai-kpis{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;}}\n.qai-kpi{{border:1px solid #d9dde8;border-radius:16px;padding:14px;background:linear-gradient(180deg,#fff,#f8faff);}}\n.qai-kpi .big{{font-size:26px;font-weight:700;margin-top:4px;}}\n.qai-two{{display:grid;grid-template-columns:1.1fr .9fr;gap:18px;}}\n.qai-box{{padding:18px;}}\n.qai-family-list,.qai-blockers,.qai-components{{display:grid;gap:10px;}}\n.qai-family,.qai-item{{border:1px solid #d9dde8;border-radius:14px;padding:12px;background:#fcfdff;}}\n.qai-status{{display:inline-flex;align-items:center;gap:8px;font-weight:600;}}\n.qai-dot{{width:10px;height:10px;border-radius:999px;display:inline-block;}}\n.qai-dot.pass{{background:#1fa971;}} .qai-dot.warn{{background:#ffb020;}} .qai-dot.fail{{background:#ff5d5d;}} .qai-dot.not_applicable{{background:#94a0ba;}}\n.qai-meta{{font-size:12px;color:#66708a;}}\n.qai-field{{display:grid;gap:8px;margin-bottom:14px;}}\n.qai-field label{{font-size:12px;color:#66708a;text-transform:uppercase;letter-spacing:.04em;font-weight:700;}}\n.qai-field select{{border:1px solid #cdd3e2;border-radius:12px;padding:10px 12px;font-size:14px;background:#fff;}}\n@media (max-width:1100px){{.qai-grid{{grid-template-columns:1fr;}}.qai-kpis{{grid-template-columns:repeat(2,minmax(0,1fr));}}.qai-two{{grid-template-columns:1fr;}}.qai-panel{{position:static;}}}}\n</style>\n<div class=\"qai-grid\">\n  <div class=\"qai-panel\">\n    <h2 style=\"margin-top:0;\">Internal Development Driving</h2>\n    <p style=\"color:#5d6781;line-height:1.55;\">This internal page sits above the deterministic probe layer. It is intended for canon drift review, SOLID refactoring pressure review, and RC hardening decisions.</p>\n    <div class=\"qai-field\"><label>Component</label><select id=\"qai-component\"></select></div>\n    <p style=\"font-size:12px;color:#66708a;margin-bottom:0;\">Probe data lives under <code>.sync/quality-atlas/components/*/probes/current.yaml</code>.</p>\n  </div>\n  <div class=\"qai-main\">\n    <div class=\"qai-kpis\">\n      <div class=\"qai-kpi\"><div>Probe families</div><div class=\"big\" id=\"qai-family-count\"></div></div>\n      <div class=\"qai-kpi\"><div>Average score</div><div class=\"big\" id=\"qai-average-score\"></div></div>\n      <div class=\"qai-kpi\"><div>Overall probe status</div><div id=\"qai-overall-status\"></div></div>\n      <div class=\"qai-kpi\"><div>Top blockers</div><div class=\"big\" id=\"qai-blocker-count\"></div></div>\n    </div>\n    <div class=\"qai-two\">\n      <div class=\"qai-box\"><h3 style=\"margin-top:0;\">Family breakdown</h3><div class=\"qai-family-list\" id=\"qai-families\"></div></div>\n      <div class=\"qai-box\"><h3 style=\"margin-top:0;\">Top blockers across current components</h3><div class=\"qai-blockers\" id=\"qai-blockers\"></div></div>\n    </div>\n    <div class=\"qai-box\"><h3 style=\"margin-top:0;\">Component overview</h3><div class=\"qai-components\" id=\"qai-components\"></div></div>\n  </div>\n</div>\n<script>\nconst QA_INTERNAL = {json.dumps(payload, ensure_ascii=False)};\nconst select=document.getElementById('qai-component');\nfunction fillSelect(){{QA_INTERNAL.components.forEach((component,index)=>{{const opt=document.createElement('option');opt.value=component.component;opt.textContent=component.title;select.appendChild(opt);if(index===0)select.value=component.component;}});}}\nfunction dot(status){{return `<span class=\"qai-dot ${'{'}status{'}'}\"></span>`;}}\nfunction selected(){{return QA_INTERNAL.components.find(c=>c.component===select.value) || QA_INTERNAL.components[0];}}\nfunction render(){{const component=selected();const summary=component.probe_summary || {{}};document.getElementById('qai-family-count').textContent=Object.keys(component.families || {{}}).length;document.getElementById('qai-average-score').textContent=(summary.average_score ?? 'n/a');document.getElementById('qai-overall-status').innerHTML=`<span class=\"qai-status\">${'{'}dot(summary.overall_status || 'warn'){'}'} ${'{'}summary.overall_status || 'warn'{'}'}</span>`;document.getElementById('qai-blocker-count').textContent=(summary.top_blockers || []).length;const families=document.getElementById('qai-families');families.innerHTML='';Object.entries(component.families || {{}}).forEach(([familyId,family])=>{{const div=document.createElement('div');div.className='qai-family';div.innerHTML=`<div style=\"display:flex;justify-content:space-between;gap:12px;align-items:center;\"><strong>${'{'}family.title{'}'}</strong><span class=\"qai-status\">${'{'}dot(family.status){'}'} ${'{'}family.status{'}'}</span></div><div class=\"qai-meta\">score: ${'{'}family.score ?? 'n/a'{'}'}</div><p style=\"margin:8px 0 0;color:#374056;\">${'{'}family.summary{'}'}</p><div class=\"qai-meta\">${'{'}(family.blockers || []).join(' • '){'}'}</div>`;families.appendChild(div);}});const blockers=document.getElementById('qai-blockers');blockers.innerHTML='';QA_INTERNAL.blockers.forEach((item)=>{{const div=document.createElement('div');div.className='qai-item';div.innerHTML=`<strong>${'{'}item.component{'}'}</strong><div class=\"qai-meta\">${'{'}item.detail{'}'}</div>`;blockers.appendChild(div);}});const components=document.getElementById('qai-components');components.innerHTML='';QA_INTERNAL.components.forEach((item)=>{{const status=item.probe_summary?.overall_status || 'warn';const div=document.createElement('div');div.className='qai-item';div.innerHTML=`<div style=\"display:flex;justify-content:space-between;gap:12px;align-items:center;\"><strong>${'{'}item.title{'}'}</strong><span class=\"qai-status\">${'{'}dot(status){'}'} ${'{'}status{'}'}</span></div><div class=\"qai-meta\">overall ${'{'}item.overall ?? 'n/a'{'}'} · probe avg ${'{'}item.probe_summary?.average_score ?? 'n/a'{'}'} · snapshot ${'{'}item.snapshot?.label || 'n/a'{'}'}</div>`;components.appendChild(div);}});}}\nfillSelect();render();select.addEventListener('change',render);\n</script></div>"""


def write_internal_page(payload: dict) -> None:
    write(QUALITY_DIR / 'internal.adoc', f'''= Quality Atlas Internal
:description: Internal development-driving cockpit built from deterministic probe layers and canonical component snapshots.

This page is generated from `.sync/quality-atlas/components/*/probes/current.yaml` and paired component `current.yaml` snapshots.

* xref:quality-atlas/index.adoc[Back to Quality Atlas]
* xref:quality-atlas/portfolio.adoc[Portfolio]

++++
{build_html(payload)}
++++
''')


def patch_nav() -> None:
    text = NAV_FILE.read_text(encoding='utf-8')
    anchor = '* xref:quality-atlas/index.adoc[Quality Atlas]\n'
    child = '** xref:quality-atlas/internal.adoc[Internal]\n'
    if child not in text and anchor in text:
        text = text.replace(anchor, anchor + child)
        write(NAV_FILE, text)


def patch_home() -> None:
    text = HOME_FILE.read_text(encoding='utf-8')
    bullet = '* xref:quality-atlas/internal.adoc[Internal] — development-driving probe cockpit for canon drift, SOLID pressure, and RC blocker review.\n'
    if bullet not in text and '== Pre-RC Quality Atlas\n' in text:
        text = text.replace('== Pre-RC Quality Atlas\n\n', '== Pre-RC Quality Atlas\n\n' + bullet + '\n')
        write(HOME_FILE, text)


def main() -> None:
    payload = build_payload()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    (GENERATED_DIR / 'internal-dataset.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    write_internal_page(payload)
    patch_nav()
    patch_home()


if __name__ == '__main__':
    main()
