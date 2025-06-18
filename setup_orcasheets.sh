#!/bin/bash

# OrcaSheets Computer Use Framework Setup Script

set -e

echo "🚀 Setting up OrcaSheets Computer Use Framework..."

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This framework is designed for macOS only."
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.12"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.12 or higher is required. Found: Python $python_version"
    echo "Please install Python 3.12+ and try again."
    exit 1
fi

echo "✅ Python version check passed: Python $python_version"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Error: Homebrew is required but not installed."
    echo "Please install Homebrew from https://brew.sh/ and try again."
    exit 1
fi

echo "✅ Homebrew found"

# Install cliclick if not already installed
if ! command -v cliclick &> /dev/null; then
    echo "📦 Installing cliclick for mouse/keyboard automation..."
    brew install cliclick
else
    echo "✅ cliclick is already installed"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "📦 Installing Python dependencies..."
if [ -f "requirements_orcasheets.txt" ]; then
    pip install -r requirements_orcasheets.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    # Also install OrcaSheets specific dependencies
    pip install streamlit anthropic
else
    echo "⚠️ requirements file not found. Installing basic dependencies..."
    pip install streamlit anthropic
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env configuration file..."
    cat > .env << EOF
# OrcaSheets Framework Configuration
API_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key_here

# OrcaSheets Settings
ORCASHEETS_DEFAULT_PROJECT=Default Project
DOWNLOADS_FOLDER=~/Downloads

# UI Automation Settings
SCREENSHOT_DELAY=1.0
CLICK_DELAY=0.5
TYPING_DELAY=0.1
WINDOW_TIMEOUT=10.0

# Display Settings (for screenshots)
WIDTH=1024
HEIGHT=768
DISPLAY_NUM=1
EOF
    
    echo "⚠️ Please edit .env file and add your Anthropic API key"
    echo "   You can get an API key from: https://console.anthropic.com/"
fi

# Check macOS accessibility permissions
echo "🔐 Checking macOS permissions..."
echo "📋 For the framework to work properly, you may need to grant accessibility permissions:"
echo "   1. Go to System Preferences > Security & Privacy > Privacy"
echo "   2. Select 'Accessibility' from the left panel"
echo "   3. Click the lock to make changes"
echo "   4. Add Terminal (or your terminal app) to the list"
echo "   5. Add Python to the list if prompted"

# Create a simple test script
echo "🧪 Creating test script..."
cat > test_orcasheets.py << 'EOF'
#!/usr/bin/env python3
"""
Simple test script for OrcaSheets framework.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orcasheets_main import OrcaSheetsAutomation

def test_framework():
    """Test the OrcaSheets framework."""
    print("🧪 Testing OrcaSheets Framework...")
    
    automation = OrcaSheetsAutomation()
    
    # Test valid commands
    test_commands = [
        "open orcasheets",
        "open orcasheets and upload test.csv from downloads",
        "upload data.xlsx from documents project TestProject"
    ]
    
    # Test invalid commands (should be blocked)
    blocked_commands = [
        "open chrome",
        "browse the internet", 
        "send an email"
    ]
    
    print("\n✅ Testing valid commands:")
    for command in test_commands:
        print(f"  Command: {command}")
        result = automation.process_request(command)
        if result['success'] or 'file not found' in result.get('error', '').lower():
            print(f"  ✅ Accepted (validation passed)")
        else:
            print(f"  ❌ Rejected: {result.get('error')}")
    
    print("\n🚫 Testing blocked commands:")
    for command in blocked_commands:
        print(f"  Command: {command}")
        result = automation.process_request(command)
        if not result['success']:
            print(f"  ✅ Correctly blocked: {result.get('error')}")
        else:
            print(f"  ❌ Incorrectly allowed!")
    
    print("\n🎉 Framework test completed!")

if __name__ == "__main__":
    test_framework()
EOF

chmod +x test_orcasheets.py

# Create launch script for Streamlit
echo "🖥️ Creating launch script..."
cat > launch_orcasheets.sh << 'EOF'
#!/bin/bash

# Launch OrcaSheets Computer Use Framework

echo "🚀 Starting OrcaSheets Computer Use Framework..."

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists and has API key
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please run setup_orcasheets.sh first."
    exit 1
fi

# Check if API key is configured
if grep -q "your_api_key_here" .env; then
    echo "⚠️ Warning: Please configure your Anthropic API key in .env file"
    echo "   Edit .env and replace 'your_api_key_here' with your actual API key"
    exit 1
fi

# Launch Streamlit interface
echo "🌐 Starting web interface at http://localhost:8501"
streamlit run orcasheets_streamlit.py
EOF

chmod +x launch_orcasheets.sh

echo ""
echo "🎉 OrcaSheets Computer Use Framework setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your Anthropic API key"
echo "2. Test basic framework: python3 test_framework_basic.py"
echo "3. Test environment loading: python3 test_env_loading.py"
echo "4. Launch the web interface: ./launch_orcasheets.sh"
echo "   Or manually: streamlit run orcasheets_streamlit.py"
echo ""
echo "📚 Documentation: README_ORCASHEETS.md"
echo "🔧 Configuration: .env file"
echo ""
echo "⚠️ Important: Make sure to grant accessibility permissions in macOS System Preferences"
echo "   if prompted when running the framework."

# Run basic tests
echo ""
echo "🧪 Running basic framework test..."
if python3 test_framework_basic.py; then
    echo "✅ Basic framework test passed!"
else
    echo "❌ Basic framework test failed. Please check the errors above."
fi