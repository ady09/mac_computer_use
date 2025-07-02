"""
Natural language test command parser for test automation framework
"""

import re
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedCommand:
    """Parsed natural language test command"""
    action: str  # 'run_test', 'run_suite', 'run_all'
    project: Optional[str] = None
    feature: Optional[str] = None
    test_name: Optional[str] = None
    test_file: Optional[str] = None
    test_directory: Optional[str] = None
    tags: List[str] = None
    platform: Optional[str] = None  # 'desktop', 'mobile', 'web'
    emulator: bool = False
    parallel: bool = False
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TestCommandParser:
    """Parser for natural language test automation commands"""
    
    def __init__(self, tests_base_dir: str = None):
        self.tests_base_dir = tests_base_dir or "/Users/aditya/Documents/computer-use/mac_computer_use/tests"
        
        # Command patterns
        self.patterns = {
            # Test specific flows/features
            'test_flow': [
                r'test (?P<feature>[\w\s]+) flow for (?P<project>\w+)',
                r'test (?P<feature>[\w\s]+) in (?P<project>\w+)',
                r'run (?P<feature>[\w\s]+) test for (?P<project>\w+)',
            ],
            
            # Run all tests
            'run_all_project': [
                r'run all (?P<project>\w+) tests?',
                r'test all (?P<project>\w+) features?',
                r'execute all (?P<project>\w+) test cases?',
            ],
            
            # Specific test file
            'run_test_file': [
                r'run test (?P<test_name>[\w\s]+)\.json',
                r'execute (?P<test_name>[\w\s]+)\.json',
                r'test file (?P<test_name>[\w\s]+)\.json',
            ],
            
            # Mobile/emulator specific
            'mobile_test': [
                r'test (?P<feature>[\w\s]+) (?:on|using) (?P<platform>mobile|emulator)',
                r'(?P<platform>mobile|emulator) test for (?P<feature>[\w\s]+)',
                r'test mobile app (?P<feature>[\w\s]+)',
            ],
            
            # Web app tests
            'web_test': [
                r'test (?P<feature>[\w\s]+) (?:on|for) web app',
                r'web test (?P<feature>[\w\s]+)',
                r'test web (?P<feature>[\w\s]+)',
            ],
            
            # Tagged tests
            'tagged_tests': [
                r'run (?P<tags>[\w,\s]+) tests',
                r'test with tags? (?P<tags>[\w,\s]+)',
                r'execute (?P<tags>[\w,\s]+) test cases',
            ]
        }
        
        # Project aliases
        self.project_aliases = {
            'orcasheets': ['orcasheets', 'orca', 'sheets'],
            'mobile_app': ['mobile', 'app', 'mobile_app'],
            'web_app': ['web', 'webapp', 'web_app', 'website'],
            'spotify': ['spotify', 'music', 'player'],
            'vscode': ['vscode', 'vs code', 'visual studio code', 'code editor', 'editor']
        }
        
        # Feature aliases
        self.feature_aliases = {
            'file_upload': ['file upload', 'upload file', 'file uploading', 'upload'],
            'login': ['login', 'sign in', 'authentication', 'auth'],
            'checkout': ['checkout', 'purchase', 'buy', 'payment'],
            'navigation': ['navigation', 'nav', 'menu', 'navigate'],
            'project_creation': ['project creation', 'new project', 'create project'],
            'data_import': ['data import', 'import data', 'import'],
            'play_music': ['play music', 'music playback', 'play song', 'playback'],
            'create_playlist': ['create playlist', 'new playlist', 'playlist creation'],
            'shuffle_play': ['shuffle play', 'shuffle', 'random play'],
            'search_artist': ['search artist', 'find artist', 'artist search'],
            'create_new_file': ['create file', 'new file', 'file creation'],
            'open_folder_project': ['open folder', 'open project', 'project management'],
            'search_and_replace': ['search replace', 'find replace', 'text search'],
            'terminal_integration': ['terminal', 'integrated terminal', 'command line'],
            'debug_session': ['debug', 'debugging', 'breakpoints'],
            'extension_management': ['extensions', 'plugins', 'marketplace']
        }

    def parse(self, command: str) -> ParsedCommand:
        """
        Parse a natural language test command
        
        Args:
            command: Natural language command string
            
        Returns:
            ParsedCommand object with parsed components
        """
        command = command.lower().strip()
        
        # Try each pattern category
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command, re.IGNORECASE)
                if match:
                    return self._process_match(category, match, command)
        
        # If no pattern matches, try to extract components manually
        return self._fallback_parse(command)

    def _process_match(self, category: str, match: re.Match, command: str) -> ParsedCommand:
        """Process a regex match based on category"""
        groups = match.groupdict()
        
        if category == 'test_flow':
            project = self._normalize_project(groups.get('project', ''))
            feature = self._normalize_feature(groups.get('feature', ''))
            
            return ParsedCommand(
                action='run_test',
                project=project,
                feature=feature,
                test_file=self._find_test_file(project, feature),
                platform=self._detect_platform(command),
                emulator='emulator' in command or 'mobile' in command
            )
        
        elif category == 'run_all_project':
            project = self._normalize_project(groups.get('project', ''))
            return ParsedCommand(
                action='run_suite',
                project=project,
                test_directory=f"{self.tests_base_dir}/projects/{project}",
                parallel='parallel' in command
            )
        
        elif category == 'run_test_file':
            test_name = groups.get('test_name', '').replace(' ', '_')
            return ParsedCommand(
                action='run_test',
                test_name=test_name,
                test_file=self._find_test_file_by_name(test_name)
            )
        
        elif category in ['mobile_test', 'web_test']:
            feature = self._normalize_feature(groups.get('feature', ''))
            platform = 'mobile' if category == 'mobile_test' or 'mobile' in command else 'web'
            project = 'mobile_app' if platform == 'mobile' else 'web_app'
            
            return ParsedCommand(
                action='run_test',
                project=project,
                feature=feature,
                platform=platform,
                emulator=platform == 'mobile',
                test_file=self._find_test_file(project, feature)
            )
        
        elif category == 'tagged_tests':
            tags = [tag.strip() for tag in groups.get('tags', '').split(',')]
            return ParsedCommand(
                action='run_suite',
                tags=tags,
                test_directory=self.tests_base_dir
            )
        
        return self._fallback_parse(command)

    def _fallback_parse(self, command: str) -> ParsedCommand:
        """Fallback parsing when no patterns match"""
        # Extract project if mentioned
        project = None
        for proj, aliases in self.project_aliases.items():
            if any(alias in command for alias in aliases):
                project = proj
                break
        
        # Extract feature if mentioned
        feature = None
        for feat, aliases in self.feature_aliases.items():
            if any(alias in command for alias in aliases):
                feature = feat
                break
        
        # Determine action
        if 'all' in command:
            action = 'run_suite'
        else:
            action = 'run_test'
        
        return ParsedCommand(
            action=action,
            project=project,
            feature=feature,
            test_file=self._find_test_file(project, feature) if project and feature else None,
            platform=self._detect_platform(command),
            emulator='emulator' in command or 'mobile' in command
        )

    def _normalize_project(self, project: str) -> str:
        """Normalize project name to standard format"""
        project = project.lower().strip()
        for standard, aliases in self.project_aliases.items():
            if project in aliases:
                return standard
        return project

    def _normalize_feature(self, feature: str) -> str:
        """Normalize feature name to standard format"""
        feature = feature.lower().strip()
        for standard, aliases in self.feature_aliases.items():
            if feature in aliases:
                return standard
        return feature.replace(' ', '_')

    def _detect_platform(self, command: str) -> Optional[str]:
        """Detect platform from command"""
        if any(word in command for word in ['mobile', 'app', 'emulator']):
            return 'mobile'
        elif any(word in command for word in ['web', 'website', 'browser']):
            return 'web'
        elif any(word in command for word in ['desktop', 'mac', 'application']):
            return 'desktop'
        return None

    def _find_test_file(self, project: str, feature: str) -> Optional[str]:
        """Find test file based on project and feature"""
        if not project or not feature:
            return None
        
        project_dir = Path(self.tests_base_dir) / "projects" / project
        if not project_dir.exists():
            return None
        
        # Try exact match first
        test_file = project_dir / f"{feature}.json"
        if test_file.exists():
            return str(test_file)
        
        # Try pattern matching
        for file_path in project_dir.glob("*.json"):
            if feature in file_path.stem.lower():
                return str(file_path)
        
        return None

    def _find_test_file_by_name(self, test_name: str) -> Optional[str]:
        """Find test file by name across all projects"""
        tests_dir = Path(self.tests_base_dir)
        
        # Search in projects directory
        for project_dir in (tests_dir / "projects").glob("*/"):
            test_file = project_dir / f"{test_name}.json"
            if test_file.exists():
                return str(test_file)
        
        return None

    def get_available_tests(self, project: str = None) -> Dict[str, List[str]]:
        """Get list of available tests, optionally filtered by project"""
        available = {}
        projects_dir = Path(self.tests_base_dir) / "projects"
        
        if not projects_dir.exists():
            return available
        
        for project_dir in projects_dir.glob("*/"):
            project_name = project_dir.name
            
            if project and project_name != project:
                continue
            
            tests = []
            for test_file in project_dir.glob("*.json"):
                tests.append(test_file.stem)
            
            if tests:
                available[project_name] = tests
        
        return available

    def suggest_command(self, partial_command: str) -> List[str]:
        """Suggest possible commands based on partial input"""
        suggestions = []
        available_tests = self.get_available_tests()
        
        partial = partial_command.lower()
        
        # Suggest project-based commands
        for project in available_tests.keys():
            if project in partial:
                suggestions.append(f"run all {project} tests")
                for test in available_tests[project]:
                    suggestions.append(f"test {test} for {project}")
        
        # Suggest common patterns
        common_patterns = [
            "test file upload flow for orcasheets",
            "run all orcasheets tests",
            "test mobile app login using emulator",
            "test checkout flow for web app"
        ]
        
        for pattern in common_patterns:
            if any(word in pattern for word in partial.split()):
                suggestions.append(pattern)
        
        return suggestions[:5]  # Return top 5 suggestions