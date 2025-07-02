#!/bin/bash

echo "🚀 Starting Test Automation API Server..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "📁 Starting from: $SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Check if required packages are installed
python -c "import fastapi, uvicorn, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required packages..."
    pip install fastapi uvicorn pydantic
fi

echo "✅ Starting API server at http://localhost:8000"
echo "📖 API docs will be available at http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo ""
echo "🎯 Available endpoints:"
echo "   • POST /test/execute - Execute test automation"
echo "   • GET  /test/available - List available tests" 
echo "   • GET  /test/validate - Validate test files"
echo "   • POST /orcasheets/automation - OrcaSheets automation"
echo ""

# Start the API server
cd "$SCRIPT_DIR"
python api_server.py