"""
Web Search Integration using DuckDuckGo (Free API)
Provides real-time knowledge and current information
"""

from duckduckgo_search import DDGS


class WebSearchHandler:
    """Handles web searches using free DuckDuckGo API"""
    
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query, max_results=3):
        """
        Search the web for current information
        
        Args:
            query: Search query
            max_results: Number of results to return
            
        Returns:
            Formatted search results
        """
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            
            if not results:
                return "Sorry, I couldn't find any information about that."
            
            # Format results
            response = f"Here's what I found about '{query}':\n\n"
            
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                snippet = result.get('body', 'No description')
                url = result.get('href', '')
                
                response += f"{i}. **{title}**\n"
                response += f"   {snippet}\n"
                if url:
                    response += f"   Source: {url}\n"
                response += "\n"
            
            return response.strip()
            
        except Exception as e:
            return f"I had trouble searching for that. Error: {str(e)}"
    
    def get_instant_answer(self, query):
        """Get instant answer for factual questions"""
        try:
            answer = self.ddgs.answers(query)
            if answer:
                return answer[0].get('text', 'No answer found')
            return None
        except:
            return None
