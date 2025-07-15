import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import customtkinter as ctk
import subprocess
import threading
import json
import os
import sys
import re

# Main application class
class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("Nuwan's Playlist Downloader")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        # --- Variables ---
        self.download_processes = {}
        self.video_widgets = {}
        self.is_fetching = False
        self.download_path = os.getcwd() # Set default download path to current directory

        # --- GUI Elements ---
        self.create_widgets()

        # --- Start monitoring downloads ---
        self.after(100, self.monitor_downloads)

    def create_widgets(self):
        # Header Frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=10, fill=tk.X)

        ctk.CTkLabel(header_frame, text="Playlist URL:", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)

        self.url_entry = ctk.CTkEntry(header_frame, width=500)
        self.url_entry.pack(side=tk.LEFT, padx=5, expand=True)

        self.load_button = ctk.CTkButton(
            header_frame,
            text="Load Playlist",
            command=self.start_fetch_thread,
            font=("Arial", 12, "bold")
        )
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Download Path Selector
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(pady=5, fill=tk.X)
        
        self.path_label = ctk.CTkLabel(path_frame, text=f"Save to: {self.download_path}", font=("Arial", 10), text_color="gray")
        self.path_label.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.path_button = ctk.CTkButton(
            path_frame,
            text="Change Folder",
            command=self.select_download_path,
            font=("Arial", 10, "bold"),
            width=120
        )
        self.path_button.pack(side=tk.RIGHT, padx=5)

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Paste a playlist URL and click 'Load Playlist'.", font=("Arial", 12))
        self.status_label.pack(pady=10)

        # Video List Frame (Scrollable)
        self.video_list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.video_list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Control Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        self.download_all_button = ctk.CTkButton(
            button_frame,
            text="Download All",
            command=self.download_all,
            state=tk.DISABLED,
            font=("Arial", 12, "bold")
        )
        self.download_all_button.pack(side=tk.LEFT, padx=10)

        self.cancel_all_button = ctk.CTkButton(
            button_frame,
            text="Cancel All",
            command=self.cancel_all,
            state=tk.DISABLED,
            fg_color="red",
            hover_color="#c70000",
            font=("Arial", 12, "bold")
        )
        self.cancel_all_button.pack(side=tk.LEFT, padx=10)

        # Footer
        self.footer_label = ctk.CTkLabel(self, text="Nuwan Kaushalya © 2025", text_color="gray")
        self.footer_label.pack(side=tk.BOTTOM, pady=5)
        
        # Call the new function to create the right-click menu
        self.create_context_menu()

    def select_download_path(self):
        """Opens a file dialog to select the download directory."""
        selected_path = filedialog.askdirectory()
        if selected_path:
            self.download_path = selected_path
            self.path_label.configure(text=f"Save to: {self.download_path}")

    def create_context_menu(self):
        """Creates and binds the right-click context menu for the URL entry."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Cut", command=lambda: self.url_entry.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Copy", command=lambda: self.url_entry.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Paste", command=self.paste_from_clipboard)

        # Bind the right-click event to the URL entry widget
        self.url_entry.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Displays the context menu at the mouse cursor position."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def paste_from_clipboard(self):
        """Gets content from the clipboard and pastes it into the URL entry."""
        try:
            clipboard_content = self.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_content)
        except tk.TclError:
            # Handle cases where clipboard is empty or non-text content
            pass

    def start_fetch_thread(self):
        if self.is_fetching:
            return
        
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return

        self.is_fetching = True
        self.load_button.configure(state=tk.DISABLED)
        self.status_label.configure(text="Fetching playlist titles...")
        
        # Clear previous widgets
        for widget in self.video_list_frame.winfo_children():
            widget.destroy()

        fetch_thread = threading.Thread(target=self.fetch_playlist_titles, args=(url,))
        fetch_thread.start()

    def fetch_playlist_titles(self, url):
        try:
            command = ["yt-dlp", "--flat-playlist", "-j", url]
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )

            self.video_info_list = []
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    try:
                        video_json = json.loads(line)
                        self.video_info_list.append({
                            'title': video_json['title'],
                            'url': video_json['url']
                        })
                    except json.JSONDecodeError:
                        self.status_label.configure(text=f"Error parsing JSON: {line.strip()}")
            process.wait()

            self.after(0, self.display_videos)

        except Exception as e:
            # CORRECTED LINE: Pass 'e' as an argument to the lambda
            self.after(0, lambda error_msg=e: messagebox.showerror("Error", f"Failed to fetch playlist: {error_msg}"))
        finally:
            self.is_fetching = False
            self.load_button.configure(state=tk.NORMAL)

    def display_videos(self):
        if self.video_info_list:
            self.status_label.configure(text=f"Found {len(self.video_info_list)} videos. Ready to download.")
            self.download_all_button.configure(state=tk.NORMAL)
            
            for video_info in self.video_info_list:
                video_url = video_info['url']
                row_frame = ctk.CTkFrame(self.video_list_frame, fg_color="transparent")
                row_frame.pack(fill=tk.X, pady=2, padx=5)

                ctk.CTkLabel(row_frame, text=video_info['title'], anchor="w", font=("Arial", 12)).pack(side=tk.LEFT, padx=5, expand=True)

                status_label = ctk.CTkLabel(row_frame, text="", fg_color="transparent", font=("Arial", 10))
                status_label.pack(side=tk.LEFT, padx=5)
                
                progress_bar = ctk.CTkProgressBar(row_frame, orientation="horizontal", width=150)
                progress_bar.set(0)
                progress_bar.pack(side=tk.LEFT, padx=5)

                # Download button
                download_button = ctk.CTkButton(
                    row_frame,
                    text="Download",
                    command=lambda url=video_url: self.start_single_download(url),
                    font=("Arial", 12, "bold"),
                    width=100
                )
                download_button.pack(side=tk.RIGHT, padx=5)

                # NEW: Cancel button
                cancel_button = ctk.CTkButton(
                    row_frame,
                    text="Cancel",
                    command=lambda url=video_url: self.cancel_single_download(url),
                    state=tk.DISABLED,
                    fg_color="red",
                    hover_color="#c70000",
                    width=60,
                    font=("Arial", 10, "bold")
                )
                cancel_button.pack(side=tk.RIGHT, padx=5)
                
                self.video_widgets[video_url] = {
                    'status_label': status_label,
                    'progress_bar': progress_bar,
                    'download_button': download_button,
                    'cancel_button': cancel_button, # Store reference to the new button
                }
        else:
            self.status_label.configure(text="No videos found in playlist.")
            self.download_all_button.configure(state=tk.DISABLED)

    def start_single_download(self, video_url):
        if video_url in self.download_processes:
            return
        
        self.download_all_button.configure(state=tk.DISABLED)
        self.cancel_all_button.configure(state=tk.NORMAL)
        
        widgets = self.video_widgets[video_url]
        widgets['download_button'].configure(state=tk.DISABLED)
        widgets['cancel_button'].configure(state=tk.NORMAL) # Enable cancel button
        widgets['status_label'].configure(text="Starting...")

        download_thread = threading.Thread(target=self.run_download, args=(video_url,))
        download_thread.start()

    def run_download(self, video_url):
        try:
            widgets = self.video_widgets[video_url]
            # Use the selected download path in the command
            output_template = os.path.join(self.download_path, "%(title)s.%(ext)s")
            command = ["yt-dlp", "--progress", "-o", output_template, video_url]
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.download_processes[video_url] = process
            process.wait()

        except Exception as e:
            widgets['status_label'].configure(text=f"Error: {e}")
        finally:
            if video_url in self.download_processes:
                del self.download_processes[video_url]
            widgets['download_button'].configure(state=tk.NORMAL)
            widgets['cancel_button'].configure(state=tk.DISABLED)

    def download_all(self):
        self.download_all_button.configure(state=tk.DISABLED)
        self.cancel_all_button.configure(state=tk.NORMAL)
        
        for video_info in self.video_info_list:
            video_url = video_info['url']
            if video_url not in self.download_processes:
                self.start_single_download(video_url)

    def cancel_single_download(self, video_url):
        if video_url in self.download_processes:
            process = self.download_processes[video_url]
            process.terminate()
            
    def cancel_all(self):
        self.status_label.configure(text="Cancelling all downloads...")
        
        keys_to_delete = list(self.download_processes.keys())
        for video_url in keys_to_delete:
            process = self.download_processes[video_url]
            process.terminate()
            
        self.download_all_button.configure(state=tk.NORMAL)
        self.cancel_all_button.configure(state=tk.DISABLED)

    def monitor_downloads(self):
        progress_regex = re.compile(r'\[download\]\s+(\d+\.\d+)%')
        
        for video_url, process in list(self.download_processes.items()):
            widgets = self.video_widgets[video_url]
            
            # Read non-blocking output
            line = process.stdout.readline()
            if line:
                match = progress_regex.search(line)
                if match:
                    try:
                        percentage = float(match.group(1)) / 100.0
                        widgets['progress_bar'].set(percentage)
                        widgets['status_label'].configure(text=f"Downloading: {percentage:.1f}%")
                    except (ValueError, IndexError):
                        widgets['status_label'].configure(text="Downloading...")
                else:
                    widgets['status_label'].configure(text=line.strip())

            # Check if process is finished
            if process.poll() is not None:
                if process.returncode == 0:
                    widgets['status_label'].configure(text="Download Complete!")
                    widgets['progress_bar'].set(1.0)
                else:
                    widgets['status_label'].configure(text="Download Failed!")
                
                # The finally block in run_download handles removal from dict and UI reset
                
        # Check if all downloads are complete
        if not self.download_processes and self.download_all_button.cget("state") == tk.DISABLED:
             self.download_all_button.configure(state=tk.NORMAL)
             self.cancel_all_button.configure(state=tk.DISABLED)

        # Reschedule the next check
        self.after(100, self.monitor_downloads)

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
