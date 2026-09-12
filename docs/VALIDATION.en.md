# Validation record

[中文](VALIDATION.md) | **English**

Checks were performed by the Codex AI collaborator, not claimed as personal acceptance testing by the project owner.

## Bilingual update (September 13, 2026)

Six local pytest tests, Ruff, and JavaScript syntax checks passed. A real browser verified the English default, Chinese switching, persistence after reload, bilingual fault explanations, and recovery. Both languages passed the 390px mobile overflow check with no JavaScript errors. Actual screenshots were refreshed in both languages.

## Initial V1 checks

- Windows / Python 3.12.14: six pytest tests passed; Ruff and JavaScript syntax checks passed.
- A separate PyModbus server and client exchanged four registers over real TCP and verified expected ranges and scaling.
- Headless Edge tested a running Uvicorn service: live readings, progressive fault injection, Critical status, and recovery.
- Desktop and 390px mobile layouts were checked; no page-level horizontal overflow or JavaScript errors were observed.
- GitHub Actions passed Python 3.12 and 3.13 on Ubuntu: [initial run](https://github.com/IISophieII/smartplant-monitor/actions/runs/34704636127).

The first pytest attempt encountered an inaccessible system temporary directory. A writable workspace `--basetemp` resolved it without changing assertions. A local Starlette/AnyIO deprecation warning and GitHub Actions Node.js runtime warnings did not fail the checks.

## Limitations

Docker is unavailable locally, so the image and Compose stack have not been executed here. No real PLC, motor, or sensor was connected. No real-world accuracy, false-alarm rate, performance benchmark, or production reliability claim is made.

## Recheck

```sh
pytest -q
ruff check .
```

If the default temporary directory is inaccessible, specify a new writable directory with `--basetemp=./work-test-temp`. Pytest manages this directory; do not point it at important existing files.
