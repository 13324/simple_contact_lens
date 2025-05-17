#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run both scripts
python "$SCRIPT_DIR/fetch_contacts.py"
python "$SCRIPT_DIR/check_contacts.py"
