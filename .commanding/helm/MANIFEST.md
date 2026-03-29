# deploy/helm

Intent
- Kubernetes deployment method using Helm charts.
- This is the preferred path for production-like environments.

What belongs here
- chart(s) for SmartResponsor services
- values files per environment (dev/stage/prod)
- ingress, configmap, secret templates (secrets are injected, not committed)
- upgrade/rollback notes

Suggested tree
- chart/
  - Chart.yaml
  - values.yaml
  - templates/
- values/
  - values-dev.yaml
  - values-stage.yaml
  - values-prod.yaml
- doc/
  - upgrade.md
  - rollback.md
