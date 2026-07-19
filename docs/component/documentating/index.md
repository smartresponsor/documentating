# Documentating

Documentating is the public documentation portal and publication pipeline for the Smart Responsor ecosystem.

## Responsibility boundary

Documentating owns:

- canonical Antora source generation from repository documentation;
- public article and component entry-point publication;
- search-index generation through the Antora Lunr extension;
- documentation quality-atlas and QA/RC publication surfaces;
- GitHub Pages build and deployment orchestration;
- factual documentation diagnostics and release gates.

Documentating does not own business entities, Doctrine mappings, CRUD controllers or routes, application navigation, or presentation runtime components. Those responsibilities remain in Objecting, Cruding, Navigating, Viewing, Interfacing, and the relevant business repositories.

## Canonical build

```bash
npm test
npm run build
```

The build generates `.antora-src/` from `docs/` and publishes the rendered site into `.site_build/`.

## Canonical inputs

- Playbook: `antora-playbook.yml`
- Content builder: `tools/build_antora_site.py`
- Component registry: `.sync/manifest/component-list.yml`
- Public content: `docs/`
- Static assets: `assets/`
- Publish workflow: `.github/workflows/gh-pages.yml`
