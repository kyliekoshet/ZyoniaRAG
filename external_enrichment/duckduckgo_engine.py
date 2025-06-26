#!/usr/bin/env python3
"""
DuckDuckGo search engine with enhanced content extraction and confidence scoring.
"""

import time
import logging
from typing import Dict, List, Optional
from datetime import datetime

# Import LangChain components
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

try:
    from .content_extractor import ContentExtractor
    from .confidence_scorer import ConfidenceScorer
    from .structured_extractor import StructuredExtractor
    from .config import SEARCH_SETTINGS
except ImportError:
    from content_extractor import ContentExtractor
    from confidence_scorer import ConfidenceScorer
    from structured_extractor import StructuredExtractor
    from config import SEARCH_SETTINGS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DuckDuckGoEngine:
    """Enhanced DuckDuckGo search with content extraction and confidence scoring."""
    
    def __init__(self):
        """Initialize the DuckDuckGo search engine with enhanced features."""
        self.search_wrapper = DuckDuckGoSearchAPIWrapper(
            region="es-es",
            time="y",  # Last year
            max_results=SEARCH_SETTINGS.get("max_results_per_category", 5),
            safesearch="moderate"
        )
        self.content_extractor = ContentExtractor()
        self.confidence_scorer = ConfidenceScorer()
        self.structured_extractor = StructuredExtractor()
        self.last_search_time = 0
        
    def _apply_rate_limiting(self):
        """Apply rate limiting between searches."""
        current_time = time.time()
        time_since_last = current_time - self.last_search_time
        min_delay = SEARCH_SETTINGS.get("delay_between_searches", 3.0)
        
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            logger.info(f"Applying rate limiting: sleeping for {sleep_time:.1f}s")
            time.sleep(sleep_time)
        
        self.last_search_time = time.time()
    
    def search(self, query: str, enhance_content: bool = True, add_confidence: bool = True, 
               category: str = 'general_info', neighborhood: str = '') -> Dict:
        """
        Perform DuckDuckGo search with optional content enhancement and confidence scoring.
        
        Args:
            query: Search query string
            enhance_content: Whether to enhance content with web scraping
            add_confidence: Whether to add confidence scores to results
            category: Search category for structured extraction
            neighborhood: Neighborhood name for context
            
        Returns:
            Dictionary with search results, content enhancement, confidence data, and structured extraction
        """
        try:
            self._apply_rate_limiting()
            
            logger.info(f"Performing DuckDuckGo search: {query}")
            start_time = time.time()
            
            # Perform the search
            raw_results = self.search_wrapper.run(query)
            
            # Parse results
            if isinstance(raw_results, str):
                # Handle case where results come as string
                sources = [{"title": "Search Result", "url": "No URL", "snippet": raw_results}]
            elif isinstance(raw_results, list):
                sources = raw_results[:SEARCH_SETTINGS.get("max_results_per_category", 5)]
            else:
                sources = []
            
            # Create initial results structure
            results = {
                "sources": sources,
                "search_term": query,
                "search_engine": "duckduckgo",
                "instance_used": "duckduckgo.com",
                "response_time": f"{time.time() - start_time:.2f}s",
                "total_results": len(sources),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Enhance content if requested
            if enhance_content and sources:
                logger.info("Enhancing search results with scraped content...")
                results = self.content_extractor.enhance_search_results(results, query)
            
            # Add confidence scores if requested
            if add_confidence and sources:
                logger.info("Adding confidence scores to search results...")
                results = self.confidence_scorer.score_search_results(results, query)
            
            # Add structured extraction if we have category and neighborhood info
            if sources and category and neighborhood:
                logger.info("Applying structured data extraction...")
                for source in results['sources']:
                    if 'snippet' in source and source['snippet']:
                        structured_data = self.structured_extractor.extract_structured_data(
                            source['snippet'], category, neighborhood
                        )
                        source['structured_data'] = structured_data
                
                # Add summary of extracted data to results
                all_metrics = {}
                all_facts = []
                quality_scores = []
                
                for source in results['sources']:
                    if 'structured_data' in source and source['structured_data']:
                        sd = source['structured_data']
                        if 'extracted_metrics' in sd:
                            all_metrics.update(sd['extracted_metrics'])
                        if 'key_facts' in sd:
                            all_facts.extend(sd['key_facts'])
                        if 'data_quality' in sd and sd['data_quality'] != 'error':
                            quality_map = {'high': 3, 'medium': 2, 'low': 1}
                            quality_scores.append(quality_map.get(sd['data_quality'], 1))
                
                # Add structured summary to results
                results['structured_summary'] = {
                    'combined_metrics': all_metrics,
                    'key_facts': list(set(all_facts))[:10],  # Remove duplicates, limit to 10
                    'data_quality': 'high' if quality_scores and sum(quality_scores) / len(quality_scores) >= 2.5 else 
                                   'medium' if quality_scores and sum(quality_scores) / len(quality_scores) >= 1.5 else 'low',
                    'extraction_success': len([s for s in results['sources'] if 'structured_data' in s])
                }
            
            logger.info(f"DuckDuckGo search successful in {results['response_time']}")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return {
                "sources": [],
                "search_term": query,
                "search_engine": "duckduckgo",
                "error": str(e),
                "response_time": f"{time.time() - start_time:.2f}s",
                "total_results": 0,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }


def test_duckduckgo_engine():
    """Test function for DuckDuckGo engine."""
    engine = DuckDuckGoEngine()
    
    test_queries = [
        "Soho London crime rate statistics",
        "Malasana Madrid cleanliness rating"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: {query}")
        result = engine.search(query)
        print(f"Results: {result['total_results']}")
        print(f"Engine: {result['search_engine']}")
        print(f"Time: {result['response_time']}")
        
        if result['sources']:
            print("First result:")
            first = result['sources'][0]
            print(f"  Title: {first['title']}")
            print(f"  URL: {first['url']}")
            print(f"  Snippet: {first['snippet'][:100]}...")


if __name__ == "__main__":
    test_duckduckgo_engine() 