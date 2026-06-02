#!/bin/bash
# =========================================================
# SRE Monitor - Daemon Startup Script
# =========================================================
# This script initializes the environment and starts the 
# continuous schedule-based daemon.

# Resolve absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/monitor:${PYTHONPATH}"

cd "${PROJECT_ROOT}"

echo "Starting SRE Health Monitor in Daemon Mode..."
python3 monitor/main.py