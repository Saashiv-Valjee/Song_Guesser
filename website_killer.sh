# Kill whatever is running on port 8000 (your HTTP server)
lsof -ti :8000 | xargs kill

# Kill whatever is running on port 5000 (your Flask proxy)
lsof -ti :5000 | xargs kill
