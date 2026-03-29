# deploy/systemd

Intent
- Bare-metal / VM deployment method without Kubernetes.
- Services are managed by systemd (units/timers), optionally using Docker as a runtime, but NOT required.

What belongs here
- *.service and *.timer unit files
- env templates (example only)
- install scripts and notes

Suggested tree
- unit/
  - my-service.service
  - my-worker.timer
- env/
  - my-service.env.example
- tool/
  - install.sh / install.ps1
- doc/
  - README.md
