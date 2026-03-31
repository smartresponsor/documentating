#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / '.antora-src'
PAGES_DIR = OUT_DIR / 'modules' / 'ROOT' / 'pages'
COMPONENT_DIR = PAGES_DIR / 'component'
NAV_FILE = OUT_DIR / 'modules' / 'ROOT' / 'nav.adoc'
IMAGE_DIR = OUT_DIR / 'modules' / 'ROOT' / 'assets' / 'images' / 'quality-atlas'

ROW_SCORE_RE = re.compile(r'(\d+(?:\.\d+)?)\s*/\s*10')
TITLE_RE = re.compile(r'^=\s+(.+?)\s+Report\s*$', re.MULTILINE)

AXES = [
    ('product', 'Product'),
    ('architecture', 'Architecture'),
    ('runtime', 'Runtime'),
    ('qa', 'QA'),
    ('ops', 'Ops/Gov/Sec'),
    ('market', 'Market'),
    ('overall', 'Overall RC'),
]
AXES_SPIDER = AXES[:-1]


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str) -> None:
    ensure(path.parent)
    path.write_text(content.rstrip() + '\n', encoding='utf-8')


def report_files() -> list[Path]:
    return sorted(COMPONENT_DIR.glob('*/report/index.adoc'))


def extract_title(text: str) -> str | None:
    m = TITLE_RE.search(text)
    return m.group(1).strip() if m else None


def extract_score_rows(text: str) -> list[tuple[str, float]]:
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == '== RC Scorecard'), None)
    if start is None:
        return []
    table_start = None
    table_end = None
    for i in range(start, len(lines)):
        if lines[i].strip() == '|===':
            if table_start is None:
                table_start = i
            else:
                table_end = i
                break
    if table_start is None or table_end is None:
        return []
    rows = [line.strip() for line in lines[table_start + 1:table_end] if line.strip().startswith('|')]
    if len(rows) >= 3 and rows[0] == '| Layer' and rows[1] == '| Score to RC' and rows[2] == '| Reading':
        rows = rows[3:]
    out: list[tuple[str, float]] = []
    i = 0
    while i + 2 < len(rows):
        label = rows[i][1:].strip()
        score_text = rows[i + 1][1:].strip()
        m = ROW_SCORE_RE.search(score_text)
        if m:
            out.append((label, float(m.group(1))))
        i += 3
    return out


def normalize_component(name: str, rows: list[tuple[str, float]]) -> dict[str, float | str] | None:
    values: dict[str, float | str] = {'component': name}
    ops_candidates: list[float] = []
    for label, score in rows:
        lo = label.lower()
        if 'product identity' in lo:
            values['product'] = score
        elif 'architecture' in lo or 'layering' in lo or 'workspace shape' in lo or 'domain shape' in lo:
            values['architecture'] = score
        elif 'runtime and application surface' in lo:
            values['runtime'] = score
        elif 'qa maturity' in lo:
            values['qa'] = score
        elif 'market-facing alignment' in lo:
            values['market'] = score
        elif 'overall readiness to rc' in lo:
            values['overall'] = score
        elif any(token in lo for token in ['governance', 'security', 'policy readiness', 'owner governance', 'operational readiness']):
            ops_candidates.append(score)
    if ops_candidates:
        values['ops'] = round(sum(ops_candidates) / len(ops_candidates), 1)
    elif 'overall' in values:
        values['ops'] = float(values['overall'])
    required = {'product', 'architecture', 'runtime', 'qa', 'ops', 'market', 'overall'}
    return values if required.issubset(values.keys()) else None


def load_dataset() -> list[dict[str, float | str]]:
    items: dict[str, dict[str, float | str]] = {}
    for path in report_files():
        text = path.read_text(encoding='utf-8')
        title = extract_title(text)
        if not title:
            continue
        rows = extract_score_rows(text)
        item = normalize_component(title, rows)
        if item is not None:
            items[title] = item
    return sorted(items.values(), key=lambda x: (-float(x['overall']), str(x['component'])))


def average_profile(data: list[dict[str, float | str]]) -> dict[str, float | str]:
    avg: dict[str, float | str] = {'component': 'Average'}
    for key, _ in AXES:
        avg[key] = round(sum(float(x[key]) for x in data) / len(data), 2)
    return avg


def strongest_axis(item: dict[str, float | str]) -> str:
    pairs = [(label, float(item[key])) for key, label in AXES_SPIDER]
    pairs.sort(key=lambda x: x[1], reverse=True)
    return f'{pairs[0][1]:.1f} · {pairs[0][0]}'


def weakest_axis(item: dict[str, float | str]) -> str:
    pairs = [(label, float(item[key])) for key, label in AXES_SPIDER]
    pairs.sort(key=lambda x: x[1])
    return f'{pairs[0][1]:.1f} · {pairs[0][0]}'


def radar_points(values: list[float], cx: float, cy: float, radius: float, vmin: float = 6.5, vmax: float = 9.5) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    total = len(values)
    for i, val in enumerate(values):
        angle = -math.pi / 2 + 2 * math.pi * i / total
        frac = max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))
        r = radius * frac
        pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    return pts


def poly(points: list[tuple[float, float]]) -> str:
    return ' '.join(f'{x:.1f},{y:.1f}' for x, y in points)


def radar_svg(item: dict[str, float | str], title: str | None = None, size: int = 240) -> str:
    cx = cy = size / 2
    radius = size * 0.30
    values = [float(item[k]) for k, _ in AXES_SPIDER]
    rings = []
    axes = []
    for frac in [0.25, 0.5, 0.75, 1.0]:
        ring_pts = []
        for i in range(len(AXES_SPIDER)):
            angle = -math.pi / 2 + 2 * math.pi * i / len(AXES_SPIDER)
            ring_pts.append((cx + math.cos(angle) * radius * frac, cy + math.sin(angle) * radius * frac))
        rings.append(f'<polygon points="{poly(ring_pts)}" class="ring" />')
    for i, (_, label) in enumerate(AXES_SPIDER):
        angle = -math.pi / 2 + 2 * math.pi * i / len(AXES_SPIDER)
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        axes.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{y:.1f}" class="axis" />')
    pts = radar_points(values, cx, cy, radius)
    texts = []
    short = {'Product': 'Product', 'Architecture': 'Arch', 'Runtime': 'Run', 'QA': 'QA', 'Ops/Gov/Sec': 'Ops', 'Market': 'Market'}
    for i, (_, label) in enumerate(AXES_SPIDER):
        angle = -math.pi / 2 + 2 * math.pi * i / len(AXES_SPIDER)
        lx = cx + math.cos(angle) * (radius + 18)
        ly = cy + math.sin(angle) * (radius + 18)
        texts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" class="tiny" text-anchor="middle">{short[label]}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" aria-label="{title or item['component']}"><style>.axis{{stroke:#b9bfd0;stroke-width:1;}}.ring{{fill:none;stroke:#d8dce8;stroke-width:1;}}.shape{{fill:rgba(20,20,20,.10);stroke:#101010;stroke-width:1.7;}}.tiny{{font:9px sans-serif;fill:#505a73;}}</style>{''.join(rings)}{''.join(axes)}<polygon points="{poly(pts)}" class="shape" />{''.join(texts)}</svg>'''


def save_summary_svgs(data: list[dict[str, float | str]]) -> list[dict[str, str | float]]:
    ensure(IMAGE_DIR)
    top3 = data[:3]
    cards = []
    for item in top3:
        slug = str(item['component']).lower()
        (IMAGE_DIR / f'{slug}.svg').write_text(radar_svg(item, str(item['component'])), encoding='utf-8')
        cards.append({'name': str(item['component']), 'slug': slug, 'overall': float(item['overall'])})
    avg = average_profile(data)
    (IMAGE_DIR / 'ecosystem-average.svg').write_text(radar_svg(avg, 'Pre-RC ecosystem average'), encoding='utf-8')
    return cards


def build_summary_adoc(data: list[dict[str, float | str]]) -> str:
    cards = save_summary_svgs(data)
    avg = average_profile(data)
    best = max(AXES_SPIDER, key=lambda kv: float(avg[kv[0]]))
    return f'''This pre-RC quality layer is auto-generated from component reports on every push to the documentation repository.

It describes the ecosystem *before release-candidate maturity and before versioned portfolio dashboards*. Once components move into stable versioned life, they should be observed in a different portfolio layer.

[cols="1,1",frame=none,grid=none]
|===
a|*{cards[0]['name']}* +
Overall RC: *{cards[0]['overall']:.1f}* +
image::quality-atlas/{cards[0]['slug']}.svg[width=240]
a|*{cards[1]['name']}* +
Overall RC: *{cards[1]['overall']:.1f}* +
image::quality-atlas/{cards[1]['slug']}.svg[width=240]

a|*{cards[2]['name']}* +
Overall RC: *{cards[2]['overall']:.1f}* +
image::quality-atlas/{cards[2]['slug']}.svg[width=240]
a|*Pre-RC ecosystem average* +
Average Overall RC: *{float(avg['overall']):.2f}* +
Strongest shared axis: *{best[1]}* ({float(avg[best[0]]):.2f}) +
image::quality-atlas/ecosystem-average.svg[width=240]
|===

* xref:quality-atlas/index.adoc[Open Pre-RC Quality Atlas]
* xref:quality-atlas/explorer.adoc[Open Pre-RC Quality Atlas Explorer]
'''


def build_atlas_html(data: list[dict[str, float | str]]) -> str:
    avg = average_profile(data)
    top5 = data[:5]
    rows = []
    for item in data:
        cells = ''.join(f'<td>{float(item[key]):.1f}</td>' for key, _ in AXES)
        rows.append(f'<tr><th>{item["component"]}</th>{cells}</tr>')
    cards = []
    for item in data:
        cards.append(f'''<div class="qa-card"><div class="qa-head"><div class="qa-title">{item['component']}</div><div class="qa-score">{float(item['overall']):.1f}</div></div>{radar_svg(item, str(item['component']), 220)}<div class="qa-note">Strongest: {strongest_axis(item)}<br>Weakest: {weakest_axis(item)}</div></div>''')
    leaders = []
    for item in top5:
        leaders.append(f'''<div class="mini-card"><div class="mini-title">{item['component']}</div><div class="mini-score">{float(item['overall']):.1f}</div><div class="mini-sub">QA {float(item['qa']):.1f} · Ops {float(item['ops']):.1f}</div></div>''')
    return f'''<div class="qa-atlas"><style>.qa-atlas{{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#111;}}.qa-panel{{background:#fff;border:1px solid #ddd;border-radius:20px;padding:22px;margin:0 0 18px 0;}}.qa-lead{{color:#666;line-height:1.55;max-width:920px;}}.qa-grid{{display:grid;grid-template-columns:1.1fr .9fr;gap:18px;}}.qa-mini-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;}}.mini-card{{border:1px solid #ddd;border-radius:14px;padding:14px;background:#fff;}}.mini-title{{font-weight:700;margin-bottom:4px;}}.mini-score{{font-size:24px;font-weight:800;margin-bottom:4px;}}.mini-sub{{color:#666;font-size:12px;}}.qa-kpis{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:16px;}}.qa-kpi{{border:1px solid #ddd;border-radius:14px;padding:14px;}}.qa-kpi .label{{color:#666;font-size:12px;}}.qa-kpi .value{{font-size:28px;font-weight:800;}}.qa-cards{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;}}.qa-card{{border:1px solid #ddd;border-radius:16px;padding:10px;background:#fff;}}.qa-head{{display:flex;justify-content:space-between;align-items:baseline;padding:4px 6px 8px 6px;}}.qa-title{{font-weight:700;font-size:14px;}}.qa-score{{font-size:16px;font-weight:800;}}.qa-note{{color:#666;font-size:12px;padding:6px;line-height:1.45;}}.qa-table-wrap{{overflow:auto;}}.qa-atlas table{{width:100%;border-collapse:collapse;font-size:14px;}}.qa-atlas th,.qa-atlas td{{border-bottom:1px solid #ddd;padding:10px;text-align:center;white-space:nowrap;}}.qa-atlas th:first-child,.qa-atlas td:first-child{{text-align:left;}}@media (max-width:1100px){{.qa-grid{{grid-template-columns:1fr;}}.qa-cards{{grid-template-columns:repeat(2,minmax(0,1fr));}}.qa-mini-grid{{grid-template-columns:1fr;}}.qa-kpis{{grid-template-columns:repeat(2,minmax(0,1fr));}}}}</style><div class="qa-panel"><h2>Pre-RC Quality Atlas</h2><p class="qa-lead">This atlas is auto-generated from component reports on every push. It describes the ecosystem before release-candidate maturity and before versioned portfolio dashboards. The layer is normalized across Product, Architecture, Runtime, QA, Ops/Governance/Security, Market Alignment, and Overall RC.</p><div class="qa-kpis"><div class="qa-kpi"><div class="label">Components</div><div class="value">{len(data)}</div></div><div class="qa-kpi"><div class="label">Average Overall RC</div><div class="value">{float(avg['overall']):.2f}</div></div><div class="qa-kpi"><div class="label">Leader</div><div class="value">{top5[0]['component']}</div></div><div class="qa-kpi"><div class="label">Explorer</div><div class="value"><a href="explorer/">Open</a></div></div></div></div><div class="qa-grid"><div class="qa-panel"><h3>Pre-RC ecosystem average profile</h3>{radar_svg(avg, 'Pre-RC average profile', 320)}</div><div class="qa-panel"><h3>Leaders in the pre-RC band</h3><div class="qa-mini-grid">{''.join(leaders)}</div></div></div><div class="qa-panel"><h3>Unified pre-RC heat table</h3><div class="qa-table-wrap"><table><thead><tr><th>Component</th>{''.join(f'<th>{label}</th>' for _, label in AXES)}</tr></thead><tbody>{''.join(rows)}</tbody></table></div></div><div class="qa-panel"><h3>Component 360° cards</h3><div class="qa-cards">{''.join(cards)}</div></div></div>'''


def build_explorer_html(data: list[dict[str, float | str]]) -> str:
    return f'''<div class="qa-explorer"><style>.qa-explorer{{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#111;}}.ex-wrap{{display:grid;grid-template-columns:300px 1fr;gap:18px;}}.ex-side,.ex-main{{background:#fff;border:1px solid #ddd;border-radius:20px;padding:18px;}}.ex-field{{display:grid;gap:6px;margin-bottom:12px;}}.ex-field label{{font-size:12px;color:#666;}}.ex-field select,.ex-field input{{padding:10px;border:1px solid #ddd;border-radius:12px;}}.ex-cards{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:16px;}}.ex-card{{border:1px solid #ddd;border-radius:14px;padding:14px;}}.ex-big{{font-size:28px;font-weight:800;}}.ex-rank{{display:grid;gap:10px;}}.ex-item{{display:grid;grid-template-columns:1fr auto;gap:12px;border:1px solid #ddd;border-radius:12px;padding:12px;}}.ex-mini{{color:#666;font-size:12px;}}@media (max-width:1100px){{.ex-wrap{{grid-template-columns:1fr;}}.ex-cards{{grid-template-columns:repeat(2,minmax(0,1fr));}}}}</style><div class="ex-wrap"><div class="ex-side"><h2>Pre-RC Quality Atlas Explorer</h2><p style="color:#666;line-height:1.55;">This is the more interactive pre-RC view. Keep the main Quality Atlas as the universal overview, and use this page when you want compare-mode or filtered pre-RC scanning.</p><div class="ex-field"><label>Main component</label><select id="atlas-component"></select></div><div class="ex-field"><label>Compare with</label><select id="atlas-compare"><option value="__average__">Pre-RC average profile</option></select></div><div class="ex-field"><label>Overall RC threshold: <span id="atlas-threshold-value">7.5</span></label><input id="atlas-threshold" type="range" min="7.5" max="9.0" step="0.1" value="7.5"></div></div><div class="ex-main"><div class="ex-cards"><div class="ex-card"><div>Selected component</div><div class="ex-big" id="atlas-selected-name"></div></div><div class="ex-card"><div>Overall RC</div><div class="ex-big" id="atlas-selected-overall"></div></div><div class="ex-card"><div>Strongest axis</div><div id="atlas-selected-strong"></div></div><div class="ex-card"><div>Weakest axis</div><div id="atlas-selected-weak"></div></div></div><div style="display:grid;grid-template-columns:1.1fr .9fr;gap:18px;"><div style="border:1px solid #ddd;border-radius:18px;padding:14px;"><canvas id="atlas-radar" width="660" height="500" style="width:100%;max-width:660px;height:auto;"></canvas></div><div style="border:1px solid #ddd;border-radius:18px;padding:14px;"><div class="ex-rank" id="atlas-ranking"></div></div></div></div></div><script>const ATLAS_DATA = {json.dumps(data, ensure_ascii=False)};const ATLAS_AXES = [['product','Product'],['architecture','Architecture'],['runtime','Runtime'],['qa','QA'],['ops','Ops/Gov/Sec'],['market','Market'],['overall','Overall RC']];function atlasAverage(items){{const out={{component:'Average'}};ATLAS_AXES.forEach(([k])=>out[k]=items.reduce((a,b)=>a+b[k],0)/items.length);return out;}}const ATLAS_AVG = atlasAverage(ATLAS_DATA);function axisStrong(item,dir){{const pairs=ATLAS_AXES.slice(0,6).map(([k,l])=>[l,item[k]]).sort((a,b)=>dir==='desc'?b[1]-a[1]:a[1]-b[1]);return `${{pairs[0][1].toFixed(1)}} · ${{pairs[0][0]}}`;}}function fillSelectors(){{const s=document.getElementById('atlas-component');const c=document.getElementById('atlas-compare');[...ATLAS_DATA].sort((a,b)=>b.overall-a.overall).forEach(x=>{{let o=document.createElement('option');o.value=x.component;o.textContent=x.component;s.appendChild(o);let p=document.createElement('option');p.value=x.component;p.textContent=x.component;c.appendChild(p);}});s.value='Shipping';c.value='__average__';}}function drawRadar(selected, compare){{const cv=document.getElementById('atlas-radar');const ctx=cv.getContext('2d');const w=cv.width,h=cv.height;ctx.clearRect(0,0,w,h);const cx=w*0.42,cy=h*0.55,r=Math.min(w,h)*0.30,vmin=6.5,vmax=9.5;function ang(i,n){{return -Math.PI/2+2*Math.PI*i/n;}} function pt(val,i,n){{const f=Math.max(0,Math.min(1,(val-vmin)/(vmax-vmin)));return {{x:cx+Math.cos(ang(i,n))*r*f,y:cy+Math.sin(ang(i,n))*r*f}};}} for(let ring=1; ring<=4; ring++){{const frac=ring/4;ctx.beginPath();ATLAS_AXES.forEach((a,i)=>{{const x=cx+Math.cos(ang(i,ATLAS_AXES.length))*r*frac;const y=cy+Math.sin(ang(i,ATLAS_AXES.length))*r*frac;if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);}});ctx.closePath();ctx.strokeStyle='rgba(180,180,180,.45)';ctx.stroke();}} ATLAS_AXES.forEach(([,label],i)=>{{const x=cx+Math.cos(ang(i,ATLAS_AXES.length))*r;const y=cy+Math.sin(ang(i,ATLAS_AXES.length))*r;ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(x,y);ctx.strokeStyle='rgba(180,180,180,.45)';ctx.stroke();const lx=cx+Math.cos(ang(i,ATLAS_AXES.length))*(r+30);const ly=cy+Math.sin(ang(i,ATLAS_AXES.length))*(r+30);ctx.fillStyle='#555';ctx.font='12px sans-serif';ctx.textAlign='center';ctx.fillText(label,lx,ly);}}); function shape(item,stroke,fill){{ctx.beginPath();ATLAS_AXES.forEach(([k],i)=>{{const p=pt(item[k],i,ATLAS_AXES.length);if(i===0)ctx.moveTo(p.x,p.y);else ctx.lineTo(p.x,p.y);}});ctx.closePath();ctx.fillStyle=fill;ctx.strokeStyle=stroke;ctx.lineWidth=2;ctx.fill();ctx.stroke();}} shape(compare,'rgba(80,170,100,.95)','rgba(80,170,100,.12)'); shape(selected,'rgba(60,110,220,.95)','rgba(60,110,220,.12)');}}function renderRanking(){{const t=parseFloat(document.getElementById('atlas-threshold').value);document.getElementById('atlas-threshold-value').textContent=t.toFixed(1);const host=document.getElementById('atlas-ranking');host.innerHTML='';[...ATLAS_DATA].filter(x=>x.overall>=t).sort((a,b)=>b.overall-a.overall).forEach(x=>{{const div=document.createElement('div');div.className='ex-item';div.innerHTML=`<div><div><strong>${{x.component}}</strong></div><div class="ex-mini">QA ${{x.qa.toFixed(1)}} · Ops ${{x.ops.toFixed(1)}} · Runtime ${{x.runtime.toFixed(1)}}</div></div><div><strong>${{x.overall.toFixed(1)}}</strong></div>`;host.appendChild(div);}});}}function renderExplorer(){{const name=document.getElementById('atlas-component').value;const compareName=document.getElementById('atlas-compare').value;const selected=ATLAS_DATA.find(x=>x.component===name);const compare=compareName==='__average__'?ATLAS_AVG:ATLAS_DATA.find(x=>x.component===compareName);document.getElementById('atlas-selected-name').textContent=selected.component;document.getElementById('atlas-selected-overall').textContent=selected.overall.toFixed(1);document.getElementById('atlas-selected-strong').textContent=axisStrong(selected,'desc');document.getElementById('atlas-selected-weak').textContent=axisStrong(selected,'asc');drawRadar(selected,compare);renderRanking();}}fillSelectors();renderExplorer();document.getElementById('atlas-component').addEventListener('change',renderExplorer);document.getElementById('atlas-compare').addEventListener('change',renderExplorer);document.getElementById('atlas-threshold').addEventListener('input',renderExplorer);</script></div>'''


def write_pages(data: list[dict[str, float | str]]) -> None:
    summary = build_summary_adoc(data)
    write(PAGES_DIR / 'quality-atlas' / 'summary.adoc', summary)
    write(PAGES_DIR / 'quality-atlas' / 'index.adoc', f'''= Pre-RC Quality Atlas
:description: Comparative pre-release-candidate component quality atlas for the Smartresponsor ecosystem.

This page describes ecosystem maturity *before release-candidate status and before versioned portfolio dashboards*.

The menu label remains *Quality Atlas* as the umbrella entry point, but the current content is explicitly scoped to the pre-RC development life of the components.

* xref:quality-atlas/explorer.adoc[Open Pre-RC Quality Atlas Explorer]

++++
{build_atlas_html(data)}
++++
''')
    write(PAGES_DIR / 'quality-atlas' / 'explorer.adoc', f'''= Pre-RC Quality Atlas Explorer
:description: Interactive pre-release-candidate explorer for the Smartresponsor component quality atlas.

This is the more interactive companion to the current pre-RC atlas layer.

* xref:quality-atlas/index.adoc[Back to Pre-RC Quality Atlas]

++++
{build_explorer_html(data)}
++++
''')


def patch_nav() -> None:
    nav = NAV_FILE.read_text(encoding='utf-8') if NAV_FILE.exists() else '* xref:index.adoc[Home]\n'
    line = '* xref:quality-atlas/index.adoc[Quality Atlas]\n'
    if 'xref:quality-atlas/index.adoc[Quality Atlas]' not in nav:
        if '* xref:component/index.adoc[Components]\n' in nav:
            nav = nav.replace('* xref:component/index.adoc[Components]\n', '* xref:component/index.adoc[Components]\n' + line)
        else:
            nav += line
    write(NAV_FILE, nav)


def patch_home(summary_text: str) -> None:
    home = PAGES_DIR / 'index.adoc'
    if not home.exists():
        return
    text = home.read_text(encoding='utf-8')
    atlas_bullet = '* xref:quality-atlas/index.adoc[Quality Atlas] — pre-RC component maturity view, 360° profiles, and ecosystem-level readiness snapshot before versioned portfolio life.\n'
    target = '* xref:component/index.adoc[Components] — entry points for ecosystem components and directions.\n'
    if 'xref:quality-atlas/index.adoc[Quality Atlas]' not in text and target in text:
        text = text.replace(target, target + atlas_bullet)
    section = '\n== Pre-RC Quality Atlas\n\nThe current quality layer describes the ecosystem before release-candidate maturity and before versioned portfolio dashboards.\n\n' + summary_text + '\n'
    if '== Pre-RC Quality Atlas\n' not in text:
        if '== Selected Reads\n' in text:
            text = text.replace('== Selected Reads\n', section + '\n== Selected Reads\n')
        else:
            text += section
    write(home, text)


def main() -> None:
    data = load_dataset()
    if not data:
        return
    write_pages(data)
    patch_nav()
    summary_text = (PAGES_DIR / 'quality-atlas' / 'summary.adoc').read_text(encoding='utf-8')
    patch_home(summary_text)
    write(PAGES_DIR / 'quality-atlas' / 'dataset.json', json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
