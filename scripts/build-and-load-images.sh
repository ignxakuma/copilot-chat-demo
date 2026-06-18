#!/usr/bin/env bash
# Purpose: Build all service images and load them into the Kind cluster nodes.
set -euo pipefail

# Detect Docker server architecture so the correct Linux wheel platform is downloaded.
DOCKER_ARCH="$(docker version -f '{{.Server.Arch}}')"

# Map Docker architecture to pip's manylinux platform tags.
if [[ "${DOCKER_ARCH}" == "arm64" || "${DOCKER_ARCH}" == "aarch64" ]]; then
  PIP_PLATFORM="manylinux2014_aarch64"
  COPILOT_SDK_PLATFORM="manylinux_2_28_aarch64"
elif [[ "${DOCKER_ARCH}" == "amd64" || "${DOCKER_ARCH}" == "x86_64" ]]; then
  PIP_PLATFORM="manylinux2014_x86_64"
  COPILOT_SDK_PLATFORM="manylinux_2_28_x86_64"
else
  echo "Unsupported Docker architecture: ${DOCKER_ARCH}" >&2
  exit 1
fi

# Define Python services that install dependencies from a local wheelhouse.
PYTHON_SERVICES=("api-gateway" "user-service" "product-service" "order-service" "aiops-service" "copilot-chat-service")

# Prepare and refresh wheels for each Python service before docker builds.
for service in "${PYTHON_SERVICES[@]}"; do
  # Create local wheel folder so pip install in Docker can run offline.
  mkdir -p "./services/${service}/wheels"

  # aiops-service keeps vendored Copilot SDK wheels that are not resolvable from index anymore.
  if [[ "${service}" == "aiops-service" ]]; then
    if ! ls "./services/${service}/wheels"/github_copilot_sdk-0.1.25-*.whl >/dev/null 2>&1; then
      echo "Missing vendored github_copilot_sdk-0.1.25 wheel(s) for ${service}." >&2
      exit 1
    fi
    # Ensure transitive runtime wheels required by vendored Copilot SDK are present.
    if ! ls "./services/${service}/wheels"/python_dateutil-2.9.0.post0-*.whl >/dev/null 2>&1; then
      python3 -m pip download \
        --only-binary=:all: \
        --platform "${PIP_PLATFORM}" \
        --implementation cp \
        --python-version 3.12 \
        --abi cp312 \
        python-dateutil==2.9.0.post0 six==1.17.0 httpx==0.28.1 httpcore==1.0.9 anyio==4.13.0 idna==3.18 certifi==2026.5.20 exceptiongroup==1.3.1 \
        -d "./services/${service}/wheels"
    fi
    echo "Using vendored wheels for ${service}"
    continue
  fi

  # Remove old wheels to avoid accidental architecture/version mismatches.
  rm -f "./services/${service}/wheels"/*

  # copilot-chat-service requires mixed wheel platforms:
  # dependencies from manylinux2014 + SDK wheel from manylinux_2_28.
  if [[ "${service}" == "copilot-chat-service" ]]; then
    python3 -m pip download \
      --only-binary=:all: \
      --platform "${PIP_PLATFORM}" \
      --implementation cp \
      --python-version 3.12 \
      --abi cp312 \
      --requirement <(grep -v '^github-copilot-sdk==' "./services/${service}/requirements.txt") \
      -d "./services/${service}/wheels"

    python3 -m pip download \
      --no-deps \
      --only-binary=:all: \
      --platform "${COPILOT_SDK_PLATFORM}" \
      --implementation cp \
      --python-version 3.12 \
      --abi cp312 \
      github-copilot-sdk==1.0.1 \
      -d "./services/${service}/wheels"
    continue
  fi

  # Download Linux-compatible wheels for the service based on Docker architecture.
  python3 -m pip download \
    --only-binary=:all: \
    --platform "${PIP_PLATFORM}" \
    --implementation cp \
    --python-version 3.12 \
    --abi cp312 \
    -r "./services/${service}/requirements.txt" \
    -d "./services/${service}/wheels"
done

# Define every service directory and image name in one place.
SERVICES=("api-gateway" "user-service" "product-service" "order-service" "aiops-service" "copilot-chat-service" "web-frontend")

for service in "${SERVICES[@]}"; do
  # Build the Docker image for the current microservice.
  docker build -t "local/${service}:0.1.0" "./services/${service}"

  # Load the image into Kind so Kubernetes can run it without external registry pulls.
  kind load docker-image "local/${service}:0.1.0" --name retail-aiops
done
