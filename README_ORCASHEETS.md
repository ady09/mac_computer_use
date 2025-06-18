# OrcaSheets Computer Use Framework

A specialized computer use framework designed exclusively for automating OrcaSheets tasks on macOS. This framework provides secure, restricted automation that only allows OrcaSheets-related operations.

## 🔒 Security Features

- **Restricted to OrcaSheets only**: Cannot perform web browsing, system administration, or other non-OrcaSheets tasks
- **File upload restrictions**: Only allows uploads from Downloads, Documents, or Desktop folders
- **Supported file types**: CSV, XLSX, XLS, JSON, TXT only
- **Input validation**: All user requests are validated before execution
- **Safe task parsing**: Built-in protection against malicious commands

## 📁 Project Structure

```
orcasheets/
├── __init__.py              # Package initialization
├── config.py                # Configuration management
├── core.py                  # Main framework class
├── tasks.py                 # Task definitions and validation
└── tools/
    ├── __init__.py          # Tools package
    ├── orcasheets_tool.py   # Main automation tool
    └── ui_automation.py     # UI interaction utilities

orcasheets_main.py           # Main entry point
orcasheets_loop.py           # Modified sampling loop for OrcaSheets
orcasheets_streamlit.py      # Streamlit web interface
```

## 🚀 Quick Start

### Prerequisites

- macOS Sonoma 15.7 or later
- Python 3.12+
- cliclick (`brew install cliclick`)
- Anthropic API key

### Installation

1. **Install cliclick** (required for mouse/keyboard automation):
```bash
brew install cliclick
```

2. **Set up environment variables** (create `.env` file):
```env
API_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key_here
ORCASHEETS_DEFAULT_PROJECT=Default Project
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

### Running the Framework

#### Option 1: Streamlit Web Interface (Recommended)
```bash
streamlit run orcasheets_streamlit.py
```

#### Option 2: Direct Python Usage
```python
from orcasheets_main import OrcaSheetsAutomation

automation = OrcaSheetsAutomation()
result = automation.process_request("open orcasheets and upload industry.csv from downloads")
print(result)
```

## 📊 Supported Operations

### 1. Open OrcaSheets
```
"open orcasheets"
```

### 2. Upload File
```
"upload industry.csv from downloads"
"upload data.xlsx from documents"
```

### 3. Combined Open and Upload
```
"open orcasheets and upload industry.csv from downloads"
"open orcasheets and upload data.xlsx from documents project MyProject"
```

### 4. Select Project
```
"select project ProjectName"
```

### 5. Add New Sheet
```
"add new sheet"
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ORCASHEETS_DEFAULT_PROJECT` | Default project name | "Default Project" |
| `DOWNLOADS_FOLDER` | Downloads folder path | "~/Downloads" |
| `SCREENSHOT_DELAY` | Delay after screenshots | 1.0 |
| `CLICK_DELAY` | Delay after clicks | 0.5 |
| `TYPING_DELAY` | Delay after typing | 0.1 |
| `WINDOW_TIMEOUT` | Window detection timeout | 10.0 |

### Programmatic Configuration

```python
from orcasheets import OrcaSheetsConfig, OrcaSheetsFramework

config = OrcaSheetsConfig(
    default_project="My Default Project",
    screenshot_delay=0.5,
    click_delay=0.3
)

framework = OrcaSheetsFramework(config)
```

## 🛡️ Security Restrictions

### Allowed Operations
- Opening OrcaSheets application
- Uploading files to OrcaSheets
- Selecting projects
- Adding new sheets
- Taking screenshots for automation

### Blocked Operations
- Web browsing (Chrome, Firefox, Safari)
- Email applications
- Social media
- System administration
- File management outside OrcaSheets context
- Installing or downloading software
- Financial transactions
- Password or account management

### File Restrictions
- **Allowed folders**: Downloads, Documents, Desktop only
- **Allowed extensions**: .csv, .xlsx, .xls, .json, .txt
- **Path validation**: All file paths are validated for security

## 🔍 Task Validation

The framework includes comprehensive validation:

```python
from orcasheets import TaskValidator

# Parse user input
task = TaskValidator.parse_user_request("open orcasheets and upload data.csv from downloads")

# Validate task
if task and task.validate():
    print("Task is safe to execute")
else:
    print("Task validation failed")
```

## 🎯 Example Usage Patterns

### Basic File Upload Workflow
1. User: "open orcasheets and upload sales_data.csv from downloads"
2. Framework opens Spotlight search
3. Types "orcasheets" and launches app
4. Waits for OrcaSheets window to appear
5. Selects default project (or specified project)
6. Clicks "Add new sheet" or "+" button
7. Navigates to file location
8. Uploads the specified file
9. Returns success status with screenshot

### Project-Specific Upload
1. User: "upload quarterly_report.xlsx from documents project Q4_Analysis"
2. Framework assumes OrcaSheets is already open
3. Searches for "Q4_Analysis" project
4. Selects the project
5. Uploads quarterly_report.xlsx
6. Returns success status

## 🐛 Troubleshooting

### Common Issues

1. **"OrcaSheets window did not appear"**
   - Ensure OrcaSheets is installed
   - Check if macOS requires accessibility permissions
   - Verify Spotlight search is working

2. **"File not found"**
   - Verify file exists in specified folder
   - Check file extension is supported
   - Ensure proper file path format

3. **"Task validation failed"**
   - Request contains blocked keywords
   - File path outside allowed directories
   - Unsupported file extension

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your automation code here
```

## 🔄 Extending the Framework

### Adding New Task Types

1. Add to `TaskType` enum in `tasks.py`
2. Implement validation in `TaskValidator`
3. Add execution logic in `OrcaSheetsTool`
4. Update tool parameters

### Adding New File Types

1. Update `ALLOWED_FILE_EXTENSIONS` in `tasks.py`
2. Test with the new file type
3. Update documentation

## 📝 API Reference

### OrcaSheetsFramework

Main framework class for processing requests.

```python
framework = OrcaSheetsFramework(config)
result = framework.process_user_request("open orcasheets")
```

### OrcaSheetsTool

Core automation tool that implements the actual UI interactions.

```python
tool = OrcaSheetsTool(config)
result = tool(task_type="open_orcasheets", parameters={})
```

### TaskValidator

Validates and parses user requests into safe tasks.

```python
task = TaskValidator.parse_user_request(user_input)
is_valid = task.validate() if task else False
```

## 🤝 Contributing

When contributing to this framework:

1. Maintain security restrictions - never allow non-OrcaSheets operations
2. Add comprehensive validation for new features
3. Include tests for task validation
4. Update documentation for new operations
5. Follow the existing code patterns

## ⚠️ Important Notes

- This framework is designed to be run in a controlled environment
- Always validate user input before execution
- Screenshots may contain sensitive information - handle appropriately
- The framework requires macOS accessibility permissions for UI automation
- File uploads are restricted to safe directories and file types only

## 📄 License

This project extends the original Anthropic Computer Use framework and maintains the same security principles with additional restrictions for OrcaSheets-only operation.