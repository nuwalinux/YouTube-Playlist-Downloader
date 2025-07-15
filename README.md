YouTube Playlist Downloader
This repository contains two versions of a simple YouTube playlist (and single video) downloader: a Graphical User Interface (GUI) application and a Command-Line Interface (CLI) script. Both tools leverage yt-dlp to efficiently download videos from YouTube.

Features

GUI Application

User-Friendly Interface: Easy to use with a graphical window.
Playlist Loading: Load a YouTube playlist URL to see all video titles.
Individual Downloads: Download specific videos from the loaded list.
Download All: Option to download all videos in the playlist.
Progress Bars: Visual progress indicators for each downloading video.
Cancel Options: Cancel individual downloads or all active downloads.
Save Path Selector: Choose a custom directory to save your downloaded videos.
Right-Click Paste: Convenient right-click context menu for pasting URLs.
Copyright Footer: Includes copyright information.

CLI Script

Terminal-Based: Interact directly from your command line.
Playlist Loading: Enter a YouTube playlist URL to list all video titles.
Flexible Selection: Choose specific videos by number, ranges (e.g., 5-8), or download all.
Real-time Progress: Shows yt-dlp's download progress directly in the terminal.

Prerequisites

Before running either script, ensure you have the following installed on your system:

Python: Version 3.8 or higher is recommended.
Download from: python.org
Important: During Python installation on Windows, make sure to check the box that says "Add Python to PATH" or "Add Python to environment variables."

pip: This is Python's package installer and usually comes bundled with Python. You can verify its installation by running python -m pip --version in your terminal.

yt-dlp: The powerful video downloader that powers these scripts.
Install it using pip:
python -m pip install yt-dlp


CustomTkinter (for GUI application only): A modern Tkinter library for a nicer look.
Install it using pip:
python -m pip install customtkinter


How to Run the Applications

1. GUI Application (youtube_downloader.py)

This is the graphical version of the downloader.

Save the code: Save the GUI application code (from the last response, starting with import tkinter as tk...) into a file named youtube_downloader.py.

Open your terminal/command prompt: Navigate to the directory where you saved youtube_downloader.py.

cd path/to/your/folder

(Replace path/to/your/folder with the actual path, e.g., cd C:\Users\YourUsername\Desktop)

Run the script:

python youtube_downloader-gui.py or ./youtube_downloader-gui.py

A graphical window will appear. Paste your YouTube playlist or video URL, click "Load Playlist," and then choose your download options.

2. CLI Script (youtube_cli.py)

This is the command-line version of the downloader.

Save the code: Save the CLI script code (from the previous response, starting with import subprocess...) into a file named youtube_cli.py.

Open your terminal/command prompt: Navigate to the directory where you saved youtube_cli.py

cd path/to/your/folder

(Replace path/to/your/folder with the actual path)

Run the script:

python youtube_Download-cli.py or ./youtube_Download-cli.py

The script will prompt you directly in the terminal to enter a URL and guide you through the selection and download process.
