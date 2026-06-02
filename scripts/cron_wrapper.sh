#!/bin/bash
# =========================================================
# SRE Monitor - Cron Deployment Wrapper
# =========================================================
# This script is designed to be triggered by Linux crontab.
# Example crontab entry (* * * * * /path/to/cron_wrapper.sh)

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/monitor:${PYTHONPATH}"

cd "${PROJECT_ROOT}"

# Run with the --cron flag to execute a single pass and exit
python3 monitor/main.py --cron