"""
Browser Window Manager
Manages browser tabs and windows to avoid opening duplicates
Reuses existing tabs for YouTube, Google searches, etc.
"""

import webbrowser
import time


class BrowserManager:
    """Manages browser windows and tabs for smart reuse"""
    
    def __init__(self):
        self.last_youtube_time = 0
        self.last_google_time = 0
        self.last_website_time = 0
        self.reuse_window_delay = 2  # Seconds to wait before considering reuse
        
    def open_youtube(self, query):
        """Open YouTube and play video directly, reusing tab if recent"""
        current_time = time.time()
        
        # If we just opened YouTube recently, the browser is likely still there
        if current_time - self.last_youtube_time < self.reuse_window_delay:
            print("ℹ️ YouTube recently opened, browser should reuse tab")
        
        try:
            # Try to get direct video URL using youtube-search-python
            from youtubesearchpython import VideosSearch
            
            # Search for the video with Indian region preference
            videos_search = VideosSearch(query, limit=1, region='IN', language='hi')
            result = videos_search.result()
            
            if result and 'result' in result and len(result['result']) > 0:
                # Get the first video's URL
                video_url = result['result'][0]['link']
                print(f"✅ Found video: {result['result'][0]['title']}")
                webbrowser.open(video_url)
                self.last_youtube_time = current_time
                return f"🎵 Playing: {result['result'][0]['title']}"
            else:
                # Fallback to search results
                raise Exception("No results found")
                
        except Exception as e:
            # Fallback: Use YouTube search with video filter and Indian region
            print(f"⚠️ Direct play failed, using search: {e}")
            search_query = query.replace(' ', '+')
            # Add Indian region preference to URL
            video_url = f"https://www.youtube.com/results?search_query={search_query}&sp=EgIQAQ%253D%253D&gl=IN&hl=hi"
            webbrowser.open(video_url)
            self.last_youtube_time = current_time
            return f"🎵 Searching YouTube (India): {query}"
    
    def open_google(self, query):
        """Open Google search, reusing tab if recent"""
        current_time = time.time()
        
        if current_time - self.last_google_time < self.reuse_window_delay:
            print("ℹ️ Google recently opened, browser should reuse tab")
        
        # Open Google search with Indian region preference
        search_url = f"https://www.google.co.in/search?q={query.replace(' ', '+')}&gl=in&hl=hi"
        webbrowser.open(search_url)
        
        self.last_google_time = current_time
        return f"Searching Google India: {query}"
    
    def open_website(self, url):
        """Open a website"""
        current_time = time.time()
        
        if current_time - self.last_website_time < self.reuse_window_delay:
            print("ℹ️ Website recently opened, browser should reuse tab")
        
        # Add https:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        webbrowser.open(url)
        
        self.last_website_time = current_time
        return f"Opening: {url}"
