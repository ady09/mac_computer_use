# 🔧 OrcaSheets Framework Troubleshooting Guide

## Common Issues and Solutions

### 1. Tool Definition Error (Error 400)

**Error**: `tools.0: Input tag 'function' found using 'type' does not match any of the expected tags`

**Solution**: ✅ Fixed! The tool definition now uses `"type": "custom"` and `"input_schema"` instead of `"parameters"`.

### 2. API Key Issues

#### Missing API Key
**Error**: `Anthropic API key not found`

**Solution**:
1. Create/edit `.env` file in the project root
2. Add your API key: `ANTHROPIC_API_KEY=sk-ant-your-key-here`
3. Get your key from: https://console.anthropic.com/

#### Invalid API Key Format
**Error**: `API key loaded but validation failed`

**Solution**:
- Ensure your API key starts with `sk-ant-`
- Check for extra spaces or quotes in `.env` file
- Key should be ~50+ characters long

#### API Key Not Loading
**Error**: API key field empty in Streamlit

**Solution**:
1. Run: `python3 test_env_loading.py` to diagnose
2. Check `.env` file exists and has correct format:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```
3. Install python-dotenv: `pip install python-dotenv`

### 3. Import Errors

#### Missing anthropic module
**Error**: `ModuleNotFoundError: No module named 'anthropic'`

**Solution**:
```bash
pip install -r requirements_orcasheets.txt
# or
pip install anthropic streamlit python-dotenv
```

#### Relative import errors
**Error**: `attempted relative import beyond top-level package`

**Solution**: ✅ Fixed! All imports now use absolute paths with sys.path manipulation.

### 4. Permission Issues

#### Accessibility permissions
**Error**: UI automation not working

**Solution**:
1. Go to System Preferences → Security & Privacy → Privacy
2. Select "Accessibility" from left panel
3. Click lock to make changes
4. Add Terminal (or your terminal app)
5. Add Python if prompted

#### cliclick not found
**Error**: `cliclick: command not found`

**Solution**:
```bash
brew install cliclick
```

### 5. Streamlit Issues

#### Port already in use
**Error**: `Port 8501 is in use`

**Solution**:
```bash
# Kill existing streamlit processes
pkill -f streamlit

# Or use a different port
streamlit run orcasheets_streamlit.py --server.port 8502
```

#### Browser doesn't open
**Issue**: Streamlit starts but browser doesn't open

**Solution**:
- Manually navigate to: http://localhost:8501
- Check terminal output for actual port number

### 6. macOS Specific Issues

#### Spotlight search not working
**Issue**: "open orcasheets" fails

**Solution**:
1. Test Spotlight manually: Cmd+Space, type "orcasheets"
2. Ensure OrcaSheets is installed and indexed by Spotlight
3. Try alternative app names if needed

#### Screenshot capture fails
**Error**: Screenshot automation not working

**Solution**:
1. Grant Screen Recording permissions:
   - System Preferences → Security & Privacy → Privacy
   - Select "Screen Recording"
   - Add Terminal/Python
2. Test manually: `screencapture test.png`

### 7. Framework-Specific Issues

#### Task validation fails
**Error**: `Task validation failed - invalid or unsafe parameters`

**Solution**:
1. Check your command syntax:
   ```
   ✅ "open orcasheets and upload data.csv from downloads"
   ❌ "open chrome and browse internet"
   ```
2. Ensure file paths are in allowed directories (Downloads, Documents, Desktop)
3. Use supported file types: CSV, XLSX, XLS, JSON, TXT

#### File not found errors
**Error**: `File not found: ~/Downloads/data.csv`

**Solution**:
1. Check file actually exists
2. Use exact filename including extension
3. Ensure file is in allowed directory

### 8. Testing and Debugging

#### Run diagnostic tests
```bash
# Test basic framework
python3 test_framework_basic.py

# Test environment loading  
python3 test_env_loading.py

# Test full framework (requires API key)
python3 test_orcasheets.py
```

#### Enable debug mode
Add to your code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check configuration
```python
from orcasheets import OrcaSheetsConfig
config = OrcaSheetsConfig.load_from_env()
print(config)
```

## Setup Verification Checklist

- [ ] macOS Sonoma 15.7+
- [ ] Python 3.12+
- [ ] Homebrew installed
- [ ] cliclick installed (`brew install cliclick`)
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements_orcasheets.txt`)
- [ ] `.env` file exists with valid API key
- [ ] Accessibility permissions granted
- [ ] Screen Recording permissions granted (if needed)
- [ ] Basic tests pass (`python3 test_framework_basic.py`)
- [ ] Environment test passes (`python3 test_env_loading.py`)

## Getting Help

### Error Messages
Always include the full error message when seeking help.

### System Information
```bash
# Check Python version
python3 --version

# Check installed packages
pip list | grep -E "(anthropic|streamlit)"

# Check macOS version
sw_vers
```

### Log Files
Streamlit logs are usually in:
- `~/.streamlit/logs/`

### Common Command Patterns

#### Valid OrcaSheets Commands
```python
"open orcasheets"
"open orcasheets and upload industry.csv from downloads"
"upload data.xlsx from documents project MyProject"
"select project TestProject"
"add new sheet"
```

#### Invalid Commands (Will be blocked)
```python
"open chrome"
"browse the internet"
"send an email"
"install software"
"delete files"
```

### Quick Reset
If everything is broken:
```bash
# Clean reset
rm -rf venv/
rm .env
./setup_orcasheets.sh
# Re-add your API key to .env
```

## Performance Tips

1. **Reduce screenshot delay** in config for faster automation
2. **Use specific project names** to avoid search time
3. **Keep file names simple** (no spaces or special characters)
4. **Close unnecessary apps** to reduce UI complexity

## Still Having Issues?

1. Check that your request is OrcaSheets-related
2. Verify file paths and extensions
3. Test with simple commands first ("open orcasheets")
4. Check system permissions
5. Review logs for specific error messages

The framework is designed to be restrictive for security - if something doesn't work, it's likely by design to prevent unsafe operations.