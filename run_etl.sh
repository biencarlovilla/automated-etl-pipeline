#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")" || exit 1

# Create a directory for execution logs
mkdir -p logs

# Run the ETL pipeline and save its output
./.venv/bin/python main.py >> logs/etl.log 2>&1