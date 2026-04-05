#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
SYNC_DIR = ROOT / '.sync' / 'quality-atlas'
COMPONENTS_DIR = SYNC_DIR / 'components'
PAGES_DIR = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'pages'
QUALITY_DIR = PAGES_DIR / 'quality-atlas'
NAV_FILE = ROOT / '.antora-src' / 'modules' / 'ROOT' / 'nav.adoc'
HOME_FILE = PAGES_DIR / 'index.adoc'
GENERATED_DIR = SYNC_DIR / 'generated'
VIEW_PROFILES_FILE = SYNC_DIR / 'contract' / 'view-profiles.yaml'


def ensure(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str) -> None:
    ensure(path.parent)
    path.write_text(content.rstrip() + '\n', encoding='utf-8')


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def load_components() -> list[dict]:
    out = []
    for current in sorted(COMPONENTS_DIR.glob('*/current.yaml')):
        out.append(load_yaml(current))
    return out


def load_profiles() -> list[dict]:
    return load_yaml(VIEW_PROFILES_FILE)['profiles']


def average(values: list[float]) -> float:
    return round(sum(values) / len(values), 2) if values else 0.0


def build_payload() -> dict:
    components = load_components()
    profiles = load_profiles()
    payload = {'profiles': [], 'components': [], 'history': {}}
    for comp in components:
        payload['components'].append({
            'component': comp['component'],
            'title': comp['title'],
            'snapshot': comp['snapshot'],
            'profile_axes': comp['profile_axes'],
            'overall': float(comp['metrics']['overall']['score']),
            'strengths': comp['strengths'],
            'risks': comp['risks'],
        })
        history_files = sorted((COMPONENTS_DIR / comp['component'] / 'history').glob('*.yaml'))
        payload['history'][comp['component']] = [load_yaml(path)['snapshot'] | {'overall': float(load_yaml(path)['metrics']['overall']['score'])} for path in history_files]
    for profile in profiles:
        profile_payload = {'id': profile['id'], 'title': profile['title'], 'description': profile['description'], 'axes': [], 'components': []}
        axis_ids = [axis['id'] for axis in profile['axes']]
        for comp in components:
            axes = comp['profile_axes'][profile['id']]
            profile_payload['components'].append({'component': comp['component'], 'title': comp['title'], 'axes': axes, 'overall': average([float(axes[a]) for a in axis_ids if a in axes])})
        for axis in profile['axes']:
            axis_values = [float(item['axes'][axis['id']]) for item in profile_payload['components'] if axis['id'] in item['axes']]
            profile_payload['axes'].append({'id': axis['id'], 'title': axis['title'], 'average': average(axis_values), 'min': round(min(axis_values), 2), 'max': round(max(axis_values), 2)})
        profile_payload['component_count'] = len(profile_payload['components'])
        profile_payload['ecosystem_average'] = average([float(item['overall']) for item in profile_payload['components']])
        payload['profiles'].append(profile_payload)
    return payload


def strongest_axis(profile_payload: dict) -> dict:
    return max(profile_payload['axes'], key=lambda axis: axis['average'])


def weakest_axis(profile_payload: dict) -> dict:
    return min(profile_payload['axes'], key=lambda axis: axis['average'])


def build_html(payload: dict) -> str:
    template = r"""<div class="qa-portfolio"><style>
.qa-portfolio{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#111;}
.qa-grid{display:grid;grid-template-columns:280px 1fr;gap:18px;}
.qa-panel,.qa-main{background:#fff;border:1px solid #d9dde8;border-radius:20px;padding:18px;box-shadow:0 10px 24px rgba(0,0,0,.04);}
.qa-field{display:grid;gap:6px;margin-bottom:14px;}
.qa-field label{font-size:12px;color:#5d6781;text-transform:uppercase;letter-spacing:.04em;}
.qa-field select{padding:10px 12px;border:1px solid #d9dde8;border-radius:12px;background:#fff;}
.qa-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:16px;}
.qa-kpi{border:1px solid #d9dde8;border-radius:16px;padding:14px;background:linear-gradient(180deg,#fff,#fbfcff);}
.qa-kpi .big{font-size:28px;font-weight:800;line-height:1.1;}
.qa-two{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:18px;}
.qa-box{border:1px solid #d9dde8;border-radius:18px;padding:14px;}
.qa-bars{display:grid;gap:10px;}
.qa-bar-row{display:grid;grid-template-columns:140px 1fr 52px;gap:10px;align-items:center;}
.qa-bar{height:10px;border-radius:999px;background:#edf1fb;overflow:hidden;}
.qa-bar > span{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#6d7cff,#7cc8ff);}
.qa-ranking{display:grid;gap:10px;max-height:420px;overflow:auto;padding-right:4px;}
.qa-item{border:1px solid #d9dde8;border-radius:14px;padding:12px;display:grid;grid-template-columns:1fr auto;gap:10px;}
.qa-meta{font-size:12px;color:#66708a;}
.qa-notes{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:16px;}
.qa-note{border:1px solid #d9dde8;border-radius:16px;padding:14px;background:#fcfdff;}
@media (max-width: 1100px){.qa-grid{grid-template-columns:1fr;}.qa-kpis{grid-template-columns:repeat(2,minmax(0,1fr));}.qa-two,.qa-notes{grid-template-columns:1fr;}}
</style>
<div class="qa-grid">
  <div class="qa-panel">
    <h2 style="margin-top:0;">Portfolio Atlas</h2>
    <p style="color:#5d6781;line-height:1.55;">This page reads canonical component snapshots, history, and view profiles. It is the owner-facing, profile-aware portfolio layer that sits above individual component reports.</p>
    <div class="qa-field"><label>View profile</label><select id="qa-profile"></select></div>
    <div class="qa-field"><label>Primary component</label><select id="qa-component"></select></div>
    <div class="qa-field"><label>Compare against</label><select id="qa-compare"></select></div>
    <p style="font-size:12px;color:#66708a;margin-bottom:0;">Contracts live in <code>.sync/quality-atlas/contract</code>. History lives in <code>.sync/quality-atlas/components/*/history</code>.</p>
  </div>
  <div class="qa-main">
    <div class="qa-kpis">
      <div class="qa-kpi"><div>Profile</div><div class="big" id="qa-profile-title"></div></div>
      <div class="qa-kpi"><div>Ecosystem average</div><div class="big" id="qa-ecosystem-average"></div></div>
      <div class="qa-kpi"><div>Strongest axis</div><div id="qa-strong-axis"></div></div>
      <div class="qa-kpi"><div>Weakest axis</div><div id="qa-weak-axis"></div></div>
    </div>
    <div class="qa-two">
      <div class="qa-box"><canvas id="qa-radar" width="720" height="500" style="width:100%;max-width:720px;height:auto"></canvas></div>
      <div class="qa-box"><h3 style="margin-top:0;">Profile axis averages</h3><div class="qa-bars" id="qa-axis-bars"></div></div>
    </div>
    <div class="qa-notes">
      <div class="qa-note"><h3 style="margin-top:0;">Top components</h3><div class="qa-ranking" id="qa-ranking"></div></div>
      <div class="qa-note"><h3 style="margin-top:0;">Selected component</h3><div id="qa-selected-summary" style="line-height:1.6;color:#374056"></div></div>
    </div>
  </div>
</div>
<script>
const QA_PAYLOAD = __PAYLOAD__;
const profileSelect = document.getElementById('qa-profile');
const componentSelect = document.getElementById('qa-component');
const compareSelect = document.getElementById('qa-compare');
function fillProfiles(){QA_PAYLOAD.profiles.forEach((profile, index)=>{const opt=document.createElement('option');opt.value=profile.id;opt.textContent=profile.title;profileSelect.appendChild(opt);if(index===0) profileSelect.value=profile.id;});}
function currentProfile(){return QA_PAYLOAD.profiles.find(p=>p.id===profileSelect.value) || QA_PAYLOAD.profiles[0];}
function refillComponents(){const profile=currentProfile();componentSelect.innerHTML='';compareSelect.innerHTML='';const avg=document.createElement('option');avg.value='__average__';avg.textContent='Profile average';compareSelect.appendChild(avg);profile.components.slice().sort((a,b)=>b.overall-a.overall).forEach((component,index)=>{const opt=document.createElement('option');opt.value=component.component;opt.textContent=component.title;componentSelect.appendChild(opt);const cmp=document.createElement('option');cmp.value=component.component;cmp.textContent=component.title;compareSelect.appendChild(cmp);if(index===0) componentSelect.value=component.component;});compareSelect.value='__average__';}
function selectedComponent(){return currentProfile().components.find(c=>c.component===componentSelect.value) || currentProfile().components[0];}
function selectedCompare(){if(compareSelect.value==='__average__') return null;return currentProfile().components.find(c=>c.component===compareSelect.value) || null;}
function drawRadar(profile, selected, compare){const axes=profile.axes;const canvas=document.getElementById('qa-radar');const ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);const cx=canvas.width*0.42, cy=canvas.height*0.55, radius=Math.min(canvas.width,canvas.height)*0.30, min=6.5, max=9.5;const angle=(i)=>-Math.PI/2+(Math.PI*2*i/axes.length);const point=(value,i)=>{const frac=Math.max(0,Math.min(1,(value-min)/(max-min)));return {x:cx+Math.cos(angle(i))*radius*frac,y:cy+Math.sin(angle(i))*radius*frac};};for(let r=1;r<=4;r++){ctx.beginPath();axes.forEach((axis,i)=>{const x=cx+Math.cos(angle(i))*radius*(r/4);const y=cy+Math.sin(angle(i))*radius*(r/4);if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);});ctx.closePath();ctx.strokeStyle='rgba(173,181,197,.5)';ctx.stroke();}axes.forEach((axis,i)=>{const x=cx+Math.cos(angle(i))*radius;const y=cy+Math.sin(angle(i))*radius;ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(x,y);ctx.strokeStyle='rgba(173,181,197,.5)';ctx.stroke();ctx.fillStyle='#5d6781';ctx.font='12px sans-serif';ctx.textAlign='center';ctx.fillText(axis.title, cx+Math.cos(angle(i))*(radius+32), cy+Math.sin(angle(i))*(radius+32));});const avgShape={axes:{}};axes.forEach(axis=>avgShape.axes[axis.id]=axis.average);function poly(source, stroke, fill){ctx.beginPath();axes.forEach((axis,i)=>{const value=source.axes ? source.axes[axis.id] : source[axis.id];const p=point(value, i);if(i===0)ctx.moveTo(p.x,p.y);else ctx.lineTo(p.x,p.y);});ctx.closePath();ctx.fillStyle=fill;ctx.strokeStyle=stroke;ctx.lineWidth=2;ctx.fill();ctx.stroke();}poly(avgShape,'rgba(23,94,255,.85)','rgba(23,94,255,.10)');if(compare) poly(compare,'rgba(17,151,111,.95)','rgba(17,151,111,.12)');poly(selected,'rgba(17,17,17,.95)','rgba(17,17,17,.08)');}
function render(){const profile=currentProfile();const selected=selectedComponent();const compare=selectedCompare();document.getElementById('qa-profile-title').textContent=profile.title;document.getElementById('qa-ecosystem-average').textContent=profile.ecosystem_average.toFixed(2);const strongest=profile.axes.reduce((a,b)=>a.average>b.average?a:b);const weakest=profile.axes.reduce((a,b)=>a.average<b.average?a:b);document.getElementById('qa-strong-axis').textContent=`${strongest.title} · ${strongest.average.toFixed(2)}`;document.getElementById('qa-weak-axis').textContent=`${weakest.title} · ${weakest.average.toFixed(2)}`;drawRadar(profile, selected, compare);const bars=document.getElementById('qa-axis-bars');bars.innerHTML='';profile.axes.forEach(axis=>{const row=document.createElement('div');row.className='qa-bar-row';row.innerHTML=`<div>${axis.title}</div><div class="qa-bar"><span style="width:${((axis.average-6.5)/3.0)*100}%"></span></div><div>${axis.average.toFixed(2)}</div>`;bars.appendChild(row);});const ranking=document.getElementById('qa-ranking');ranking.innerHTML='';profile.components.slice().sort((a,b)=>b.overall-a.overall).forEach((component)=>{const div=document.createElement('div');div.className='qa-item';div.innerHTML=`<div><strong>${component.title}</strong><div class="qa-meta">${Object.entries(component.axes).slice(0,3).map(([k,v])=>`${k} ${Number(v).toFixed(1)}`).join(' · ')}</div></div><div><strong>${component.overall.toFixed(2)}</strong></div>`;ranking.appendChild(div);});const snapshot=QA_PAYLOAD.components.find(c=>c.component===selected.component);document.getElementById('qa-selected-summary').innerHTML=`<p><strong>${snapshot.title}</strong> · snapshot <code>${snapshot.snapshot.date}</code> / <code>${snapshot.snapshot.label}</code></p><p>${snapshot.strengths.join('<br>')}</p><p style="color:#8a5060">${snapshot.risks.join('<br>')}</p>`;}
fillProfiles();refillComponents();render();profileSelect.addEventListener('change',()=>{refillComponents();render();});componentSelect.addEventListener('change',render);compareSelect.addEventListener('change',render);
</script></div>"""
    return template.replace('__PAYLOAD__', json.dumps(payload, ensure_ascii=False))


def write_portfolio_page(payload: dict) -> None:
    write(QUALITY_DIR / 'portfolio.adoc', f'''= Quality Atlas Portfolio
:description: Portfolio-level Smartresponsor Quality Atlas built from canonical component snapshot contracts.

This page is generated from canonical snapshot contracts stored under `.sync/quality-atlas/components/*`.

* xref:quality-atlas/index.adoc[Back to Quality Atlas]
* xref:quality-atlas/explorer.adoc[Open Pre-RC Explorer]

++++
{build_html(payload)}
++++
''')


def patch_nav() -> None:
    text = NAV_FILE.read_text(encoding='utf-8')
    anchor = '* xref:quality-atlas/index.adoc[Quality Atlas]\n'
    child = '** xref:quality-atlas/portfolio.adoc[Portfolio]\n'
    if child not in text and anchor in text:
        text = text.replace(anchor, anchor + child)
        write(NAV_FILE, text)


def patch_home() -> None:
    text = HOME_FILE.read_text(encoding='utf-8')
    bullet = '* xref:quality-atlas/portfolio.adoc[Portfolio] — profile-aware portfolio view, history-backed snapshots, and owner-facing radar overlays.\n'
    if bullet not in text and '== Pre-RC Quality Atlas\n' in text:
        text = text.replace('== Pre-RC Quality Atlas\n\n', '== Pre-RC Quality Atlas\n\n' + bullet + '\n')
        write(HOME_FILE, text)


def main() -> None:
    payload = build_payload()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    (GENERATED_DIR / 'portfolio-dataset.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    write_portfolio_page(payload)
    patch_nav()
    patch_home()


if __name__ == '__main__':
    main()
