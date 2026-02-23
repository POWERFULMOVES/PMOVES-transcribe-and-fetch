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

replace_legacy_kv() {
  local key="$1"
  local legacy="$2"
  local value="$3"
  if grep -qF "${key}=${legacy}" "${ENV_LOCAL}"; then
    if command -v sed >/dev/null 2>&1; then
      sed -i.bak "s|^${key}=.*$|${key}=${value}|" "${ENV_LOCAL}" && rm -f "${ENV_LOCAL}.bak"
    else
      # fallback for environments without sed -i support
      perl -0pi -e "s/^${key}=.*\$/${key}=${value}/m" "${ENV_LOCAL}"
    fi
  fi
}

ensure_kv "DOCKED_MODE" "true"
ensure_kv "DB_BACKEND" "supabase"
ensure_kv "AGENT_ZERO_MCP_ENABLED" "true"
ensure_kv "SUPABASE_DUAL_WRITE" "true"
ensure_kv "SUPABASE_URL" "http://host.docker.internal:54321"
ensure_kv "SUPA_REST_URL" "http://host.docker.internal:54321/rest/v1"
replace_legacy_kv "SUPABASE_URL" "http://host.docker.internal:65421" "http://host.docker.internal:54321"
replace_legacy_kv "SUPA_REST_URL" "http://host.docker.internal:65421/rest/v1" "http://host.docker.internal:54321/rest/v1"
ensure_kv "ARCHON_URL" "http://archon-server:8051"
ensure_kv "HIRAG_URL" "http://hi-rag-gateway-v2-cpu:8086"
ensure_kv "HIRAG_GPU_URL" "http://hi-rag-gateway-v2-gpu:8086"
ensure_kv "NEO4J_URI" "bolt://neo4j:7687"
ensure_kv "NATS_URL" "nats://nats:pmoves@nats:4222"

echo "Bootstrap complete: ${ENV_LOCAL}"
