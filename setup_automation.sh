#!/bin/bash

echo "🚀 Setting up Integrated Test Automation for Claude Desktop..."

# Get the absolute path of mac_computer_use directory
MAC_COMPUTER_USE_PATH="$(cd "$(dirname "$0")" && pwd)"
echo "📁 Working from: $MAC_COMPUTER_USE_PATH"

# Navigate to MCP directory
cd "$MAC_COMPUTER_USE_PATH/../mac_computer_use_mcp"

# Install dependencies
echo "📦 Installing MCP dependencies..."
npm install

# Build TypeScript
echo "🔨 Building TypeScript..."
npm run build

# Check if build was successful
if [ ! -f "dist/index.js" ]; then
    echo "❌ Build failed - index.js not found"
    exit 1
fi

echo "✅ Build successful!"

# Get Claude Desktop config path
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

# Create Claude config directory if it doesn't exist
mkdir -p "$CLAUDE_CONFIG_DIR"

# Backup existing config if it exists
if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    echo "💾 Backing up existing Claude Desktop config..."
    cp "$CLAUDE_CONFIG_FILE" "$CLAUDE_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Get absolute path to MCP server
MCP_SERVER_PATH="$MAC_COMPUTER_USE_PATH/../mac_computer_use_mcp/dist/index.js"

# Create new Claude Desktop config
echo "⚙️ Creating Claude Desktop configuration..."
cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "mac-computer-use": {
      "command": "node",
      "args": ["$MCP_SERVER_PATH"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
EOF

echo "✅ Claude Desktop configuration updated at: $CLAUDE_CONFIG_FILE"

# Install Python dependencies for test automation
echo "📦 Installing Python dependencies..."
cd "$MAC_COMPUTER_USE_PATH"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install pydantic fastapi uvicorn

echo ""
echo "🎉 Integrated Test Automation Setup Complete!"
echo ""
echo "📋 What's Available in Claude Desktop:"
echo ""
echo "🔧 TOOLS:"
echo "   • test_automation - Run any test automation command"
echo "   • spotify_tests - Direct Spotify test execution"
echo "   • computer_use - Direct computer control"
echo "   • orcasheets_automation - OrcaSheets automation"
echo ""
echo "💬 EXAMPLE COMMANDS for Claude Desktop:"
echo '   • "Execute all Spotify tests"'
echo '   • "Run Spotify music playback test"'
echo '   • "Test Spotify playlist creation"'
echo '   • "List available test cases"'
echo ""
echo "📋 NEXT STEPS:"
echo "1. 🚀 Start the API server:"
echo "   cd mac_computer_use && ./start_api_server.sh"
echo ""
echo "2. 🔄 Restart Claude Desktop completely"
echo ""
echo "3. 🎯 Try saying to Claude Desktop:"
echo '   "Execute all Spotify tests"'
echo ""
echo "🔧 Configuration: $CLAUDE_CONFIG_FILE"
echo "📁 Project: $MAC_COMPUTER_USE_PATH"
echo ""
echo "⚠️  IMPORTANT: The API server MUST be running for test automation to work!"
echo ""