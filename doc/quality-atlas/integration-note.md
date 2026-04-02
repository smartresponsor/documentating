# Quality Atlas Integration Note

This document explains how to integrate the Quality Atlas into the live Antora site.

## Goal

Expose a pre-RC quality surface:
- navigation entry (Quality Atlas)
- home summary block
- full atlas page

## Minimal integration steps

### 1. Navigation

Add to nav.adoc:

```
* xref:quality-atlas/component-quality-summary.adoc[Quality Atlas]
```

### 2. Home page block

Include content from:

```
doc/quality-atlas/home-quality-atlas-block.adoc
```

### 3. Content location

Move or generate into Antora pages:

```
.antora-src/modules/ROOT/pages/quality-atlas/
```

### 4. Optional next step

Builder reads JSON dataset and generates:
- summary
- radar views
- future HTML dashboard bridge

## Important

This surface represents:

**pre-RC / before v1 quality state**

Not production metrics.
