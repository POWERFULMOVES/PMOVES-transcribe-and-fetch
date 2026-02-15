# PMOVES-transcribe-and-fetch Integration Operations

## Objective

Operate this submodule in PMOVES docked/hardened mode with contract checks.

## Boot Sequence

1. `make integration-bootstrap`
2. `make config`
3. `make config-hardened`
4. `make build`
5. `make integration-contract-check`
6. `make integration-submodule-check`
7. `make up-dual-write`
8. `make health`

## Contract and Audit Gates

```bash
make integration-contract-check
make integration-submodule-check
make integration-sitrep
make integration-audit
```

## Archon and HiRAG Notes

- Archon mapping is present in `.gitmodules` and seeded via `ARCHON_URL`.
- HiRAG CPU/GPU endpoints are seeded in bootstrap and compose overlay.
- Neo4j endpoint is seeded via `NEO4J_URI`.
- This legacy iteration still needs endpoint consumption hardening in backend
  logic; integration contract now provides canonical runtime keys.

## Security/Hardening Notes

- Use `docker-compose.hardened.yml` for hardened runtime.
- Keep secrets out of tracked env files.
- Prefer root PMOVES secret funnels and CHIT manifest sync for production.
