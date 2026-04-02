#!/usr/bin/env python3
from __future__ import annotations

"""Generate canonical Quality Atlas HTML dashboard from JSON dataset."""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / 'doc' / 'quality-atlas' / 'component-quality-dataset.json'
OUTPUT = ROOT / 'doc' / 'quality-atlas' / 'component_quality_dashboard.html'
AXES = [
    ('product', 'Product'),
    ('architecture', 'Architecture'),
    ('runtime', 'Runtime'),
    ('qa', 'QA'),
    ('ops', 'Ops / Gov / Sec'),
    ('market', 'Market'),
]


def load() -> list[dict]:
    return json.loads(DATASET.read_text(encoding='utf-8'))


def avg(rows: list[dict], key: str) -> float:
    return sum(float(row[key]) for row in rows) / len(rows)


def heat_color(value: float) -> str:
    if value >= 9:
        return '#2e7d32'
    if value >= 7:
        return '#c0a000'
    if value >= 5:
        return '#ef6c00'
    return '#c62828'


def radar_svg(row: dict, size: int = 220) -> str:
    cx = cy = size / 2
    radius = size * 0.34
    count = len(AXES)
    points = []
    grid = []
    labels = []
    for level in (0.25, 0.5, 0.75, 1.0):
        ring = []
        for i, (_, label) in enumerate(AXES):
            angle = -math.pi / 2 + (2 * math.pi * i / count)
            x = cx + math.cos(angle) * radius * level
            y = cy + math.sin(angle) * radius * level
            ring.append(f'{x:.1f},{y:.1f}')
        grid.append(f'<polygon points="{' '.join(ring)}" fill="none" stroke="#d0d7de" stroke-width="1" />')
    for i, (key, label) in enumerate(AXES):
        angle = -math.pi / 2 + (2 * math.pi * i / count)
        vx = cx + math.cos(angle) * radius
        vy = cy + math.sin(angle) * radius
        px = cx + math.cos(angle) * radius * (float(row[key]) / 10.0)
        py = cy + math.sin(angle) * radius * (float(row[key]) / 10.0)
        points.append(f'{px:.1f},{py:.1f}')
        lx = cx + math.cos(angle) * (radius + 22)
        ly = cy + math.sin(angle) * (radius + 22)
        labels.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" font-size="10" fill="#444">{label}</text>')
        labels.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{vx:.1f}" y2="{vy:.1f}" stroke="#d0d7de" stroke-width="1" />')
    poly = f'<polygon points="{' '.join(points)}" fill="rgba(31,111,235,0.25)" stroke="#1f6feb" stroke-width="2" />'
    return f'<svg viewBox="0 0 {size} {size}" class="radar">{"".join(grid)}{"".join(labels)}{poly}</svg>'


def build() -> str:
    rows = load()
    top = sorted(rows, key=lambda r: float(r['overall']), reverse=True)
    top5 = top[:5]
    avg_overall = avg(rows, 'overall')
    strongest_dims = sorted(((label, avg(rows, key)) for key, label in AXES), key=lambda item: item[1], reverse=True)
    weakest_dims = sorted(((label, avg(rows, key)) for key, label in AXES), key=lambda item: item[1])

    metrics = f'''
    <section class="metrics">
      <div class="metric"><span class="metric-label">Components</span><span class="metric-value">{len(rows)}</span></div>
      <div class="metric"><span class="metric-label">Average Overall RC</span><span class="metric-value">{avg_overall:.2f}</span></div>
      <div class="metric"><span class="metric-label">Top Component</span><span class="metric-value">{top[0]['component']}</span></div>
      <div class="metric"><span class="metric-label">Lowest Component</span><span class="metric-value">{top[-1]['component']}</span></div>
    </section>
    '''

    header_cells = ''.join(f'<th>{label}</th>' for _, label in AXES) + '<th>Overall RC</th>'
    body_rows = []
    for row in top:
        cells = [f'<td class="component">{row["component"]}</td>']
        for key, _label in AXES:
            val = float(row[key])
            cells.append(f'<td style="background:{heat_color(val)}20;border-left:4px solid {heat_color(val)}">{val:.1f}</td>')
        overall = float(row['overall'])
        cells.append(f'<td style="background:{heat_color(overall)}20;border-left:4px solid {heat_color(overall)}"><strong>{overall:.1f}</strong></td>')
        body_rows.append('<tr>' + ''.join(cells) + '</tr>')
    table = f'<section><h2>Component Heatmap</h2><table><thead><tr><th>Component</th>{header_cells}</tr></thead><tbody>{"".join(body_rows)}</tbody></table></section>'

    radar_cards = []
    for row in top5:
        radar_cards.append(f'''<article class="card"><h3>{row['component']} <span>{float(row['overall']):.1f}</span></h3>{radar_svg(row)}</article>''')
    radars = f'<section><h2>Top 5 Radar Profiles</h2><div class="grid">{"".join(radar_cards)}</div></section>'

    insights = f'''
    <section class="insights">
      <div>
        <h2>Top 3 Components</h2>
        <ol>
          <li>{top[0]['component']} — {float(top[0]['overall']):.1f}</li>
          <li>{top[1]['component']} — {float(top[1]['overall']):.1f}</li>
          <li>{top[2]['component']} — {float(top[2]['overall']):.1f}</li>
        </ol>
      </div>
      <div>
        <h2>Strongest Dimensions</h2>
        <ol>
          <li>{strongest_dims[0][0]} — {strongest_dims[0][1]:.2f}</li>
          <li>{strongest_dims[1][0]} — {strongest_dims[1][1]:.2f}</li>
          <li>{strongest_dims[2][0]} — {strongest_dims[2][1]:.2f}</li>
        </ol>
      </div>
      <div>
        <h2>Weakest Signals</h2>
        <ol>
          <li>{weakest_dims[0][0]} — {weakest_dims[0][1]:.2f}</li>
          <li>{weakest_dims[1][0]} — {weakest_dims[1][1]:.2f}</li>
          <li>{top[-1]['component']} overall — {float(top[-1]['overall']):.1f}</li>
        </ol>
      </div>
    </section>
    '''

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Quality Atlas — Pre-RC Component Maturity</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; background: #f6f8fa; color: #1f2328; }}
    .wrap {{ max-width: 1320px; margin: 0 auto; padding: 32px 20px 56px; }}
    .hero {{ background: linear-gradient(135deg, #0b3d91, #1f6feb); color: white; border-radius: 18px; padding: 28px; box-shadow: 0 12px 28px rgba(0,0,0,.12); }}
    .hero h1 {{ margin: 0 0 10px; font-size: 2rem; }}
    .hero p {{ margin: 0; line-height: 1.6; max-width: 900px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 14px; margin: 24px 0; }}
    .metric {{ background: white; border-radius: 16px; padding: 18px; box-shadow: 0 6px 18px rgba(0,0,0,.06); }}
    .metric-label {{ display:block; color:#57606a; font-size:.9rem; margin-bottom:8px; }}
    .metric-value {{ font-size:1.5rem; font-weight:700; }}
    section {{ margin-top: 28px; }}
    section h2 {{ margin: 0 0 14px; font-size: 1.25rem; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 6px 18px rgba(0,0,0,.06); }}
    th, td {{ padding: 12px 10px; border-bottom: 1px solid #eaeef2; text-align: center; }}
    th {{ background: #f0f4f8; font-size: .92rem; }}
    td.component {{ text-align:left; font-weight:600; white-space:nowrap; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }}
    .card {{ background: white; border-radius: 18px; padding: 16px; box-shadow: 0 6px 18px rgba(0,0,0,.06); }}
    .card h3 {{ display:flex; justify-content:space-between; margin:0 0 10px; font-size:1rem; }}
    .radar {{ width: 100%; height: auto; }}
    .insights {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(240px,1fr)); gap:16px; }}
    .insights > div {{ background:white; border-radius:18px; padding:18px; box-shadow:0 6px 18px rgba(0,0,0,.06); }}
    .footnote {{ margin-top: 28px; color:#57606a; line-height:1.6; }}
    @media (max-width: 900px) {{ .metrics {{ grid-template-columns: repeat(2, minmax(0,1fr)); }} }}
    @media (max-width: 560px) {{ .metrics {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <h1>Quality Atlas</h1>
      <p>Pre-RC / before v1 maturity surface for Smartresponsor components. This is not a production SLA dashboard. It is a development-stage quality map showing structure, readiness, and unevenness before first release candidate.</p>
    </header>
    {metrics}
    {table}
    {radars}
    {insights}
    <p class="footnote">This dashboard reflects component life before RC. It should be read as maturity shape, not as post-release observability or final production quality.</p>
  </div>
</body>
</html>
'''


def main() -> None:
    OUTPUT.write_text(build(), encoding='utf-8')


if __name__ == '__main__':
    main()
