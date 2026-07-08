#!/usr/bin/env bash
# This script should be run from the project main directory
set -euo pipefail

# ---- Ensure podman machine is running (macOS) ----
if ! podman machine inspect >/dev/null 2>&1; then
  echo "No podman machine found. Initializing..."
  podman machine init
fi

MACHINE_STATE=$(podman machine inspect --format '{{.State}}')

if [[ "$MACHINE_STATE" != "running" ]]; then
  echo "Starting podman machine..."
  podman machine start
fi

# ---- Set parameters ----
IMAGE="arctichoke"
CONTAINER_NAME="arctichoke_cont"
WORKDIR="/workspace"

# ---- Cleanup old container if it exists ----
podman rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

# ---- Ensure image exists ----
if ! podman image exists "$IMAGE"; then
  echo "Image $IMAGE not found. Building from '.devcontainer/Containerfile'..."
  podman build -f .devcontainer/Containerfile -t "$IMAGE" . | tee .devcontainer/build_container_log.txt
fi

# ---- Setup external hard drive access ----
export SICP_DATA_DIR=/Volumes/BERGY_BITS/arctichoke_data/
SICP_DATA_DIR="${SICP_DATA_DIR:-}"

if [[ -n "$SICP_DATA_DIR" ]]; then
  if [[ ! -d "$SICP_DATA_DIR" ]]; then
    echo "ERROR: SICP_DATA_DIR does not exist: $SICP_DATA_DIR"
    exit 1
  fi
fi

# ---- Build volume args ----
VOLUMES=(-v "$(pwd)":"$WORKDIR")

if [[ -n "$SICP_DATA_DIR" ]]; then
  VOLUMES+=(-v "$SICP_DATA_DIR:/arctichoke_data")
fi

# ---- Run container (Jupyter starts automatically from CMD) ----
podman run -it --rm \
  --name "$CONTAINER_NAME" \
  -p 8889:8888 \
  "${VOLUMES[@]}" \
  -w "$WORKDIR" \
  "$IMAGE"