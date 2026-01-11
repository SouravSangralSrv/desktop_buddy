import os
import subprocess
import webbrowser
from pathlib import Path
import glob
from core.browser_manager import BrowserManager
import datetime
import json

class SystemActions:
    """Handles system automation actions like file operations, app launching, and web actions"""
    
    def __init__(self):
        self.browser_manager = BrowserManager()
        
        self.common_apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'edge': 'msedge.exe',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
        }
        
        self.common_folders = {
            'documents': str(Path.home() / 'Documents'),
            'downloads': str(Path.home() / 'Downloads'),
            'pictures': str(Path.home() / 'Pictures'),
            'desktop': str(Path.home() / 'Desktop'),
            'music': str(Path.home() / 'Music'),
            'videos': str(Path.home() / 'Videos'),
        }
    
    def get_datetime_info(self):
        """Get current date, time, and timezone information"""
        try:
            now = datetime.datetime.now()
            tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
            
            result = f"📅 Current Date & Time:\n\n"
            result += f"Date: {now.strftime('%A, %B %d, %Y')}\n"
            result += f"Time: {now.strftime('%I:%M:%S %p')}\n"
            result += f"24-hour: {now.strftime('%H:%M:%S')}\n"
            result += f"Timezone: {tz}\n"
            result += f"Full: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            
            return result
        except Exception as e:
            return f"❌ Error getting date/time: {e}"
    
    def save_chat_message(self, sender, message):
        """Save chat message to backup log"""
        try:
            # Create chat logs directory
            log_dir = str(Path.home() / 'Documents' / 'DesktopBuddy_ChatLogs')
            os.makedirs(log_dir, exist_ok=True)
            
            # Create log file for today
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            log_file = os.path.join(log_dir, f'chat_{today}.json')
            
            # Load existing messages
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
            else:
                messages = []
            
            # Add new message
            messages.append({
                'timestamp': datetime.datetime.now().isoformat(),
                'sender': sender,
                'message': message
            })
            
            # Save back
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Error saving chat: {e}")
            return False
    
    def open_file(self, path):
        """Open a file with its default application"""
        try:
            if os.path.exists(path):
                os.startfile(path)
                return f"✅ Opened {path}"
            else:
                return f"❌ File not found: {path}"
        except Exception as e:
            return f"❌ Error opening file: {e}"
    
    def open_folder(self, folder_name_or_path):
        """Open a folder in Windows Explorer"""
        try:
            # Check if it's a common folder name
            if folder_name_or_path.lower() in self.common_folders:
                path = self.common_folders[folder_name_or_path.lower()]
            else:
                path = folder_name_or_path
            
            if os.path.exists(path):
                os.startfile(path)
                return f"✅ Opened folder: {path}"
            else:
                return f"❌ Folder not found: {path}"
        except Exception as e:
            return f"❌ Error opening folder: {e}"
    
    def search_files(self, query, directory=None, file_type=None):
        """Search for files by name with exact path results"""
        try:
            if directory is None:
                # Search in common user directories
                search_dirs = [
                    str(Path.home() / 'Documents'),
                    str(Path.home() / 'Downloads'),
                    str(Path.home() / 'Desktop'),
                    str(Path.home() / 'Music'),
                    str(Path.home() / 'Videos'),
                    str(Path.home() / 'Pictures'),
                ]
            else:
                search_dirs = [directory]
            
            all_matches = []
            
            for search_dir in search_dirs:
                if not os.path.exists(search_dir):
                    continue
                
                # Search with glob pattern
                pattern = f"**/*{query}*"
                try:
                    matches = list(Path(search_dir).glob(pattern))
                    
                    # Filter by file type if specified
                    if file_type:
                        extensions = {
                            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
                            'audio': ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg'],
                            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
                            'document': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx']
                        }
                        
                        if file_type.lower() in extensions:
                            matches = [m for m in matches if m.suffix.lower() in extensions[file_type.lower()]]
                    
                    all_matches.extend(matches)
                except Exception as e:
                    print(f"Error searching {search_dir}: {e}")
                    continue
            
            # Limit to 10 results
            all_matches = all_matches[:10]
            
            if all_matches:
                result = f"✅ Found {len(all_matches)} file(s) for '{query}':\n\n"
                for i, match in enumerate(all_matches, 1):
                    file_size = match.stat().st_size if match.is_file() else 0
                    size_str = self._format_file_size(file_size)
                    result += f"{i}. {match.name}\n"
                    result += f"   📁 Path: {str(match)}\n"
                    result += f"   📊 Size: {size_str}\n"
                    result += f"   📅 Type: {match.suffix or 'Folder'}\n\n"
                return result
            else:
                return f"❌ No files found matching '{query}'"
        except Exception as e:
            return f"❌ Error searching files: {e}"
    
    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def play_media(self, file_path=None, search_query=None):
        """Play media files (video/audio) from local system"""
        try:
            if file_path:
                # Direct file path provided
                if os.path.exists(file_path):
                    os.startfile(file_path)
                    return f"▶️ Playing: {Path(file_path).name}"
                else:
                    return f"❌ File not found: {file_path}"
            
            elif search_query:
                # Search for media file
                result = self.search_files(search_query, file_type='video')
                if "Found 0" in result or "No files" in result:
                    # Try audio
                    result = self.search_files(search_query, file_type='audio')
                
                # Extract first file path from result
                if "Path:" in result:
                    lines = result.split('\n')
                    for line in lines:
                        if 'Path:' in line:
                            path = line.split('Path:')[1].strip()
                            if os.path.exists(path):
                                os.startfile(path)
                                return f"▶️ Playing: {Path(path).name}"
                
                return f"❌ No media file found for '{search_query}'"
            
            return "❌ Please provide a file path or search query"
            
        except Exception as e:
            return f"❌ Error playing media: {e}"
    
    def open_application(self, app_name):
        """Launch an application by name"""
        try:
            app_name_lower = app_name.lower()
            
            # Check common apps
            if app_name_lower in self.common_apps:
                app_path = self.common_apps[app_name_lower]
                subprocess.Popen(app_path, shell=True)
                return f"✅ Launched {app_name}"
            else:
                # Try to launch directly
                subprocess.Popen(app_name, shell=True)
                return f"✅ Attempted to launch {app_name}"
        except Exception as e:
            return f"❌ Error launching application: {e}"
    
    def open_youtube(self, query=None):
        """Open YouTube, optionally with a search query - REUSES TAB"""
        try:
            if query:
                return self.browser_manager.open_youtube(query)
            else:
                webbrowser.open("https://www.youtube.com")
                return "🎵 Opened YouTube"
        except Exception as e:
            return f"❌ Error opening YouTube: {e}"
    
    def play_music(self, query):
        """Play music by searching on YouTube - REUSES TAB"""
        return self.browser_manager.open_youtube(query)
    
    def google_search(self, query):
        """Perform a Google search - REUSES TAB"""
        try:
            return self.browser_manager.open_google(query)
        except Exception as e:
            return f"❌ Error performing Google search: {e}"
    
    def open_website(self, url):
        """Open any website URL - REUSES TAB"""
        try:
            return self.browser_manager.open_website(url)
        except Exception as e:
            return f"❌ Error opening website: {e}"
    
    def execute_action(self, action_type, params):
        """Execute an action based on type and parameters"""
        action_map = {
            'open_file': lambda: self.open_file(params.get('path', '')),
            'open_folder': lambda: self.open_folder(params.get('folder', '')),
            'search_files': lambda: self.search_files(
                params.get('query', ''), 
                params.get('directory'),
                params.get('file_type')
            ),
            'play_media': lambda: self.play_media(
                params.get('file_path'),
                params.get('search_query')
            ),
            'get_datetime': lambda: self.get_datetime_info(),
            'open_app': lambda: self.open_application(params.get('app', '')),
            'youtube': lambda: self.open_youtube(params.get('query')),
            'play_music': lambda: self.play_music(params.get('query', '')),
            'google': lambda: self.google_search(params.get('query', '')),
            'open_website': lambda: self.open_website(params.get('url', '')),
        }
        
        if action_type in action_map:
            return action_map[action_type]()
        else:
            return f"❌ Unknown action: {action_type}"
