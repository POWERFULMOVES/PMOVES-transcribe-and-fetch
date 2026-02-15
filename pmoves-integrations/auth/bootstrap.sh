#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_LOCAL="${ROOT}/.env.local"

mkdir -p "$(dirname "${ENV_LOCAL}")"
touch "${ENV_LOCAL}"

ensure_kv() {
  local key="$1"
  local value="$2"
  if grep -qE "^${key}=" "${ENV_LOCAL}"; then
    return 0
  fi
  printf '%s=%s\n' "${key}" "${value}" >> "${ENV_LOCAL}"
}

ensure_kv "DOCKED_MODE" "true"
ensure_kv "DB_BACKEND" "supabase"
ensure_kv "AGENT_ZERO_MCP_ENABLED" "true"
ensure_kv "SUPABASE_DUAL_WRITE" "true"
ensure_kv "SUPABASE_URL" "http://host.docker.internal:65421"
ensure_kv "SUPA_REST_URL" "http://host.docker.internal:65421/rest/v1"
ensure_kv "ARCHON_URL" "http://archon-server:8051"
ensure_kv "HIRAG_URL" "http://hi-rag-gateway-v2-cpu:8086"
ensure_kv "HIRAG_GPU_URL" "http://hi-rag-gateway-v2-gpu:8086"
ensure_kv "NEO4J_URI" "bolt://neo4j:7687"
ensure_kv "NATS_URL" "nats://nats:4222"

echo "Bootstrap complete: ${ENV_LOCAL}"
