# 🔐 macOS Permissions Setup for OrcaSheets Framework

The OrcaSheets framework requires specific macOS permissions to automate UI interactions. Follow this guide to set them up properly.

## 🚨 Required Permissions

### 1. Accessibility Permissions ⚡️ **CRITICAL**
**Required for**: Keyboard input, mouse clicks, UI automation

**Setup Steps**:
1. Open **System Preferences** (or **System Settings** on newer macOS)
2. Go to **Security & Privacy** > **Privacy**
3. Click **Accessibility** in the left sidebar
4. Click the **lock icon** 🔒 to make changes (enter your password)
5. Click the **+** button
6. Add **Terminal** (or your terminal app like iTerm2)
7. Make sure the checkbox next to Terminal is **checked** ✅
8. **Restart your terminal** for changes to take effect

### 2. Screen Recording Permissions 📸 **RECOMMENDED**
**Required for**: Taking screenshots for automation feedback

**Setup Steps**:
1. In **System Preferences** > **Security & Privacy** > **Privacy**
2. Click **Screen Recording** in the left sidebar
3. Click the **+** button
4. Add **Terminal** (or your terminal app)
5. Make sure the checkbox is **checked** ✅

## 🧪 Test Your Permissions

Run the diagnostic test to verify everything is working:

```bash
python3 test_ui_automation.py
```

**Expected Output** (when permissions are correct):
```
✅ cliclick: /opt/homebrew/bin/cliclick
✅ osascript: /usr/bin/osascript
✅ screencapture: /usr/sbin/screencapture
Permissions - Screenshot: ✅
Permissions - Spotlight: ✅
Permissions - Typing: ✅
```

## 🐛 Troubleshooting Permission Issues

### Error: "osascript is not allowed to send keystrokes"
**Solution**: Add Terminal to Accessibility permissions (see step 1 above)

### Error: "Accessibility privileges not enabled"
**Solution**: 
1. Add Terminal to Accessibility permissions
2. **Restart Terminal completely** (close all windows and reopen)
3. Try again

### Error: Screenshot fails
**Solution**: Add Terminal to Screen Recording permissions

### Permission dialog keeps appearing
**Solution**: 
1. Remove Terminal from the permissions list
2. Re-add it
3. Restart Terminal

## 🔄 Alternative Setup Method

If you're having trouble finding the right settings:

### macOS Monterey/Ventura/Sonoma:
1. Open **System Settings**
2. Click **Privacy & Security** in sidebar
3. Click **Accessibility**
4. Toggle on your Terminal app

### Or use command line:
```bash
# Open System Preferences directly to Privacy settings
open "x-apple.systempreferences:com.apple.preference.security?Privacy"
```

## 🚀 Quick Permission Test

Run this quick test to check if accessibility is working:

```bash
# This should return a number (count of processes)
osascript -e 'tell application "System Events" to return (count of processes)'
```

If you get an error about permissions, follow the setup steps above.

## 🛠️ Advanced: Granting Permissions Programmatically

For enterprise deployments, you can use profiles or MDM to grant permissions:

```bash
# Example: Check current accessibility permissions
sqlite3 /Library/Application\ Support/com.apple.TCC/TCC.db \
  "SELECT client FROM access WHERE service='kTCCServiceAccessibility';"
```

## ✅ Verification Checklist

Before using the OrcaSheets framework:

- [ ] Terminal added to Accessibility permissions
- [ ] Terminal added to Screen Recording permissions  
- [ ] Terminal completely restarted
- [ ] `python3 test_ui_automation.py` shows all ✅
- [ ] `osascript -e 'tell application "System Events" to return true'` works

## 🔒 Security Notes

- These permissions allow the terminal to control your computer
- Only grant permissions to trusted applications
- The OrcaSheets framework is restricted to OrcaSheets-only operations
- You can revoke permissions at any time in System Preferences

## 📞 Still Having Issues?

1. **Restart your Mac** - Sometimes permissions need a full restart
2. **Check macOS version** - Some older versions have different paths
3. **Try different terminal app** - iTerm2, Terminal.app, etc.
4. **Run diagnostics**: `python3 test_ui_automation.py`

Once permissions are set up correctly, the OrcaSheets framework will work seamlessly! 🎉