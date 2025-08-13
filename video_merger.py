import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import subprocess
import tempfile
import re
import logging

# Try to import pdfplumber first, fallback to PyPDF2
try:
    import pdfplumber
    PDF_LIB = 'pdfplumber'
except ImportError:
    try:
        import PyPDF2
        PDF_LIB = 'pypdf2'
    except ImportError:
        PDF_LIB = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Merger")
        self.root.geometry("600x500")
        
        # Variables to store file paths
        self.video_folder = tk.StringVar()
        self.pdf_file = tk.StringVar()
        self.output_file = tk.StringVar()
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Video folder selection
        ttk.Label(main_frame, text="Video Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.video_folder, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_video_folder).grid(row=0, column=2, pady=5)
        
        # PDF file selection
        ttk.Label(main_frame, text="PDF File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.pdf_file, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_pdf_file).grid(row=1, column=2, pady=5)
        
        # Output file selection
        ttk.Label(main_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self.browse_output_file).grid(row=2, column=2, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Status log
        ttk.Label(main_frame, text="Status Log:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        self.status_log = tk.Text(main_frame, height=15, width=70)
        self.status_log.grid(row=5, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for status log
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.status_log.yview)
        scrollbar.grid(row=5, column=3, sticky=(tk.N, tk.S))
        self.status_log.configure(yscrollcommand=scrollbar.set)
        
        # Merge button
        self.merge_button = ttk.Button(main_frame, text="Merge Videos", command=self.merge_videos)
        self.merge_button.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
    def browse_video_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.video_folder.set(folder)
            
    def browse_pdf_file(self):
        file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file:
            self.pdf_file.set(file)
            
    def browse_output_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".mp4", 
                                          filetypes=[("MP4 files", "*.mp4"), 
                                                    ("MKV files", "*.mkv"), 
                                                    ("MOV files", "*.mov"),
                                                    ("All files", "*.*")])
        if file:
            self.output_file.set(file)
            
    def log_message(self, message):
        self.status_log.insert(tk.END, message + "\n")
        self.status_log.see(tk.END)
        self.root.update_idletasks()
        
    def extract_filenames_from_pdf(self, pdf_path):
        """Extract filenames from PDF using pdfplumber or PyPDF2"""
        filenames = []
        
        if PDF_LIB == 'pdfplumber':
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            # Find potential filenames with extensions
                            matches = re.findall(r'\S+\.(mp4|mkv|mov|MP4|MKV|MOV)', text)
                            for match in matches:
                                # Extract the full filename
                                full_match = re.search(r'\S+\.' + match, text)
                                if full_match:
                                    filenames.append(full_match.group())
            except Exception as e:
                self.log_message(f"Error with pdfplumber: {str(e)}")
                
        elif PDF_LIB == 'pypdf2':
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            # Find potential filenames with extensions
                            matches = re.findall(r'\S+\.(mp4|mkv|mov|MP4|MKV|MOV)', text)
                            for match in matches:
                                # Extract the full filename
                                full_match = re.search(r'\S+\.' + match, text)
                                if full_match:
                                    filenames.append(full_match.group())
            except Exception as e:
                self.log_message(f"Error with PyPDF2: {str(e)}")
                
        else:
            self.log_message("No PDF library available. Please install pdfplumber or PyPDF2.")
            return []
            
        self.log_message(f"Found {len(filenames)} filenames in PDF: {filenames}")
        return filenames
        
    def find_matching_files(self, folder, filenames):
        """Find matching video files in the folder (case-insensitive)"""
        matched_files = []
        missing_files = []
        
        # Get all files in the folder
        folder_files = os.listdir(folder)
        folder_files_lower = [f.lower() for f in folder_files]
        
        for filename in filenames:
            filename_lower = filename.lower()
            if filename_lower in folder_files_lower:
                # Find the original case filename
                idx = folder_files_lower.index(filename_lower)
                matched_files.append(os.path.join(folder, folder_files[idx]))
            else:
                missing_files.append(filename)
                
        if missing_files:
            self.log_message(f"Warning: Missing files: {missing_files}")
            
        self.log_message(f"Matched {len(matched_files)} files out of {len(filenames)}")
        return matched_files, missing_files
        
    def copy_files_to_temp(self, files):
        """Copy files to temporary directory with sequential names"""
        temp_dir = tempfile.mkdtemp()
        copied_files = []
        
        self.log_message(f"Copying files to temporary directory: {temp_dir}")
        
        for i, file_path in enumerate(files, 1):
            # Get file extension
            _, ext = os.path.splitext(file_path)
            # Create new filename with leading zeros
            new_filename = f"{i:04d}{ext}"
            new_path = os.path.join(temp_dir, new_filename)
            
            try:
                shutil.copy2(file_path, new_path)
                copied_files.append(new_path)
                self.log_message(f"Copied {os.path.basename(file_path)} -> {new_filename}")
            except Exception as e:
                self.log_message(f"Error copying {file_path}: {str(e)}")
                
        return temp_dir, copied_files
        
    def create_concat_file(self, temp_dir, files):
        """Create FFmpeg concat list file"""
        concat_file = os.path.join(temp_dir, "concat_list.txt")
        
        with open(concat_file, 'w') as f:
            for file_path in files:
                # Use forward slashes for FFmpeg compatibility
                f.write(f"file '{file_path.replace('\\', '/')}'\n")
                
        return concat_file
        
    def run_ffmpeg_merge(self, concat_file, output_file):
        """Run FFmpeg to merge videos without re-encoding"""
        try:
            # Check if FFmpeg is available
            subprocess.run(["ffmpeg", "-version"], check=True, 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_message("Error: FFmpeg not found. Please install FFmpeg and add it to your PATH.")
            return False
            
        # FFmpeg command for concatenation without re-encoding
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            "-y",  # Overwrite output file without asking
            output_file
        ]
        
        self.log_message("Running FFmpeg merge command...")
        self.log_message(" ".join(cmd))
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                     universal_newlines=True)
            
            # Update progress bar
            self.progress["value"] = 0
            self.progress["maximum"] = 100
            
            # Wait for process to complete
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.log_message("Merge completed successfully!")
                return True
            else:
                self.log_message(f"FFmpeg error: {stderr}")
                return False
                
        except Exception as e:
            self.log_message(f"Error running FFmpeg: {str(e)}")
            return False
            
    def merge_videos(self):
        """Main function to merge videos"""
        # Validate inputs
        if not self.video_folder.get():
            messagebox.showerror("Error", "Please select a video folder.")
            return
            
        if not self.pdf_file.get():
            messagebox.showerror("Error", "Please select a PDF file.")
            return
            
        if not self.output_file.get():
            messagebox.showerror("Error", "Please select an output file.")
            return
            
        # Disable merge button during processing
        self.merge_button.config(state="disabled")
        self.progress["value"] = 0
        
        try:
            self.log_message("Starting video merge process...")
            
            # Step 1: Extract filenames from PDF
            self.log_message("Extracting filenames from PDF...")
            filenames = self.extract_filenames_from_pdf(self.pdf_file.get())
            
            if not filenames:
                self.log_message("No filenames found in PDF. Please check the PDF format.")
                return
                
            # Step 2: Find matching files
            self.log_message("Finding matching video files...")
            matched_files, missing_files = self.find_matching_files(self.video_folder.get(), filenames)
            
            if not matched_files:
                self.log_message("No matching video files found. Please check your video folder and PDF.")
                return
                
            # Step 3: Copy files to temp directory
            self.log_message("Organizing files...")
            temp_dir, copied_files = self.copy_files_to_temp(matched_files)
            
            # Step 4: Create concat file
            self.log_message("Creating merge list...")
            concat_file = self.create_concat_file(temp_dir, copied_files)
            
            # Step 5: Run FFmpeg merge
            self.log_message("Merging videos...")
            success = self.run_ffmpeg_merge(concat_file, self.output_file.get())
            
            if success:
                self.log_message("Video merge completed successfully!")
                messagebox.showinfo("Success", "Videos merged successfully!")
            else:
                self.log_message("Video merge failed. Please check the log for details.")
                messagebox.showerror("Error", "Video merge failed. Please check the log for details.")
                
        except Exception as e:
            self.log_message(f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            
        finally:
            # Re-enable merge button
            self.merge_button.config(state="normal")
            self.progress["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoMergerApp(root)
    root.mainloop()
