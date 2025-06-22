# OrcaSheets Automation Framework

A specialized automation framework for OrcaSheets app tasks, built as a wrapper around the existing computer automation tools.

## Features

- **Framework-based Architecture**: Extensible design for adding new tasks
- **Multiple Automation Methods**: 
  - Coordinate-based clicking (using computer.py)
  - AppleScript integration for more reliable automation
  - Computer vision for dynamic element detection
- **Task Registry System**: Organized task management and workflows
- **Non-hardcoded Coordinates**: Uses image analysis and AppleScript when possible

## Core Functionality

### Main Tasks
1. **Open OrcaSheets** - Uses Spotlight to launch the application
2. **Project Selection** - Select projects with search capability
3. **File Upload** - Add new sheets and upload files

### Example Usage

```python
import asyncio
from tools.orcasheets import OrcaSheetsAutomation

# Simple one-liner
from tools.orcasheets.orcasheets_automation import automate_orcasheets

async def main():
    # Upload industry.csv from Downloads to default project
    success = await automate_orcasheets("~/Downloads/industry.csv", "default")
    print(f"Result: {'Success' if success else 'Failed'}")

asyncio.run(main())
```

### Advanced Usage with Task Registry

```python
from tools.orcasheets.core.tasks import TaskRegistry, WORKFLOWS
from tools.orcasheets import OrcaSheetsAutomation

async def advanced_example():
    automation = OrcaSheetsAutomation()
    registry = TaskRegistry()
    
    # Execute complete workflow
    success = await registry.execute_workflow(
        WORKFLOWS["upload_file"],
        automation,
        project_name="My Project",
        file_path="~/Downloads/data.csv"
    )
```

## Architecture

```
tools/orcasheets/
├── __init__.py                 # Main exports
├── orcasheets_automation.py    # Main automation class
├── core/                       # Core framework components
│   ├── tasks.py               # Task registry and task definitions
│   ├── vision.py              # Computer vision for element detection
│   └── applescript_helper.py  # AppleScript integration
├── example_usage.py           # Usage examples
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

### Key Components

1. **OrcaSheetsAutomation** - Main automation class wrapping computer.py
2. **TaskRegistry** - Framework for managing and executing tasks
3. **ScreenAnalyzer** - Computer vision for finding UI elements
4. **AppleScriptHelper** - Alternative automation using AppleScript

## Installation

1. Install additional dependencies:
```bash
pip install -r tools/orcasheets/requirements.txt
```

2. Ensure system dependencies are available:
```bash
# cliclick (should already be installed for computer.py)
brew install cliclick

# Optional: tesseract for OCR
brew install tesseract
```

## Customization

### Adding New Tasks

```python
from tools.orcasheets.core.tasks import OrcaSheetsTask

class CustomTask(OrcaSheetsTask):
    def __init__(self):
        super().__init__("custom_task", "Description of custom task")
    
    def validate_params(self, **kwargs) -> bool:
        return "required_param" in kwargs
    
    async def execute(self, automation_instance, **kwargs) -> bool:
        # Your custom automation logic here
        return True

# Register the task
registry = TaskRegistry()
registry.register_task(CustomTask())
```

### Adjusting Coordinates

If the hardcoded coordinates don't work for your screen resolution:

1. Use the debug screenshot function:
```python
automation = OrcaSheetsAutomation()
await automation.take_debug_screenshot("debug.png")
```

2. Open the screenshot and note the coordinates of UI elements
3. Update the coordinates in `orcasheets_automation.py`

### Using AppleScript Instead

For more reliable automation, use AppleScript methods:

```python
from tools.orcasheets.core.applescript_helper import AppleScriptHelper

# Open app reliably
await AppleScriptHelper.open_application("OrcaSheets")

# Click buttons by name (if accessible)
await AppleScriptHelper.click_button_by_name("OrcaSheets", "Add new sheet")
```

## Workflow Examples

### Basic File Upload
```python
# Open OrcaSheets -> Select default project -> Upload file
await automate_orcasheets("~/Downloads/industry.csv")
```

### Upload to Specific Project
```python
# Open OrcaSheets -> Search and select project -> Upload file
await automate_orcasheets("~/Downloads/data.csv", "My Project Name")
```

### Step-by-Step Control
```python
automation = OrcaSheetsAutomation()

await automation.search_and_open_app("OrcaSheets")
await automation.select_project("My Project")  
await automation.add_new_sheet()
await automation.upload_file("~/Downloads/file.csv")
```

## Troubleshooting

1. **App doesn't open**: Try using AppleScript method or check app name
2. **Wrong clicks**: Take debug screenshots and adjust coordinates
3. **Slow automation**: Adjust wait times in the automation instance
4. **Permission issues**: Grant accessibility permissions to Terminal/Python

## Future Enhancements

- OCR integration for text-based element detection
- Machine learning for UI element recognition  
- Support for more OrcaSheets operations
- Better error handling and recovery
- Configuration file for coordinates and settings