Owner Gate (Canonization / owner / Gate)

This repository is the executable Owner Canon Gate.
- policy/ = source of truth
- linting/ = enforcement tools (js/ps1/sh)
- gate.ps1, gate.sh = entrypoints
- .github/workflows/gate.yml = CI gate

Local:
  bash gate.sh .
  pwsh ./gate.ps1 -Path .

CI:
  pull_request + push master
