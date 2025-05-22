#!/bin/bash

# Start Flask proxy
python3 ./proxy.py &

# Start HTTP server
python3 -m http.server 8000 --bind 0.0.0.0 &

# Optional: wait for user to Ctrl+C
echo "Servers running. Press Ctrl+C to stop."
wait
