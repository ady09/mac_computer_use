"""
File operations for OrcaSheets automation.
"""

import os
from pathlib import Path
from typing import List, Optional


class FileOperations:
    """Handle file-related operations for OrcaSheets."""
    
    @staticmethod
    def find_files_by_pattern(directory: str, pattern: str) -> List[Path]:
        """Find files matching a pattern in a directory."""
        dir_path = Path(directory)
        if not dir_path.exists():
            return []
        
        import fnmatch
        matches = []
        for file_path in dir_path.iterdir():
            if file_path.is_file() and fnmatch.fnmatch(file_path.name, pattern):
                matches.append(file_path)
        
        return matches
    
    @staticmethod
    def get_downloads_directory() -> Path:
        """Get the user's Downloads directory."""
        return Path.home() / "Downloads"
    
    @staticmethod
    def validate_file_exists(file_path: str) -> bool:
        """Check if a file exists."""
        try:
            path = Path(file_path)
            return path.exists() and path.is_file()
        except Exception:
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Optional[dict]:
        """Get information about a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                'name': path.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'extension': path.suffix,
                'absolute_path': str(path.absolute())
            }
        except Exception:
            return None

