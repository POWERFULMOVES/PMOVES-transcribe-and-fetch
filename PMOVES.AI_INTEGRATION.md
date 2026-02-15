# PMOVES-transcribe-and-fetch Integration Dossier

## Purpose

This document defines how `PMOVES-transcribe-and-fetch` integrates with the
PMOVES.AI hardened stack and where the remaining gaps are.

## Current Integration Status

### Implemented

- Archon submodule is wired as a nested gitlink:
  - `PMOVES-Archon`
- Supporting nested submodules for agent workflows are mapped:
  - `docs/Seed1.5-VL`
  - `github-mcp-server`
  - `pmoves-ottomator-agents`
- PMOVES hardened deployment modes are present in:
  - `docker-compose.hardened.yml`
  - `AGENTS.md`
- PMOVES integration overlay is present:
  - `pmoves-integrations/`
- Docked bootstrap now seeds Supabase dual-write + service endpoints:
  - `SUPABASE_DUAL_WRITE=true`
  - `ARCHON_URL`
  - `HIRAG_URL`, `HIRAG_GPU_URL`
  - `NEO4J_URI`
  - `NATS_URL`

### Not Yet Implemented (explicit gap)

- Backend runtime logic in this legacy iteration does not yet consume the
  newly-seeded Archon/HiRAG/Neo4j env keys end-to-end.
- No direct `hirag`/`hi-rag` container dependency is declared in this
  submodule's top-level compose (expected in docked PMOVES parent stack).

## Integration Contract Alignment

The submodule now includes a first-class `pmoves-integrations/` overlay:

- `pmoves-integrations/compose/docker-compose.pmoves-net.yml`
- `pmoves-integrations/tools/*` validation helpers
- `pmoves-integrations/events/subjects.yaml`
- `pmoves-integrations/models/mappings/service_model_mappings.json`
- `pmoves-integrations/secrets/labels.yaml`
- `pmoves-integrations/auth/bootstrap.sh`
- `pmoves-integrations/docs/OPERATIONS.md`

Run checks:

```bash
make integration-contract-check
make integration-submodule-check
make integration-sitrep
```

## Archon + HiRAG Plan for This Submodule

1. Keep Archon nested submodule mapping as the orchestration anchor.
2. Add explicit HiRAG routing knobs in env + compose:
   - `HIRAG_URL`
   - `HIRAG_GPU_URL`
3. Add explicit Neo4j routing knob:
   - `NEO4J_URI`
4. Add smoke path for retrieval-assisted transcription/fetch workflow.
5. Gate changes through integration-contract and hardened compose validation.

## Build and Audit Sequence

1. `make config`
2. `make config-hardened`
3. `make build`
4. `make integration-contract-check`
5. `make integration-submodule-check`
6. `make health` (after services are up)

## Notes

- Keep commits atomic: pointer hygiene, contract scaffolding, runtime wiring.
- Root PMOVES.AI should only move this submodule pointer once local checks pass.
