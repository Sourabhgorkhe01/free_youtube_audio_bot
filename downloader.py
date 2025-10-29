import os
import time
import random
import re
import tempfile
from yt_dlp import YoutubeDL
from config import DOWNLOAD_DIR

COOKIES_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Firefox/116.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) Chrome/115.0.0.0 Safari/537.36',
]

def sanitize_filename(filename):
    """Remove special characters and truncate long filenames"""
    if not filename:
        return "audio_download"
    
    # Remove invalid Windows characters and problematic symbols
    cleaned = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    # Remove leading/trailing spaces and dots
    cleaned = cleaned.strip().strip('.')
    # Truncate to 100 characters
    return cleaned[:100] if cleaned else "audio_download"

def download_audio(url: str, cancel_flag=None, proxy: str = None):
    def progress_hook(d):
        if cancel_flag and cancel_flag.is_set():
            raise Exception("Download cancelled by user.")

    # Create a temporary directory for downloads to avoid file locking issues
    temp_download_dir = tempfile.mkdtemp()
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(temp_download_dir, '%(title)s.%(ext)s'),  # Use temp directory
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'http_headers': {'User-Agent': random.choice(USER_AGENTS)},
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'verbose': True,
        'force-ipv4': True,
        'ratelimit': 1000000,
        'progress_hooks': [progress_hook],
        'writethumbnail': False,
        'nooverwrites': True,  # Prevent overwrite conflicts
        'continuedl': False,   # Disable continue download
        'nopart': True,        # Don't use .part files - this is key for Windows
    }

    if os.path.exists(COOKIES_FILE_PATH):
        ydl_opts['cookiefile'] = COOKIES_FILE_PATH
    if proxy:
        ydl_opts['proxy'] = proxy

    try:
        with YoutubeDL(ydl_opts) as ydl:
            start_time = time.time()
            info = ydl.extract_info(url, download=True)
            elapsed_time = time.time() - start_time
            
            if not info:
                raise Exception("Failed to extract video information")
            
            original_title = info.get('title', 'audio')
            sanitized_title = sanitize_filename(original_title)
            
            # Look for the downloaded file in the temp directory
            downloaded_files = []
            for file in os.listdir(temp_download_dir):
                if file.endswith('.mp3'):
                    downloaded_files.append(file)
            
            if not downloaded_files:
                # If no MP3 found, look for the original downloaded file
                for file in os.listdir(temp_download_dir):
                    if file.endswith(('.mp4', '.webm', '.m4a', '.opus')):
                        downloaded_files.append(file)
            
            if not downloaded_files:
                raise FileNotFoundError("No downloaded files found")
            
            # Use the first found file
            temp_file_path = os.path.join(temp_download_dir, downloaded_files[0])
            final_filename = os.path.join(DOWNLOAD_DIR, f"{sanitized_title}.mp3")
            
            # Move the file from temp directory to final destination
            import shutil
            shutil.move(temp_file_path, final_filename)
            
            # Clean up temp directory
            shutil.rmtree(temp_download_dir, ignore_errors=True)
            
            if os.path.exists(final_filename):
                return final_filename, original_title, elapsed_time
            else:
                raise FileNotFoundError("File move failed")
            
    except Exception as e:
        # Clean up temp directory on error
        import shutil
        shutil.rmtree(temp_download_dir, ignore_errors=True)
        
        if cancel_flag and cancel_flag.is_set():
            raise Exception("Download cancelled by user")
        else:
            raise e

def download_video(url: str, cancel_flag=None, proxy: str = None):
    def progress_hook(d):
        if cancel_flag and cancel_flag.is_set():
            raise Exception("Download cancelled by user.")

    # Create a temporary directory for downloads
    temp_download_dir = tempfile.mkdtemp()
    
    ydl_opts = {
        'format': 'best[height<=720]',  # Simpler format selection
        'outtmpl': os.path.join(temp_download_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'http_headers': {'User-Agent': random.choice(USER_AGENTS)},
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'verbose': True,
        'force-ipv4': True,
        'ratelimit': 1000000,
        'progress_hooks': [progress_hook],
        'writethumbnail': False,
        'nooverwrites': True,
        'continuedl': False,
        'nopart': True,  # Critical for Windows file locking issues
    }

    if os.path.exists(COOKIES_FILE_PATH):
        ydl_opts['cookiefile'] = COOKIES_FILE_PATH
    if proxy:
        ydl_opts['proxy'] = proxy

    try:
        with YoutubeDL(ydl_opts) as ydl:
            start_time = time.time()
            info = ydl.extract_info(url, download=True)
            elapsed_time = time.time() - start_time
            
            if not info:
                raise Exception("Failed to extract video information")
            
            original_title = info.get('title', 'video')
            sanitized_title = sanitize_filename(original_title)
            
            # Look for the downloaded file
            downloaded_files = []
            for file in os.listdir(temp_download_dir):
                if file.endswith(('.mp4', '.webm', '.mkv')):
                    downloaded_files.append(file)
            
            if not downloaded_files:
                raise FileNotFoundError("No downloaded video files found")
            
            # Use the first found file
            temp_file_path = os.path.join(temp_download_dir, downloaded_files[0])
            final_filename = os.path.join(DOWNLOAD_DIR, f"{sanitized_title}.mp4")
            
            # Move the file
            import shutil
            shutil.move(temp_file_path, final_filename)
            
            # Clean up temp directory
            shutil.rmtree(temp_download_dir, ignore_errors=True)
            
            if os.path.exists(final_filename):
                return final_filename, original_title, elapsed_time
            else:
                raise FileNotFoundError("File move failed")
            
    except Exception as e:
        # Clean up temp directory on error
        import shutil
        shutil.rmtree(temp_download_dir, ignore_errors=True)
        
        if cancel_flag and cancel_flag.is_set():
            raise Exception("Download cancelled by user")
        else:
            raise e