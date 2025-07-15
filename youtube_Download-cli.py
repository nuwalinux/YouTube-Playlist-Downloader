import subprocess
import json
import sys
import os
import re

def main():
    """Main function to run the command-line interface."""
    
    # Check if yt-dlp is installed
    try:
        subprocess.run(["yt-dlp", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Error: yt-dlp is not installed or not in your system's PATH.")
        print("Please install it by running: pip install yt-dlp")
        sys.exit(1)

    print("============================================")
    print("= YouTube Playlist Downloader (CLI)      =")
    print("============================================")
    
    while True:
        playlist_url = input("\nEnter YouTube Playlist URL (or 'exit' to quit): ")
        if playlist_url.lower() == 'exit':
            break

        print("\nFetching playlist info...")
        videos = fetch_playlist_info(playlist_url)

        if videos:
            selected_videos = prompt_for_selection(videos)
            if selected_videos:
                download_videos(selected_videos)
        else:
            print("Could not find any videos at that URL. Please try again.")

def fetch_playlist_info(url):
    """Fetches video titles and URLs from a playlist."""
    try:
        command = [
            "yt-dlp",
            "--flat-playlist",
            "-j",
            "--no-warnings", # Hide warnings for a cleaner output
            url
        ]
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )

        video_info_list = []
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                try:
                    video_json = json.loads(line)
                    video_info_list.append({
                        'title': video_json['title'],
                        'url': video_json['url']
                    })
                except json.JSONDecodeError:
                    pass # Ignore lines that are not valid JSON
        process.wait()

        return video_info_list

    except Exception as e:
        print(f"An error occurred while fetching info: {e}")
        return []

def prompt_for_selection(video_list):
    """Displays videos and prompts user for selection."""
    print("\n------------------ Videos Found ------------------")
    for i, video in enumerate(video_list, 1):
        print(f"[{i:2}] {video['title']}")
    print("--------------------------------------------------")
    
    while True:
        selection_input = input("\nEnter the number(s) to download (e.g., 1, 5, 8-10) or 'all': ").strip().lower()
        
        if selection_input == 'all':
            return video_list

        selected_indices = set()
        
        # Parse ranges and individual numbers
        parts = re.split(r'[,\s]+', selection_input)
        
        valid_input = True
        for part in parts:
            if not part:
                continue
            
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    if 1 <= start <= end <= len(video_list):
                        selected_indices.update(range(start, end + 1))
                    else:
                        print("Invalid range. Please enter valid numbers.")
                        valid_input = False
                        break
                except ValueError:
                    print("Invalid range format. Use numbers and a dash (e.g., 5-8).")
                    valid_input = False
                    break
            else:
                try:
                    index = int(part)
                    if 1 <= index <= len(video_list):
                        selected_indices.add(index)
                    else:
                        print("Invalid number. Please enter a valid number from the list.")
                        valid_input = False
                        break
                except ValueError:
                    print("Invalid input. Please use numbers or 'all'.")
                    valid_input = False
                    break
        
        if valid_input and selected_indices:
            return [video_list[i-1] for i in sorted(selected_indices)]
        else:
            if valid_input:
                print("No videos selected. Please try again.")

def download_videos(videos_to_download):
    """Downloads the selected videos."""
    for i, video in enumerate(videos_to_download, 1):
        print(f"\n[{i}/{len(videos_to_download)}] Starting download for: {video['title']}")
        
        try:
            command = ["yt-dlp", "--progress", video['url']]
            
            # Use Popen to show real-time progress
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                sys.stdout.write(line)
            
            process.wait()
            
            if process.returncode == 0:
                print(f"Download of '{video['title']}' completed successfully.")
            else:
                print(f"Download of '{video['title']}' failed.")
                
        except Exception as e:
            print(f"An error occurred during download: {e}")

if __name__ == "__main__":
    main()