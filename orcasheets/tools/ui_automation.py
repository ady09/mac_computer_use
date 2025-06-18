"""
UI automation utilities for OrcaSheets.
"""

import time
import subprocess
import os
from typing import Optional, Tuple
from ..config import OrcaSheetsConfig


class UIAutomation:
    """Handles UI automation for macOS."""
    
    def __init__(self, config: OrcaSheetsConfig):
        self.config = config
        self._check_system_requirements()
    
    def take_screenshot(self) -> str:
        """Take a screenshot and return the base64 encoded image."""
        timestamp = int(time.time())
        screenshot_path = f"/tmp/screenshot_{timestamp}.png"
        
        # Use screencapture command
        subprocess.run([
            "screencapture", 
            "-x",  # Don't play sound
            screenshot_path
        ], check=True)
        
        # Convert to base64
        with open(screenshot_path, "rb") as f:
            import base64
            screenshot_b64 = base64.b64encode(f.read()).decode()
        
        # Clean up
        os.remove(screenshot_path)
        
        return screenshot_b64
    
    def click_at_coordinates(self, x: int, y: int) -> bool:
        """Click at specific coordinates using cliclick."""
        try:
            subprocess.run([
                "cliclick", 
                f"c:{x},{y}"
            ], check=True)
            time.sleep(self.config.click_delay)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def type_text(self, text: str) -> bool:
        """Type text using cliclick."""
        try:
            subprocess.run([
                "cliclick", 
                f"t:{text}"
            ], check=True)
            time.sleep(self.config.typing_delay)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def press_key_combination(self, keys: str) -> bool:
        """Press key combination (e.g., 'cmd+space')."""
        try:
            # First try with cliclick - fix key combination format
            if keys == "cmd+space":
                cliclick_cmd = ["cliclick", "kd:cmd", "k:space", "ku:cmd"]
            elif keys == "return":
                cliclick_cmd = ["cliclick", "k:return"]
            elif keys == "cmd+shift+g":
                cliclick_cmd = ["cliclick", "kd:cmd,shift", "k:g", "ku:cmd,shift"]
            else:
                # Generic handling
                parts = keys.split('+')
                if len(parts) > 1:
                    modifiers = ','.join(parts[:-1])
                    key = parts[-1]
                    cliclick_cmd = ["cliclick", f"kd:{modifiers}", f"k:{key}", f"ku:{modifiers}"]
                else:
                    cliclick_cmd = ["cliclick", f"k:{keys}"]
            
            result = subprocess.run(cliclick_cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                time.sleep(self.config.click_delay)
                return True
            
            # If cliclick fails, try with osascript
            return self._press_key_with_osascript(keys)
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback to osascript
            return self._press_key_with_osascript(keys)
    
    def _press_key_with_osascript(self, keys: str) -> bool:
        """Press key combination using osascript (AppleScript)."""
        try:
            # Convert to AppleScript format
            if keys == "cmd+space":
                applescript = 'tell application "System Events" to keystroke space using command down'
            elif keys == "return":
                applescript = 'tell application "System Events" to keystroke return'
            elif keys == "cmd+shift+g":
                applescript = 'tell application "System Events" to keystroke "g" using {command down, shift down}'
            else:
                # Generic conversion
                parts = keys.split('+')
                key = parts[-1]
                modifiers = parts[:-1]
                
                modifier_map = {
                    'cmd': 'command down',
                    'shift': 'shift down', 
                    'alt': 'option down',
                    'ctrl': 'control down'
                }
                
                modifier_str = ', '.join([modifier_map.get(m, f'{m} down') for m in modifiers])
                
                if modifier_str:
                    applescript = f'tell application "System Events" to keystroke "{key}" using {{{modifier_str}}}'
                else:
                    applescript = f'tell application "System Events" to keystroke "{key}"'
            
            subprocess.run([
                "osascript", 
                "-e", 
                applescript
            ], check=True, timeout=5)
            
            time.sleep(self.config.click_delay)
            return True
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False
    
    def open_spotlight_search(self) -> bool:
        """Open Spotlight search with multiple fallback methods."""
        # Method 1: Key combination
        if self.press_key_combination(self.config.spotlight_shortcut):
            time.sleep(1)  # Wait for Spotlight to appear
            return True
        
        # Method 2: Direct AppleScript
        try:
            subprocess.run([
                "osascript",
                "-e",
                'tell application "System Events" to keystroke space using command down'
            ], check=True, timeout=5)
            time.sleep(1)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        
        # Method 3: Open Spotlight via System Events
        try:
            subprocess.run([
                "osascript",
                "-e",
                'tell application "System Events" to tell process "SystemUIServer" to click menu bar item "Spotlight" of menu bar 1'
            ], check=True, timeout=5)
            time.sleep(1)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        
        return False
    
    def wait_for_window(self, window_name: str, timeout: float = None) -> bool:
        """Wait for a window with the given name to appear."""
        if timeout is None:
            timeout = self.config.window_timeout
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Use osascript to check for window
                result = subprocess.run([
                    "osascript", 
                    "-e", 
                    f'tell application "System Events" to get name of every window of every process'
                ], capture_output=True, text=True, check=True)
                
                if window_name.lower() in result.stdout.lower():
                    return True
                    
            except subprocess.CalledProcessError:
                pass
            
            time.sleep(0.5)
        
        return False
    
    def get_window_bounds(self, app_name: str) -> Optional[Tuple[int, int, int, int]]:
        """Get window bounds for an application."""
        try:
            result = subprocess.run([
                "osascript",
                "-e",
                f'tell application "System Events" to get bounds of first window of application process "{app_name}"'
            ], capture_output=True, text=True, check=True)
            
            # Parse bounds: {x1, y1, x2, y2}
            bounds_str = result.stdout.strip().replace('{', '').replace('}', '')
            bounds = [int(x.strip()) for x in bounds_str.split(',')]
            
            if len(bounds) == 4:
                return tuple(bounds)
                
        except (subprocess.CalledProcessError, ValueError):
            pass
        
        return None
    
    def expand_path(self, path: str) -> str:
        """Expand user path (~/Downloads -> /Users/username/Downloads)."""
        return os.path.expanduser(path)
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        expanded_path = self.expand_path(path)
        return os.path.isfile(expanded_path)
    
    def _check_system_requirements(self) -> None:
        """Check system requirements and log warnings."""
        # Check if cliclick is available
        try:
            result = subprocess.run(["which", "cliclick"], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ Warning: cliclick not found. Install with: brew install cliclick")
        except Exception:
            print("⚠️ Warning: Cannot check cliclick availability")
        
        # Check if osascript is available
        try:
            result = subprocess.run(["which", "osascript"], capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️ Warning: osascript not found (this is unusual on macOS)")
        except Exception:
            print("⚠️ Warning: Cannot check osascript availability")
    
    def test_permissions(self) -> dict:
        """Test accessibility and automation permissions."""
        results = {
            'spotlight': False,
            'typing': False,
            'screenshot': False,
            'recommendations': []
        }
        
        # Test screenshot capability
        try:
            screenshot = self.take_screenshot()
            if len(screenshot) > 100:  # Basic check that we got actual data
                results['screenshot'] = True
        except Exception as e:
            results['recommendations'].append(
                "Enable Screen Recording permissions: System Preferences > Security & Privacy > Privacy > Screen Recording"
            )
        
        # Test Spotlight
        try:
            # Just try to execute the command, don't actually trigger it
            result = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to return true'],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                results['spotlight'] = True
            else:
                results['recommendations'].append(
                    "Enable Accessibility permissions: System Preferences > Security & Privacy > Privacy > Accessibility"
                )
        except Exception:
            results['recommendations'].append(
                "Enable Accessibility permissions and check that osascript is working"
            )
        
        # Test typing
        try:
            # Test with a safe, non-intrusive command
            result = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to return (count of processes)'],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0 and result.stdout.strip().isdigit():
                results['typing'] = True
        except Exception:
            pass
        
        return results
    
    def get_diagnostics(self) -> str:
        """Get diagnostic information for troubleshooting."""
        diagnostics = []
        
        # System info
        try:
            result = subprocess.run(["sw_vers"], capture_output=True, text=True)
            diagnostics.append(f"System: {result.stdout.strip()}")
        except Exception:
            diagnostics.append("System: Unknown")
        
        # Check tools
        tools = ['cliclick', 'osascript', 'screencapture']
        for tool in tools:
            try:
                result = subprocess.run(["which", tool], capture_output=True, text=True)
                if result.returncode == 0:
                    diagnostics.append(f"✅ {tool}: {result.stdout.strip()}")
                else:
                    diagnostics.append(f"❌ {tool}: Not found")
            except Exception:
                diagnostics.append(f"❓ {tool}: Cannot check")
        
        # Test permissions
        permissions = self.test_permissions()
        diagnostics.append(f"Permissions - Screenshot: {'✅' if permissions['screenshot'] else '❌'}")
        diagnostics.append(f"Permissions - Spotlight: {'✅' if permissions['spotlight'] else '❌'}")
        diagnostics.append(f"Permissions - Typing: {'✅' if permissions['typing'] else '❌'}")
        
        if permissions['recommendations']:
            diagnostics.append("Recommendations:")
            for rec in permissions['recommendations']:
                diagnostics.append(f"  - {rec}")
        
        return "\n".join(diagnostics)