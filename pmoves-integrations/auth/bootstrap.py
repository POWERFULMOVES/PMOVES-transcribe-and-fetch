#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


DEFAULTS: dict[str, str] = {
    "DOCKED_MODE": "true",
    "DB_BACKEND": "supabase",
    "SUPABASE_DUAL_WRITE": "true",
    "AGENT_ZERO_MCP_ENABLED": "true",
    "SUPABASE_URL": "http://host.docker.internal:54321",
    "SUPA_REST_URL": "http://host.docker.internal:54321/rest/v1",
    "ARCHON_URL": "http://archon-server:8051",
    "HIRAG_URL": "http://hi-rag-gateway-v2-cpu:8086",
    "HIRAG_GPU_URL": "http://hi-rag-gateway-v2-gpu:8086",
    "NEO4J_URI": "bolt://neo4j:7687",
    "NATS_URL": "nats://nats:pmoves@nats:4222",
}

LEGACY_VALUES: dict[str, str] = {
    "SUPABASE_URL": "http://host.docker.internal:65421",
    "SUPA_REST_URL": "http://host.docker.internal:65421/rest/v1",
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
    index: dict[str, int] = {}
    values: dict[str, str] = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        index[key] = i
        values[key] = value

    changed = False
    for key, value in DEFAULTS.items():
        if key not in index:
            if lines and lines[-1].strip() != "":
                lines.append("")
            lines.append(f"{key}={value}")
            index[key] = len(lines) - 1
            values[key] = value
            changed = True
            continue
        legacy_value = LEGACY_VALUES.get(key)
        if legacy_value and values.get(key) == legacy_value and values.get(key) != value:
            lines[index[key]] = f"{key}={value}"
            changed = True

    env_local.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Bootstrap complete: {env_local} ({'updated' if changed else 'no changes'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
