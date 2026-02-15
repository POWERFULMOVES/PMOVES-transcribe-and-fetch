#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


DEFAULTS: dict[str, str] = {
    "DOCKED_MODE": "true",
    "DB_BACKEND": "supabase",
    "SUPABASE_DUAL_WRITE": "true",
    "AGENT_ZERO_MCP_ENABLED": "true",
    "SUPABASE_URL": "http://host.docker.internal:65421",
    "SUPA_REST_URL": "http://host.docker.internal:65421/rest/v1",
    "ARCHON_URL": "http://archon-server:8051",
    "HIRAG_URL": "http://hi-rag-gateway-v2-cpu:8086",
    "HIRAG_GPU_URL": "http://hi-rag-gateway-v2-gpu:8086",
    "NEO4J_URI": "bolt://neo4j:7687",
    "NATS_URL": "nats://nats:4222",
}


def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    env_local = root / ".env.local"
    env_local.parent.mkdir(parents=True, exist_ok=True)

    lines = _read_lines(env_local)
    existing_keys = {
        line.split("=", 1)[0].strip()
        for line in lines
        if line and not line.lstrip().startswith("#") and "=" in line
    }

    missing = [(k, v) for k, v in DEFAULTS.items() if k not in existing_keys]
    if missing:
        if lines and lines[-1].strip() != "":
            lines.append("")
        for key, value in missing:
            lines.append(f"{key}={value}")

    env_local.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Bootstrap complete: {env_local}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
