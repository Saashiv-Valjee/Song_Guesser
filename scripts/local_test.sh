#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Start Flask proxy (from backend/)
cd "$ROOT_DIR/backend"
python3 proxy.py &

# Serve frontend/index.html from the frontend folder
cd "$ROOT_DIR/frontend"
python3 -m http.server 8000 --bind 0.0.0.0 &

# Wait for user to terminate
echo "Servers running. Press Ctrl+C to stop."
wait
