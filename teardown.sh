#!/usr/bin/env bash
# Purpose: Remove the local Kind cluster and all project resources.
set -euo pipefail

# Delete the Kind cluster created for this project.
kind delete cluster --name retail-aiops
