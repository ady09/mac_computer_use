"""
JSON schema validation for test automation framework
"""

import json
import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class ActionType(str, Enum):
    """Supported test actions"""
    COMPUTER_CLICK = "computer_click"
    COMPUTER_TYPE = "computer_type"
    COMPUTER_SCREENSHOT = "computer_screenshot"
    COMPUTER_KEY = "computer_key"
    WAIT = "wait"
    VERIFY_ELEMENT = "verify_element"
    VERIFY_TEXT = "verify_text"
    OPEN_APPLICATION = "open_application"
    CLOSE_APPLICATION = "close_application"
    FILE_UPLOAD = "file_upload"
    ENSURE_FILE_EXISTS = "ensure_file_exists"
    ICON_CLICK = "icon_click"
    ICON_FIND = "icon_find"
    ICON_SAVE_TEMPLATE = "icon_save_template"
    CUSTOM = "custom"


class OnFailureAction(str, Enum):
    """Actions to take when a step fails"""
    CONTINUE = "continue"
    STOP = "stop"
    RETRY = "retry"


class TestMetadata(BaseModel):
    """Test case metadata"""
    name: str = Field(..., description="Test case name")
    description: str = Field(..., description="Test case description")
    project: str = Field(..., description="Project identifier")
    feature: str = Field(..., description="Feature being tested")
    tags: List[str] = Field(default_factory=list, description="Test tags for categorization")
    timeout: int = Field(default=60, ge=1, le=3600, description="Test timeout in seconds")
    prerequisites: List[str] = Field(default_factory=list, description="Test prerequisites")


class TestStep(BaseModel):
    """Individual test step"""
    name: str = Field(..., description="Step description")
    action: ActionType = Field(..., description="Action to perform")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    expected: Dict[str, Any] = Field(default_factory=dict, description="Expected outcomes")
    timeout: int = Field(default=30, ge=1, le=300, description="Step timeout in seconds")
    on_failure: OnFailureAction = Field(default=OnFailureAction.STOP, description="Failure handling")
    screenshot: bool = Field(default=False, description="Take screenshot after step")


class TestAssertions(BaseModel):
    """Test success/failure criteria"""
    success_criteria: List[str] = Field(default_factory=list, description="Success indicators")
    failure_indicators: List[str] = Field(default_factory=list, description="Failure indicators")


class TestCase(BaseModel):
    """Complete test case definition"""
    metadata: TestMetadata
    setup: List[TestStep] = Field(default_factory=list, description="Setup steps")
    steps: List[TestStep] = Field(..., min_items=1, description="Main test steps")
    cleanup: List[TestStep] = Field(default_factory=list, description="Cleanup steps")
    assertions: TestAssertions = Field(default_factory=TestAssertions, description="Test assertions")

    @validator('steps')
    def validate_steps_not_empty(cls, v):
        if not v:
            raise ValueError("Test case must have at least one step")
        return v


class TestSuite(BaseModel):
    """Collection of test cases"""
    name: str
    description: str
    tests: List[str] = Field(..., description="List of test file paths")
    parallel: bool = Field(default=False, description="Run tests in parallel")
    timeout: int = Field(default=300, description="Suite timeout in seconds")


def validate_test_file(file_path: str) -> TestCase:
    """
    Validate a JSON test file against the schema
    
    Args:
        file_path: Path to the JSON test file
        
    Returns:
        Validated TestCase object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
        ValueError: If validation fails
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test file not found: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        test_case = TestCase(**data)
        return test_case
        
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in {file_path}: {e.msg}", e.doc, e.pos)
    except Exception as e:
        raise ValueError(f"Validation failed for {file_path}: {str(e)}")


def create_test_template(project: str, feature: str, name: str) -> Dict[str, Any]:
    """
    Create a test template with basic structure
    
    Args:
        project: Project name
        feature: Feature name
        name: Test name
        
    Returns:
        Dictionary with test template structure
    """
    return {
        "metadata": {
            "name": name,
            "description": f"Test case for {feature} in {project}",
            "project": project,
            "feature": feature,
            "tags": ["auto-generated"],
            "timeout": 60,
            "prerequisites": []
        },
        "setup": [],
        "steps": [
            {
                "name": "Example step",
                "action": "computer_screenshot",
                "params": {},
                "expected": {},
                "timeout": 10,
                "on_failure": "stop"
            }
        ],
        "cleanup": [],
        "assertions": {
            "success_criteria": [],
            "failure_indicators": []
        }
    }


def validate_test_directory(tests_dir: str) -> Dict[str, List[str]]:
    """
    Validate all test files in a directory
    
    Args:
        tests_dir: Path to tests directory
        
    Returns:
        Dictionary with 'valid' and 'invalid' lists of file paths
    """
    valid_tests = []
    invalid_tests = []
    
    if not os.path.exists(tests_dir):
        return {"valid": [], "invalid": ["Directory not found"]}
    
    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if file.endswith('.json') and not file.startswith('.'):
                file_path = os.path.join(root, file)
                try:
                    validate_test_file(file_path)
                    valid_tests.append(file_path)
                except Exception as e:
                    invalid_tests.append(f"{file_path}: {str(e)}")
    
    return {"valid": valid_tests, "invalid": invalid_tests}