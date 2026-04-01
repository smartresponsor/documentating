# Legacy migration matrix

Branch: `wave/antora-cleanup-mobile-nav`

This matrix defines how legacy artifacts in `smartresponsor/documentating` should be handled during the Antora-first cleanup.

| Legacy class | Definition | Default action | Target layer |
|---|---|---|---|
| publishable doc | A document that is already suitable for publication or can be made publishable with light normalization | keep or normalize | `docs/` -> Antora publication flow |
| source-for-doc | Early source material that should not be published raw but contains valuable content | convert / re-home | `docs/` in canonical ADoc flow |
| code/tooling | Scripts, generators, transforms, helpers, build tools, schemas | keep and relocate if needed | tooling/build layer, not public article stream |
| build legacy | Obsolete build contour or superseded publication machinery | delete after confirmation | remove from repo if no longer canonical |
| duplicate/noise | Redundant copies, trigger leftovers, broken drafts, dead artifacts | delete | remove from repo |

## Rules

1. Legacy is not equal to trash.
2. Nothing with source value should be deleted before destination is named.
3. Antora is the single publication canon for this repository.
4. MkDocs/Material remnants are treated as build legacy unless they still hold unique source value.
5. Mobile navigation fixes belong to the Antora supplemental UI layer, not to legacy migration.

## Known examples in this wave

### `README.md`
- Class: repository narrative drift
- Action: rewrite
- Target: Antora-first repository description

### `.site/mkdocs.yml`
- Class: build legacy
- Action: delete
- Target: none; superseded by Antora playbook/workflow

### `supplemental-ui/css/owner-overrides.css`
- Class: active runtime UI override, not legacy
- Action: patch carefully
- Target: keep in supplemental Antora UI layer

### Early article sources under `docs/`
- Class: publishable doc or source-for-doc depending on quality
- Action: preserve, normalize, convert where needed
- Target: canonical ADoc/Antora article flow
