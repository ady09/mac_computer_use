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

# Test environment loading
echo "🧪 Testing environment and API key..."
if python3 test_env_loading.py > /dev/null 2>&1; then
    echo "✅ Environment test passed"
else
    echo "❌ Environment test failed. Please check your API key configuration."
    echo "   Run: python3 test_env_loading.py for details"
    exit 1
fi

# Check required dependencies
echo "📦 Checking dependencies..."
python3 -c "import anthropic, streamlit; print('✅ Dependencies OK')" || {
    echo "❌ Missing dependencies. Please run: pip install -r requirements_orcasheets.txt"
    exit 1
}

# Check UI automation permissions
echo "🔐 Checking UI automation permissions..."
if python3 -c "
from orcasheets.tools.ui_automation import UIAutomation
from orcasheets.config import OrcaSheetsConfig
ui = UIAutomation(OrcaSheetsConfig())
perms = ui.test_permissions()
if not perms['spotlight']:
    print('❌ Accessibility permissions not granted')
    print('Please run: python3 test_ui_automation.py for setup instructions')
    exit(1)
else:
    print('✅ Permissions OK')
"; then
    echo "✅ UI automation permissions verified"
else
    echo "❌ Permission issues detected. Please check:"
    echo "   1. System Preferences > Security & Privacy > Privacy > Accessibility"
    echo "   2. Add Terminal to the list and enable it"
    echo "   3. Restart Terminal and try again"
    echo "   4. Run: python3 test_ui_automation.py for detailed diagnostics"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Launch Streamlit interface
echo "🌐 Starting web interface at http://localhost:8501"
echo "📝 The interface will open in your default browser"
echo "💡 Use Ctrl+C to stop the server"
echo ""
streamlit run orcasheets_streamlit.py
