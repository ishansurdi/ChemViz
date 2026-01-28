# Building ChemViz Desktop Executable

## Prerequisites

1. **Install dependencies:**
```powershell
cd desktop
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Build the Executable

### Option 1: Using PyInstaller Directly (Quick)
```powershell
pyinstaller --onefile --windowed --name="ChemViz-Desktop" main.py
```

### Option 2: Using Spec File (Recommended - More Control)
```powershell
pyinstaller ChemViz-Desktop.spec
```

## Output

The executable will be created in:
```
desktop/dist/ChemViz-Desktop.exe
```

**File size:** ~150-200 MB (includes Python runtime, PyQt5, Matplotlib)

## Distribution

1. **Locate the .exe:**
   ```
   C:\Users\Admin\Desktop\Restart\Projects\Fosse\desktop\dist\ChemViz-Desktop.exe
   ```

2. **Test it:**
   - Double-click `ChemViz-Desktop.exe`
   - It will connect to production backend automatically
   - No Python installation needed on target PC!

3. **Upload to GitHub Releases:**
   - Go to: https://github.com/ishansurdi/ChemViz/releases/new
   - Create new release (e.g., v1.0.0)
   - Upload `ChemViz-Desktop.exe`
   - Users can download directly

## Adding Download Link to Web Dashboard

Add this button to your React dashboard:

```jsx
<a 
  href="https://github.com/ishansurdi/ChemViz/releases/latest/download/ChemViz-Desktop.exe"
  className="btn btn-primary"
>
  📥 Download Desktop App (Windows)
</a>
```

## Configuration

**Default:** Connects to production backend
```
https://chemviz-backend-i9o3.onrender.com/api
```

**For local testing:** Set environment variable before running
```powershell
$env:CHEMVIZ_API_URL="http://127.0.0.1:8000/api"
.\ChemViz-Desktop.exe
```

## System Requirements

- **OS:** Windows 10/11 (64-bit)
- **RAM:** 2 GB minimum
- **Disk:** 200 MB free space
- **Internet:** Required (connects to cloud backend)

## Troubleshooting

**Antivirus blocks .exe?**
- PyInstaller executables sometimes trigger false positives
- Add exception or get code-signing certificate

**Slow first run?**
- Backend on Render free tier sleeps after 15 min inactivity
- First request wakes it up (~30 seconds delay)

**Connection errors?**
- Check internet connection
- Verify backend is online: https://chemviz-backend-i9o3.onrender.com/api/health/

## Building for macOS/Linux

**macOS:**
```bash
pyinstaller --onefile --windowed --name="ChemViz-Desktop" main.py
```
Output: `dist/ChemViz-Desktop.app`

**Linux:**
```bash
pyinstaller --onefile --name="ChemViz-Desktop" main.py
```
Output: `dist/ChemViz-Desktop` (binary)

---

## Complete Build & Release Process

```powershell
# 1. Activate venv
cd desktop
.\venv\Scripts\Activate.ps1

# 2. Install/update dependencies
pip install -r requirements.txt

# 3. Build executable
pyinstaller ChemViz-Desktop.spec

# 4. Test it
.\dist\ChemViz-Desktop.exe

# 5. Upload to GitHub Releases
# Go to GitHub and create release with the .exe file
```
