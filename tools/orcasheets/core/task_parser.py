"""
Intelligent task parser for OrcaSheets automation.
Parses natural language commands into structured tasks.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ParsedTask:
    """Represents a parsed automation task"""
    action: str
    target: str
    parameters: Dict[str, Any]
    description: str


class TaskParser:
    """
    Parses natural language commands into structured automation tasks.
    """
    
    def __init__(self):
        # Define action patterns
        self.action_patterns = {
            # Opening actions
            'open': [
                r'open\s+(\w+)',
                r'launch\s+(\w+)',
                r'start\s+(\w+)'
            ],
            
            # Clicking actions
            'click': [
                r'click\s+(?:on\s+)?(.+?)(?:\s+button|\s+link|$)',
                r'press\s+(.+?)(?:\s+button|$)',
                r'tap\s+(.+?)(?:\s+button|$)'
            ],
            
            # Selection actions
            'select': [
                r'select\s+(.+?)(?:\s+project|\s+option|$)',
                r'choose\s+(.+?)(?:\s+project|\s+option|$)',
                r'pick\s+(.+?)(?:\s+project|\s+option|$)'
            ],
            
            # Upload actions
            'upload': [
                r'upload\s+(.+?)(?:\s+file)?(?:\s+from\s+(.+?))?',
                r'add\s+(.+?)(?:\s+file)?(?:\s+from\s+(.+?))?'
            ],
            
            # Close actions
            'close': [
                r'close\s+(.+?)(?:\s+tab|\s+window|$)',
                r'shut\s+(.+?)(?:\s+tab|\s+window|$)',
                r'dismiss\s+(.+?)(?:\s+tab|\s+window|$)'
            ],
            
            # Navigation actions
            'navigate': [
                r'go\s+to\s+(.+)',
                r'navigate\s+to\s+(.+)',
                r'switch\s+to\s+(.+)'
            ],
            
            # Search actions
            'search': [
                r'search\s+for\s+(.+)',
                r'find\s+(.+)',
                r'look\s+for\s+(.+)'
            ]
        }
        
        # Define target type patterns
        self.target_patterns = {
            'application': r'(orcasheets?|app|application)',
            'project': r'(.+?)\s+project',
            'file': r'(.+?\.(?:csv|xlsx?|txt|json))',
            'tab': r'(.+?)\s+tab',
            'button': r'(.+?)\s+(?:button|btn)',
            'link': r'(.+?)\s+link',
            'sheet': r'(?:new\s+)?sheet',
            'dialog': r'(.+?)\s+(?:dialog|window|popup)'
        }
    
    def parse_command(self, command: str) -> List[ParsedTask]:
        """
        Parse a natural language command into structured tasks.
        
        Args:
            command: Natural language command
            
        Returns:
            List of ParsedTask objects
        """
        command = command.lower().strip()
        tasks = []
        
        print(f"🔍 Parsing command: '{command}'")
        
        # Handle compound commands (multiple actions)
        if ' and ' in command:
            sub_commands = command.split(' and ')
            for sub_cmd in sub_commands:
                tasks.extend(self.parse_command(sub_cmd.strip()))
            return tasks
        
        # Handle sequential commands (then, after)
        if ' then ' in command or ' after ' in command:
            separator = ' then ' if ' then ' in command else ' after '
            sub_commands = command.split(separator)
            
            # Reverse order for "after" to maintain logical sequence
            if separator == ' after ':
                sub_commands = sub_commands[::-1]
            
            for sub_cmd in sub_commands:
                sub_cmd = sub_cmd.strip()
                # Skip common filler words
                if sub_cmd and not sub_cmd.startswith(('selecting', 'choosing', 'picking')):
                    tasks.extend(self.parse_command(sub_cmd))
                elif sub_cmd.startswith(('selecting', 'choosing', 'picking')):
                    # Convert to proper select command
                    select_cmd = sub_cmd.replace('selecting', 'select').replace('choosing', 'choose').replace('picking', 'pick')
                    tasks.extend(self.parse_command(select_cmd))
            return tasks
        
        # Parse single command
        task = self._parse_single_command(command)
        if task:
            tasks.append(task)
        
        return tasks
    
    def _parse_single_command(self, command: str) -> Optional[ParsedTask]:
        """Parse a single command into a task"""
        
        # Try to match action patterns
        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command, re.IGNORECASE)
                if match:
                    return self._create_task_from_match(action, match, command)
        
        # If no specific action found, try to infer from context
        return self._infer_task_from_context(command)
    
    def _create_task_from_match(self, action: str, match, command: str) -> ParsedTask:
        """Create a task from a regex match"""
        
        groups = match.groups()
        target = groups[0] if groups else ""
        
        parameters = {}
        
        # Extract additional parameters based on action type
        if action == 'upload':
            if len(groups) > 1 and groups[1]:
                parameters['source_location'] = groups[1]
            
            # Look for file path patterns
            file_match = re.search(r'([^/\s]+\.(?:csv|xlsx?|txt|json))', target)
            if file_match:
                parameters['filename'] = file_match.group(1)
                # Try to infer full path
                if 'downloads' in command:
                    parameters['file_path'] = f"~/Downloads/{file_match.group(1)}"
                else:
                    parameters['file_path'] = f"~/{file_match.group(1)}"
        
        elif action == 'select':
            # Handle project selection
            if 'project' in command:
                parameters['project_name'] = target
        
        elif action == 'open':
            # Handle application opening
            if any(app in target for app in ['orcasheets', 'app']):
                parameters['application'] = 'OrcaSheets'
        
        elif action == 'close':
            # Handle tab/window closing
            if 'tab' in command:
                parameters['element_type'] = 'tab'
                parameters['tab_name'] = target
        
        # Determine target type
        target_type = self._determine_target_type(target, command)
        
        return ParsedTask(
            action=action,
            target=target,
            parameters=parameters,
            description=f"{action} {target_type}: {target}"
        )
    
    def _determine_target_type(self, target: str, command: str) -> str:
        """Determine the type of target (button, tab, file, etc.)"""
        
        for target_type, pattern in self.target_patterns.items():
            if re.search(pattern, command, re.IGNORECASE):
                return target_type
        
        # Infer from common patterns
        if '.' in target and any(ext in target for ext in ['.csv', '.xlsx', '.txt', '.json']):
            return 'file'
        elif 'new sheet' in command or 'add sheet' in command:
            return 'button'
        elif 'project' in command:
            return 'project'
        elif 'tab' in command:
            return 'tab'
        else:
            return 'element'
    
    def _infer_task_from_context(self, command: str) -> Optional[ParsedTask]:
        """Infer task when no explicit action pattern matches"""
        
        # Common inference patterns
        if 'orcasheets' in command and any(word in command for word in ['upload', 'add', 'import']):
            # Likely a file upload task
            file_match = re.search(r'([^/\s]+\.(?:csv|xlsx?|txt|json))', command)
            if file_match:
                filename = file_match.group(1)
                file_path = f"~/Downloads/{filename}" if 'downloads' in command else f"~/{filename}"
                
                return ParsedTask(
                    action='full_workflow',
                    target=filename,
                    parameters={
                        'file_path': file_path,
                        'filename': filename,
                        'project_name': 'default'
                    },
                    description=f"Upload file: {filename}"
                )
        
        # Default fallback
        return ParsedTask(
            action='unknown',
            target=command,
            parameters={},
            description=f"Unknown command: {command}"
        )
    
    def get_visual_targets_from_tasks(self, tasks: List[ParsedTask]) -> List[str]:
        """
        Extract visual targets that need to be found on screen.
        
        Returns list of descriptions for visual AI to search for.
        """
        visual_targets = []
        
        for task in tasks:
            if task.action == 'click':
                visual_targets.append(f"{task.target} button")
            elif task.action == 'select':
                if 'project_name' in task.parameters:
                    visual_targets.append(f"{task.parameters['project_name']} project")
                else:
                    visual_targets.append(task.target)
            elif task.action == 'upload':
                visual_targets.append("add new sheet button")
                visual_targets.append("plus button")
                visual_targets.append("upload button")
            elif task.action == 'close':
                if task.parameters.get('element_type') == 'tab':
                    visual_targets.append(f"{task.target} tab close button")
                    visual_targets.append(f"{task.target} tab")
            elif task.action == 'open':
                # Opening usually done via Spotlight, no visual target needed
                pass
            elif task.action == 'full_workflow':
                visual_targets.extend([
                    f"{task.parameters.get('project_name', 'default')} project",
                    "add new sheet button",
                    "plus button"
                ])
        
        return visual_targets
    
    def tasks_to_execution_plan(self, tasks: List[ParsedTask]) -> List[Dict[str, Any]]:
        """
        Convert parsed tasks into an execution plan for the automation system.
        """
        execution_plan = []
        
        for task in tasks:
            if task.action == 'open':
                execution_plan.append({
                    'method': 'open_application',
                    'parameters': {
                        'app_name': task.parameters.get('application', 'OrcaSheets')
                    },
                    'description': f"Open {task.parameters.get('application', 'OrcaSheets')}"
                })
            
            elif task.action == 'select':
                execution_plan.append({
                    'method': 'find_and_click',
                    'parameters': {
                        'description': f"{task.target} project",
                        'search_terms': [f"{task.target} project", task.target]
                    },
                    'description': f"Select {task.target} project"
                })
            
            elif task.action == 'click':
                execution_plan.append({
                    'method': 'find_and_click',
                    'parameters': {
                        'description': f"{task.target} button",
                        'search_terms': [f"{task.target} button", task.target, f"{task.target} link"]
                    },
                    'description': f"Click {task.target}"
                })
            
            elif task.action == 'upload':
                # Upload is a multi-step process
                execution_plan.append({
                    'method': 'find_and_click',
                    'parameters': {
                        'description': 'add new sheet button',
                        'search_terms': ['add new sheet', 'new sheet', '+ add', 'upload', 'plus button']
                    },
                    'description': 'Click add new sheet button'
                })
                
                execution_plan.append({
                    'method': 'upload_file',
                    'parameters': {
                        'file_path': task.parameters.get('file_path', ''),
                        'filename': task.parameters.get('filename', '')
                    },
                    'description': f"Upload {task.parameters.get('filename', 'file')}"
                })
            
            elif task.action == 'close':
                if task.parameters.get('element_type') == 'tab':
                    execution_plan.append({
                        'method': 'close_tab',
                        'parameters': {
                            'tab_name': task.target,
                            'search_terms': [f"{task.target} tab", f"close {task.target}", f"{task.target} close button"]
                        },
                        'description': f"Close {task.target} tab"
                    })
            
            elif task.action == 'full_workflow':
                # Full workflow combines multiple steps
                execution_plan.extend([
                    {
                        'method': 'open_application',
                        'parameters': {'app_name': 'OrcaSheets'},
                        'description': 'Open OrcaSheets'
                    },
                    {
                        'method': 'find_and_click',
                        'parameters': {
                            'description': f"{task.parameters.get('project_name', 'default')} project",
                            'search_terms': [f"{task.parameters.get('project_name', 'default')} project", task.parameters.get('project_name', 'default')]
                        },
                        'description': f"Select {task.parameters.get('project_name', 'default')} project"
                    },
                    {
                        'method': 'find_and_click',
                        'parameters': {
                            'description': 'add new sheet button',
                            'search_terms': ['add new sheet', 'new sheet', '+ add', 'upload']
                        },
                        'description': 'Click add new sheet'
                    },
                    {
                        'method': 'upload_file',
                        'parameters': {
                            'file_path': task.parameters.get('file_path', ''),
                            'filename': task.parameters.get('filename', '')
                        },
                        'description': f"Upload {task.parameters.get('filename', 'file')}"
                    }
                ])
        
        return execution_plan