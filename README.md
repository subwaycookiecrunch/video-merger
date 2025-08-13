# Video Merger Application

This application allows users to merge video files in a specific order defined by a PDF document. It extracts filenames from the PDF, arranges the videos accordingly, and merges them using FFmpeg without re-encoding to preserve quality.

## Features

- Simple GUI with Tkinter for easy interaction
- Extracts video filenames from PDF documents using pdfplumber or PyPDF2
- Arranges videos in the exact order they appear in the PDF
- Merges videos using FFmpeg without re-encoding to preserve original quality
- Handles large files efficiently (tested with files up to 50GB)
- Cross-platform support for Windows and macOS
- Progress tracking and detailed logging
- Error handling for missing files with warnings

## Requirements

- Python 3.6 or higher
- FFmpeg installed and accessible from the command line
- Required Python packages (see `requirements.txt`)

## Installation

1. Install Python 3.6+ from [python.org](https://www.python.org/downloads/)

2. Install FFmpeg:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: Install with Homebrew: `brew install ffmpeg`

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python video_merger.py
```

1. Click "Browse..." next to "Video Folder" to select the folder containing your video files
2. Click "Browse..." next to "PDF File" to select the PDF containing the video filenames
3. Click "Browse..." next to "Output File" to choose where to save the merged video
4. Click "Merge Videos" to start the process

### PDF Format Requirements

The PDF should contain the exact filenames of the videos you want to merge, including their extensions (e.g., `video1.mp4`, `scene2.mkv`). The order of filenames in the PDF will determine the order of videos in the merged output.

### Supported Video Formats

- MP4
- MKV
- MOV

The application will preserve the format of the first video in the sequence for the output file.

## Creating a Standalone Executable

To create a standalone executable using PyInstaller:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Create the executable:
   ```bash
   pyinstaller --onefile --windowed video_merger.py
   ```

This will create a `dist` folder containing the standalone executable.

### PyInstaller Options Explained

- `--onefile`: Creates a single executable file
- `--windowed`: Prevents the console window from appearing (Windows/macOS)

On Windows, you may need to specify additional options to include required libraries:
```bash
pyinstaller --onefile --windowed --hidden-import=tkinter video_merger.py
```

## How It Works

1. **PDF Text Extraction**: The application uses pdfplumber (preferred) or PyPDF2 to extract text from the PDF and identify video filenames.

2. **File Matching**: It matches the extracted filenames with files in the selected video folder (case-insensitive).

3. **Temporary File Organization**: Matching video files are copied to a temporary directory with sequential numeric names (0001.mp4, 0002.mkv, etc.) to ensure correct ordering.

4. **FFmpeg Concatenation**: A merge list file is created and passed to FFmpeg with the concat demuxer to merge videos without re-encoding.

5. **Output**: The merged video is saved to the specified output location in original quality.

## Error Handling

- Missing files are reported with warnings but won't stop the process
- FFmpeg errors are displayed in the status log
- Dependency checks ensure required libraries are installed

## Limitations

- The application requires FFmpeg to be installed separately
- PDF parsing depends on text extraction capabilities of pdfplumber/PyPDF2
- Very large files may require significant temporary disk space

## Troubleshooting

### FFmpeg Not Found

Ensure FFmpeg is installed and added to your system PATH. You can test this by running `ffmpeg -version` in your terminal/command prompt.

### No Filenames Detected

- Check that the PDF contains actual text (not images of text)
- Verify that filenames include extensions (.mp4, .mkv, .mov)
- Try selecting a different PDF file

### Videos Not Merging

- Ensure all videos have the same codec or compatible formats
- Check that FFmpeg has permission to access the files
- Verify sufficient disk space for temporary files

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Uses pdfplumber/PyPDF2 for PDF text extraction
- Uses FFmpeg for video processing
- Built with Python and Tkinter
