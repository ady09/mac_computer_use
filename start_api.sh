#!/bin/bash
# Startup script for OrcaSheets Automation API

echo "Starting OrcaSheets Automation API Server..."
echo "Server will be available at: http://127.0.0.1:8000"
echo "API docs at: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Activate virtual environment and start the API server
cd "$(dirname "$0")"
./venv/bin/python api_server.py