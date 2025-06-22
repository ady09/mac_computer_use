import subprocess
import asyncio
from typing import Optional, List


class AppleScriptHelper:
    """
    Helper class for AppleScript integration to interact with macOS applications.
    This provides an alternative to coordinate-based clicking.
    """
    
    @staticmethod
    async def run_applescript(script: str) -> tuple[bool, str]:
        """
        Execute an AppleScript and return success status and output.
        
        Args:
            script: AppleScript code to execute
            
        Returns:
            Tuple of (success, output)
        """
        try:
            process = await asyncio.create_subprocess_exec(
                'osascript', '-e', script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return True, stdout.decode('utf-8').strip()
            else:
                return False, stderr.decode('utf-8').strip()
                
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    async def open_application(app_name: str) -> bool:
        """Open an application using AppleScript"""
        script = f'tell application "{app_name}" to activate'
        success, output = await AppleScriptHelper.run_applescript(script)
        return success
    
    @staticmethod
    async def is_application_running(app_name: str) -> bool:
        """Check if an application is running"""
        script = f'''
        tell application "System Events"
            return (name of processes) contains "{app_name}"
        end tell
        '''
        success, output = await AppleScriptHelper.run_applescript(script)
        if success:
            return output.lower() == 'true'
        return False
    
    @staticmethod
    async def get_application_windows(app_name: str) -> List[str]:
        """Get list of window titles for an application"""
        script = f'''
        tell application "{app_name}"
            return name of every window
        end tell
        '''
        success, output = await AppleScriptHelper.run_applescript(script)
        if success and output:
            # Parse the output which is typically comma-separated
            return [w.strip() for w in output.split(',')]
        return []
    
    @staticmethod
    async def click_menu_item(app_name: str, menu_name: str, menu_item: str) -> bool:
        """Click a menu item in an application"""
        script = f'''
        tell application "{app_name}"
            activate
            tell application "System Events"
                tell process "{app_name}"
                    click menu item "{menu_item}" of menu "{menu_name}" of menu bar 1
                end tell
            end tell
        end tell
        '''
        success, output = await AppleScriptHelper.run_applescript(script)
        return success
    
    @staticmethod
    async def open_file_dialog(app_name: str) -> bool:
        """Try to open a file dialog using common keyboard shortcuts"""
        script = f'''
        tell application "{app_name}"
            activate
            tell application "System Events"
                tell process "{app_name}"
                    key code 12 using {{command down}} -- Cmd+Q equivalent for opening files
                end tell
            end tell
        end tell
        '''
        success, output = await AppleScriptHelper.run_applescript(script)
        return success
    
    @staticmethod
    async def type_text(text: str) -> bool:
        """Type text using AppleScript"""
        # Escape quotes in the text
        escaped_text = text.replace('"', '\\"')
        script = f'''
        tell application "System Events"
            keystroke "{escaped_text}"
        end tell
        '''
        success, output = await AppleScriptHelper.run_applescript(script)
        return success
    
    @staticmethod
    async def press_key_combination(keys: str) -> bool:
        """
        Press a key combination (e.g., "command down", "shift down", etc.)
        
        Args:
            keys: Key combination in AppleScript format
        """
        script = f'''
        tell application "System Events"
            key code 36 using {{{keys}}} -- Enter key with modifiers
        end tell
        '''
        success, output = await AppleScriptHelper.run_applescript(script)
        return success
    
    @staticmethod
    async def spotlight_search(search_term: str) -> bool:
        """Open Spotlight and search for something"""
        script = f'''
        tell application "System Events"
            key code 49 using {{command down}} -- Cmd+Space for Spotlight
            delay 0.5
            keystroke "{search_term}"
            delay 1
            key code 36 -- Enter
        end tell
        '''
        success, output = await AppleScriptHelper.run_applescript(script)
        return success
    
    @staticmethod
    async def get_ui_elements(app_name: str, window_name: str = "1") -> Optional[str]:
        """
        Get UI elements of an application window.
        This can help identify clickable elements without hardcoded coordinates.
        """
        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                tell window {window_name}
                    return entire contents
                end tell
            end tell
        end tell
        '''
        success, output = await AppleScriptHelper.run_applescript(script)
        if success:
            return output
        return None
    
    @staticmethod
    async def click_button_by_name(app_name: str, button_name: str, window_name: str = "1") -> bool:
        """Click a button by its name/title"""
        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                tell window {window_name}
                    click button "{button_name}"
                end tell
            end tell
        end tell
        '''
        success, output = await AppleScriptHelper.run_applescript(script)
        return success
    
    @staticmethod
    async def select_file_in_dialog(file_path: str) -> bool:
        """Select a file in an open file dialog"""
        script = f'''
        tell application "System Events"
            keystroke "g" using {{command down, shift down}} -- Cmd+Shift+G to go to folder
            delay 1
            keystroke "{file_path}"
            delay 0.5
            key code 36 -- Enter
        end tell
        '''
        success, output = await AppleScriptHelper.run_applescript(script)
        return success