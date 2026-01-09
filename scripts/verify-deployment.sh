#!/usr/bin/env bash
set -e

echo "Deployment preflight checks"

require_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd"
    exit 1
  fi
}

check_file() {
  local path="$1"
  if [ ! -f "$path" ]; then
    echo "Missing required file: $path"
    exit 1
  fi
}

check_env_var() {
  local var="$1"
  if ! grep -Eq "^[[:space:]]*${var}=" .env; then
    echo "Missing .env variable: $var"
    return 1
  fi
  return 0
}

check_port_free() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    if lsof -iTCP -sTCP:LISTEN -P | awk '{print $9}' | grep -q ":${port}$"; then
      echo "Port ${port} is already in use."
      return 1
    fi
    return 0
  fi

  if command -v ss >/dev/null 2>&1; then
    if ss -ltn | awk '{print $4}' | grep -q ":${port}$"; then
      echo "Port ${port} is already in use."
      return 1
    fi
    return 0
  fi

  if command -v netstat >/dev/null 2>&1; then
    if netstat -ltn | awk '{print $4}' | grep -q ":${port}$"; then
      echo "Port ${port} is already in use."
      return 1
    fi
    return 0
  fi

  echo "No port inspection tool found (lsof/ss/netstat)."
  return 1
}

echo "- Checking required commands"
require_command docker
if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose V2 is not available."
  exit 1
fi

echo "- Checking required files"
check_file docker-compose.yml
check_file backend/Dockerfile
check_file frontend/Dockerfile
check_file frontend/nginx.conf
check_file deployment/nginx/semantic-search.conf
check_file .env

echo "- Validating docker-compose.yml"
docker compose config >/dev/null

echo "- Checking .env variables"
required_vars=(
  CORS_ORIGINS
  AUDIO_DIR
  EMBEDDINGS_DIR
  CLAP_DEVICE
  API_HOST
  API_PORT
  VITE_API_BASE_URL
)
missing_vars=0
for var in "${required_vars[@]}"; do
  if ! check_env_var "$var"; then
    missing_vars=1
  fi
done
if [ "$missing_vars" -ne 0 ]; then
  exit 1
fi

echo "- Checking ports"
check_port_free 8000
check_port_free 3000

echo "All preflight checks passed."
