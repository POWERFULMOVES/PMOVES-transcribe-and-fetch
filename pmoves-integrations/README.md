# PMOVES-transcribe-and-fetch PMOVES Integration Overlay

This folder is the contractized PMOVES overlay for this submodule.

## Contract Checklist

- [x] Compose overlay present in `compose/`
- [x] Validation tools present in `tools/`
- [x] Model mapping scaffold present in `models/`
- [x] n8n flow staging folder present in `n8n/flows/`
- [x] Event subjects declared in `events/subjects.yaml`
- [x] CHIT/GitHub secret labels declared in `secrets/labels.yaml`
- [x] Idempotent auth bootstrap entrypoint in `auth/bootstrap.sh`
- [x] Operations runbook in `docs/OPERATIONS.md`
- [x] README hook terms:
  - `pmoves-announcer`
  - `tensorzero-gateway`
  - `model-registry`
  - `gpu-orchestrator`

## Integration Focus

- Archon orchestration is active via nested submodule mapping.
- Supabase docked mode is bootstrapped with `SUPABASE_DUAL_WRITE=true`.
- HiRAG, Neo4j, and NATS endpoints are seeded for docked runtime:
  - `HIRAG_URL=http://hi-rag-gateway-v2-cpu:8086`
  - `HIRAG_GPU_URL=http://hi-rag-gateway-v2-gpu:8086`
  - `NEO4J_URI=bolt://neo4j:7687`
  - `NATS_URL=nats://nats:4222`

## Validation

```bash
make integration-contract-check
make integration-submodule-check
make integration-sitrep
make integration-audit
```
