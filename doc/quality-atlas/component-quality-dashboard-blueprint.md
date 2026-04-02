# Quality Atlas Dashboard Blueprint

This document defines the structure of the canonical HTML dashboard for the Quality Atlas.

## Purpose

Provide a visual representation of **pre-RC / before v1** component maturity.

Not a production monitoring dashboard.

---

## Layout

### 1. Hero block

- Title: "Quality Atlas"
- Subtitle: "Pre-RC / Before v1 Component Maturity"
- Short description explaining development-stage nature

---

### 2. Top metrics strip

- Average Overall RC
- Number of components
- Top component
- Lowest component

---

### 3. Heatmap table

Columns:

- Component
- Product
- Architecture
- Runtime
- QA
- Ops / Gov / Sec
- Market
- Overall

Cells use gradient coloring:

- 0–5 → red
- 5–7 → orange
- 7–9 → yellow
- 9–10 → green

---

### 4. Radar / Spider charts

- One per top components (Top 5 by overall)
- Axes:
  - Product
  - Architecture
  - Runtime
  - QA
  - Ops
  - Market

---

### 5. Insights block

- Top 3 components
- Strongest dimensions
- Weakest signals

---

### 6. Narrative block

Explicit text:

"This dashboard reflects the state of components before their first release candidate (RC)."

---

## Data binding

Primary source:

```
doc/quality-atlas/component-quality-dataset.json
```

---

## Future evolution

- interactive filters
- timeline (evolution over commits)
- component drill-down

---

## Output

Target file:

```
doc/quality-atlas/component_quality_dashboard.html
```
