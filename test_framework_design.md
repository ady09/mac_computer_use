# Test Automation Framework Design

## Architecture Overview

This framework extends mac_computer_use to support JSON-based test automation with natural language parsing.

### Core Components

1. **Test Definition Schema** (`test_schema.py`)
   - JSON schema for test case definitions
   - Metadata: name, description, tags, timeout
   - Steps: actions with parameters and expected outcomes
   - Assertions: validation rules for success/failure

2. **Test Parser** (`test_parser.py`)
   - Natural language command parsing
   - Mapping commands to test files/folders
   - Context extraction (project, feature, flow)

3. **Test Runner** (`test_runner.py`)
   - Test execution engine
   - Step-by-step automation using existing tools
   - Result collection and reporting
   - Screenshot capture for failures

4. **Test Tools Integration** (`test_tools.py`)
   - Bridge between test framework and existing tools
   - Computer vision validation
   - Enhanced assertion capabilities

### Directory Structure

```
tests/
├── projects/
│   ├── orcasheets/
│   │   ├── file_upload.json
│   │   ├── project_creation.json
│   │   └── data_import.json
│   ├── mobile_app/
│   │   ├── login_flow.json
│   │   └── navigation.json
│   └── web_app/
│       ├── checkout_flow.json
│       └── user_registration.json
├── templates/
│   └── test_template.json
└── reports/
    ├── latest/
    └── archive/
```

### Test JSON Schema

```json
{
  "metadata": {
    "name": "File Upload Flow",
    "description": "Test file uploading functionality in OrcaSheets",
    "project": "orcasheets",
    "feature": "file_upload",
    "tags": ["ui", "file_handling", "smoke"],
    "timeout": 120,
    "prerequisites": ["orcasheets_installed", "test_file_available"]
  },
  "setup": [
    {
      "action": "ensure_file_exists",
      "params": {"path": "~/Downloads/test_data.csv"}
    }
  ],
  "steps": [
    {
      "name": "Open OrcaSheets",
      "action": "computer_click",
      "params": {"target": "orcasheets_icon"},
      "expected": {"window_visible": "OrcaSheets"},
      "timeout": 10
    }
  ],
  "cleanup": [
    {
      "action": "close_application",
      "params": {"app": "OrcaSheets"}
    }
  ],
  "assertions": {
    "success_criteria": ["file_uploaded", "data_imported"],
    "failure_indicators": ["error_dialog", "timeout_exceeded"]
  }
}
```

### Natural Language Commands

- "Test file uploading flow for Orcasheets"
- "Run all orcasheets tests"
- "Test mobile app login using emulator"
- "Execute checkout flow tests for web app"

### Integration Points

1. **Existing Tools**: Leverage computer.py, orcasheets/ tools
2. **Vision System**: Use existing OCR and image matching
3. **API Server**: Extend api_server.py with test endpoints
4. **Reporting**: Generate HTML reports with screenshots