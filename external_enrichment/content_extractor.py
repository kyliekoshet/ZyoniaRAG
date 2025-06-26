"""
Content extraction module for getting meaningful snippets from web pages.
Replaces poor quality search engine snippets with actual scraped content.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentExtractor:
    """Extracts meaningful content snippets from web pages."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
        
        # Sites that commonly block scrapers
        self.blocked_domains = {
            'tripadvisor.com', 'tripadvisor.co.uk', 'tripadvisor.com.ph',
            'booking.com', 'expedia.com', 'hotels.com'
        }
        
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common navigation/footer text
        noise_patterns = [
            r'cookie policy',
            r'privacy policy', 
            r'terms of service',
            r'skip to main content',
            r'sign in|log in|register',
            r'follow us on',
            r'share this',
            r'related articles',
            r'advertisement'
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _extract_relevant_paragraphs(self, soup: BeautifulSoup, search_context: str) -> List[str]:
        """Extract paragraphs most relevant to the search context."""
        # Find all text content
        paragraphs = []
        
        # Look for content in common containers
        content_selectors = [
            'article p',
            '.content p', 
            '.post-content p',
            'main p',
            '.entry-content p',
            'p'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                break
        else:
            elements = soup.find_all('p')
        
        # Extract text from paragraphs
        for p in elements:
            text = self._clean_text(p.get_text())
            if len(text) > 50:  # Only meaningful paragraphs
                paragraphs.append(text)
        
        # Score paragraphs by relevance to search context
        scored_paragraphs = []
        search_keywords = search_context.lower().split()
        
        for para in paragraphs:
            para_lower = para.lower()
            score = 0
            
            # Score based on keyword matches
            for keyword in search_keywords:
                if keyword in para_lower:
                    score += para_lower.count(keyword)
            
            # Bonus for neighborhood-specific content
            if any(word in para_lower for word in ['neighborhood', 'district', 'area', 'locals', 'residents']):
                score += 2
                
            # Bonus for experience/opinion words  
            if any(word in para_lower for word in ['experience', 'opinion', 'feel', 'atmosphere', 'vibe']):
                score += 1
                
            if score > 0:
                scored_paragraphs.append((score, para))
        
        # Return top scoring paragraphs
        scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
        return [para for score, para in scored_paragraphs[:3]]
    
    def extract_content(self, url: str, search_context: str = "") -> Optional[str]:
        """Extract meaningful content from a web page."""
        try:
            logger.info(f"Extracting content from: {url}")
            
            # Skip URLs we can't process
            if not url or url == "No URL":
                return None
            
            # Skip known blocked domains
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.lower()
            if any(blocked in domain for blocked in self.blocked_domains):
                logger.info(f"Skipping blocked domain: {domain}")
                return None
                
            # Add delay to be respectful
            time.sleep(1)
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract relevant paragraphs
            relevant_paragraphs = self._extract_relevant_paragraphs(soup, search_context)
            
            if relevant_paragraphs:
                # Combine top paragraphs with separators
                combined_content = " | ".join(relevant_paragraphs[:2])
                
                # Limit length to reasonable snippet size
                if len(combined_content) > 400:
                    combined_content = combined_content[:400] + "..."
                
                return combined_content
            
            # Fallback: try to get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                return self._clean_text(meta_desc['content'])
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract content from {url}: {e}")
            return None
    
    def enhance_search_results(self, results: Dict, search_context: str = "") -> Dict:
        """Enhance search results by replacing snippets with extracted content."""
        if not results.get('sources'):
            return results
        
        enhanced_sources = []
        
        for source in results['sources']:
            enhanced_source = source.copy()
            
            # Extract better content
            extracted_content = self.extract_content(source.get('url', ''), search_context)
            
            if extracted_content:
                enhanced_source['snippet'] = extracted_content
                enhanced_source['content_enhanced'] = True
            else:
                enhanced_source['content_enhanced'] = False
            
            enhanced_sources.append(enhanced_source)
        
        # Update results
        enhanced_results = results.copy()
        enhanced_results['sources'] = enhanced_sources
        enhanced_results['content_extraction'] = {
            'enhanced_count': sum(1 for s in enhanced_sources if s.get('content_enhanced')),
            'total_sources': len(enhanced_sources)
        }
        
        return enhanced_results


def test_content_extractor():
    """Test the content extractor."""
    extractor = ContentExtractor()
    
    test_urls = [
        ("https://xixerone.com/en/chueca-madrid-gay-area/", "Chueca Madrid neighborhood"),
        ("https://www.alwayspacktissues.com/post/chueca-madrid", "Chueca Madrid reviews")
    ]
    
    for url, context in test_urls:
        print(f"\nTesting: {url}")
        print(f"Context: {context}")
        
        content = extractor.extract_content(url, context)
        if content:
            print(f"Extracted: {content[:200]}...")
        else:
            print("No content extracted")


if __name__ == "__main__":
    test_content_extractor() 