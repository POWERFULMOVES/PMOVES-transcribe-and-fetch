# PMOVES.AI Integration Guide for PMOVES Transcribe-and-Fetch

## Overview

PMOVES-transcribe-and-fetch is integrated as a PMOVES.AI submodule and validated through the parent deterministic gate chain:

- `make -C pmoves submodule-layer-validate-all-strict`
- `make -C pmoves submodule-integrity-strict`
- `make -C pmoves audit-layers-static`

This module provides ingestion, transcription, fetch/crawl workflows, and UI surfaces that connect into PMOVES event and runtime lanes.

## Runtime Integration Points

- **Tiering**: uses PMOVES tiered environment model (`env.shared` + tier overlays).
- **Data**: Supabase-backed flows for operational/stateful paths.
- **Agents/Automation**: n8n and PMOVES agent lanes for orchestration.
- **Media Pipeline**: transcript/fetch paths align with PMOVES.YT and creator ingestion surfaces.

## Local Validation Baseline

### Deterministic parent gate

Run from parent repo root:

```bash
make -C pmoves submodule-layer-validate-one SUBMODULE=PMOVES-transcribe-and-fetch
```

### Submodule-native checks

Run from `PMOVES-transcribe-and-fetch/`:

```bash
npm ci
npm test
```

Current known test debt (captured during 2026-03-03 local replay):

- Jest suites include broken import/mock references and outdated hook testing patterns (`waitForNextUpdate`), causing broad frontend unit test failures.
- Some suites expect test doubles (`mockToast`) that are not defined in setup.

## Nested Submodule Mapping

This repo includes a nested Archon gitlink at `PMOVES-Archon`. The `.gitmodules` mapping in this repository is required so recursive integrity checks can resolve nested submodule metadata.

## Notes

- Keep this file updated when runtime contracts, event subjects, or validation commands change.
- Keep parent `pmoves/docs/NEXT_STEPS.md` and `pmoves/docs/PMOVES.AI PLANS/ROADMAP.md` aligned with any integration-impacting changes.
