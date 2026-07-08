#!/usr/bin/env bash
# Set shell behavior to exit immediately if non-zero exit code encountered
set -e

# Make sure to start in the /workspace directory of the container
cd /workspace

# Activate venv
if [[ -f ".cvenv/bin/activate" ]]; then
    source .cvenv/bin/activate
else
    echo "ERROR: Could not activate virtual environment at .cvenv/bin/activate"
    exit 1
fi

# Run esgpull install (idempotent, only takes affect the first time it is executed)
if [[ -d "/arctichoke_data" ]]; then
    cd /arctichoke_data
    # Use `|| true` to ensure the following line always returns exit status 0
    #   even if the `esgpull` command fails
    uv run esgpull self install bergybits || true
else
    echo "WARNING: Directory /arctichoke_data not found. No `esgpull` install created."
fi

# Go back and start default CMD
cd /workspace
# Ensure the rest of the CMD in the Containerfile runs
exec "$@"