"""
SearxNG Search Engine with Multiple Instance Support and Fallback
Uses multiple public SearxNG instances for unlimited searches with automatic fallback
"""

import requests
import json
import time
import random
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlencode, quote_plus
import logging
from datetime import datetime

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

logger = logging.getLogger(__name__)

class SearxNGEngine:
    """
    SearxNG search engine with multiple instance support and automatic fallback
    """
    
    def __init__(self):
        # List of reliable public SearxNG instances (tested and working)
        self.instances = [
            # Primary instances (fastest/most reliable)
            "https://searx.projectlounge.pw",
            "https://darmarit.org/searx", 
            "https://searx.be",
            "https://search.sapti.me",
            "https://searx.work",
            
            # Secondary instances (backup)
            "https://searx.tiekoetter.com",
            "https://searx.prvcy.eu",
            "https://search.bus-hit.me",
            "https://searx.fi",
            "https://searx.fmac.xyz",
            
            # Tertiary instances (additional fallbacks)
            "https://searx.lunar.icu",
            "https://searx.gnu.style",
            "https://search.mdosch.de",
            "https://searx.sev.monster",
            "https://searx.thegpm.org"
        ]
        
        # Track instance performance and failures
        self.instance_stats = {instance: {'failures': 0, 'last_success': None, 'avg_response_time': 0} 
                              for instance in self.instances}
        
        # Current primary instance (will be tested and updated)
        self.primary_instance = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Initialize enhancement components
        self.content_extractor = ContentExtractor()
        self.confidence_scorer = ConfidenceScorer()
        self.structured_extractor = StructuredExtractor()
        
        # Test and select best primary instance on initialization
        self._initialize_primary_instance()
    
    def _initialize_primary_instance(self):
        """Test instances and select the best performing one as primary"""
        logger.info("Testing SearxNG instances to find the best primary...")
        
        best_instance = None
        best_response_time = float('inf')
        
        # Test first 5 instances to find the fastest
        test_instances = self.instances[:5]
        random.shuffle(test_instances)  # Randomize to distribute load
        
        for instance in test_instances:
            try:
                start_time = time.time()
                response = self.session.get(f"{instance}/stats", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.instance_stats[instance]['avg_response_time'] = response_time
                    self.instance_stats[instance]['last_success'] = time.time()
                    
                    if response_time < best_response_time:
                        best_response_time = response_time
                        best_instance = instance
                        
                    logger.info(f"✅ {instance} - Response time: {response_time:.2f}s")
                else:
                    logger.warning(f"❌ {instance} - Status: {response.status_code}")
                    self.instance_stats[instance]['failures'] += 1
                    
            except Exception as e:
                logger.warning(f"❌ {instance} - Error: {str(e)}")
                self.instance_stats[instance]['failures'] += 1
                continue
        
        if best_instance:
            self.primary_instance = best_instance
            logger.info(f"🎯 Primary instance selected: {best_instance} ({best_response_time:.2f}s)")
        else:
            # Fallback to first instance if none tested successfully
            self.primary_instance = self.instances[0]
            logger.warning(f"⚠️ No instances responded, using fallback: {self.primary_instance}")
    
    def _mark_instance_failure(self, instance: str):
        """Mark an instance as failed and update stats"""
        self.instance_stats[instance]['failures'] += 1
        logger.warning(f"Instance failure recorded for {instance} (total: {self.instance_stats[instance]['failures']})")
    
    def _mark_instance_success(self, instance: str, response_time: float):
        """Mark an instance as successful and update stats"""
        self.instance_stats[instance]['failures'] = max(0, self.instance_stats[instance]['failures'] - 1)
        self.instance_stats[instance]['last_success'] = time.time()
        self.instance_stats[instance]['avg_response_time'] = response_time
    
    def _enhance_location_query(self, query: str, neighborhood: str) -> str:
        """
        Enhance search query to be more location-specific and reduce irrelevant results
        """
        if not neighborhood:
            return query
            
        # Extract city/country from neighborhood if present
        parts = neighborhood.split(',')
        if len(parts) >= 2:
            area = parts[0].strip()
            city = parts[1].strip()
            
            # Add location specificity to the query
            enhanced_query = f'"{area}" "{city}" {query}'
            
            # Add additional location context based on common cities
            if 'madrid' in city.lower():
                enhanced_query += ' Spain neighborhood district barrio'
            elif 'london' in city.lower():
                enhanced_query += ' UK England neighborhood area borough'
            elif 'barcelona' in city.lower():
                enhanced_query += ' Spain Catalonia neighborhood district barrio'
            else:
                enhanced_query += ' neighborhood area district'
                
            logger.info(f"Enhanced query: {enhanced_query}")
            return enhanced_query
        else:
            # Single location name - add quotes for exact match
            return f'"{neighborhood}" {query} neighborhood area'
    
    def _filter_relevant_results(self, sources: List[Dict], neighborhood: str, category: str) -> List[Dict]:
        """
        Filter out irrelevant results that don't match the target neighborhood
        """
        if not neighborhood:
            return sources
            
        filtered = []
        neighborhood_lower = neighborhood.lower()
        
        # Extract key location terms
        location_terms = set()
        if ',' in neighborhood:
            parts = [p.strip().lower() for p in neighborhood.split(',')]
            location_terms.update(parts)
        else:
            location_terms.add(neighborhood_lower)
            
        for source in sources:
            title_lower = source.get('title', '').lower()
            snippet_lower = source.get('snippet', '').lower()
            url_lower = source.get('url', '').lower()
            
            # Calculate relevance score
            relevance_score = 0
            
            # Check for location terms in title (highest weight)
            for term in location_terms:
                if term in title_lower:
                    relevance_score += 3
                if term in snippet_lower:
                    relevance_score += 2
                if term in url_lower:
                    relevance_score += 1
            
            # Penalty for clearly irrelevant content
            irrelevant_terms = [
                'restaurant', 'taco', 'menu', 'food', 'cuisine', 'recipe',
                'nasa', 'space', 'solar', 'heliospheric', 'observatory',
                'bus tracking', 'gps technology', 'transportation app'
            ]
            
            for term in irrelevant_terms:
                if term in title_lower or term in snippet_lower:
                    relevance_score -= 5
                    
            # Only include results with positive relevance
            if relevance_score > 0:
                source['relevance_score'] = relevance_score
                filtered.append(source)
            else:
                logger.info(f"Filtered out irrelevant result: {source.get('title', 'No title')}")
        
        # Sort by relevance score (descending)
        filtered.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        logger.info(f"Filtered {len(sources)} -> {len(filtered)} relevant results")
        return filtered
    
    def _get_available_instances(self) -> List[str]:
        """Get list of instances sorted by reliability (primary first, then by failure count)"""
        available = []
        
        # Always try primary first if it exists
        if self.primary_instance:
            available.append(self.primary_instance)
        
        # Sort other instances by failure count (ascending) and last success (descending)
        other_instances = [i for i in self.instances if i != self.primary_instance]
        other_instances.sort(key=lambda x: (
            self.instance_stats[x]['failures'],
            -(self.instance_stats[x]['last_success'] or 0)
        ))
        
        available.extend(other_instances)
        return available
    
    def search(self, query: str, enhance_content: bool = True, add_confidence: bool = True, 
               category: str = 'general_info', neighborhood: str = '', max_results: int = 10) -> Dict:
        """
        Search using SearxNG with automatic fallback between instances
        
        Args:
            query: Search query string
            enhance_content: Whether to enhance content with web scraping
            add_confidence: Whether to add confidence scores to results
            category: Search category for structured extraction
            neighborhood: Neighborhood name for context
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with search results, content enhancement, confidence data, and structured extraction
        """
        available_instances = self._get_available_instances()
        last_error = None
        start_time = time.time()
        
        for i, instance in enumerate(available_instances):
            try:
                logger.info(f"🔍 Searching with instance {i+1}/{len(available_instances)}: {instance}")
                
                # Enhance query for better location specificity
                enhanced_query = self._enhance_location_query(query, neighborhood)
                
                # Prepare search parameters
                params = {
                    'q': enhanced_query,
                    'format': 'json',
                    'categories': 'general',
                    'engines': 'google,bing,duckduckgo,brave,startpage',  # Use reliable engines
                    'time_range': '',
                    'language': 'en',
                    'pageno': 1
                }
                
                # Make search request
                instance_start_time = time.time()
                url = f"{instance}/search"
                response = self.session.get(url, params=params, timeout=15)
                response_time = time.time() - instance_start_time
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        raw_sources = self._parse_searxng_results(data, max_results * 2)  # Get more to filter
                        
                        # Filter for relevance
                        sources = self._filter_relevant_results(raw_sources, neighborhood, category)
                        sources = sources[:max_results]  # Limit to requested number
                        
                        if sources:
                            self._mark_instance_success(instance, response_time)
                            logger.info(f"✅ Success with {instance}: {len(sources)} results in {response_time:.2f}s")
                            
                            # Create results structure matching DuckDuckGo format
                            results = {
                                "sources": sources,
                                "search_term": query,
                                "search_engine": "searxng",
                                "instance_used": instance,
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
                            
                            logger.info(f"SearxNG search successful in {results['response_time']}")
                            return results
                        else:
                            logger.warning(f"⚠️ {instance} returned no results")
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ {instance} - JSON decode error: {str(e)}")
                        self._mark_instance_failure(instance)
                        last_error = f"JSON decode error: {str(e)}"
                        
                elif response.status_code == 429:
                    logger.warning(f"⏳ {instance} - Rate limited (429)")
                    self._mark_instance_failure(instance)
                    last_error = "Rate limited"
                    # Add delay before trying next instance
                    time.sleep(2)
                    
                else:
                    logger.warning(f"❌ {instance} - HTTP {response.status_code}")
                    self._mark_instance_failure(instance)
                    last_error = f"HTTP {response.status_code}"
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ {instance} - Request timeout")
                self._mark_instance_failure(instance)
                last_error = "Request timeout"
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"❌ {instance} - Request error: {str(e)}")
                self._mark_instance_failure(instance)
                last_error = f"Request error: {str(e)}"
                
            # Small delay between instance attempts
            if i < len(available_instances) - 1:
                time.sleep(1)
        
        # All instances failed - return error format matching DuckDuckGo
        logger.error(f"🚨 All {len(available_instances)} SearxNG instances failed. Last error: {last_error}")
        return {
            "sources": [],
            "search_term": query,
            "search_engine": "searxng",
            "error": last_error or "All instances failed",
            "response_time": f"{time.time() - start_time:.2f}s",
            "total_results": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _parse_searxng_results(self, data: Dict, max_results: int) -> List[Dict[str, Any]]:
        """Parse SearxNG JSON response into standardized format"""
        results = []
        
        if 'results' not in data:
            return results
        
        for item in data['results'][:max_results]:
            try:
                result = {
                    'title': item.get('title', '').strip(),
                    'url': item.get('url', '').strip(),
                    'snippet': item.get('content', '').strip(),  # Use 'snippet' to match DuckDuckGo format
                    'engine': item.get('engine', 'searxng'),
                    'score': item.get('score', 1.0)
                }
                
                # Only add results with valid title and URL
                if result['title'] and result['url']:
                    results.append(result)
                    
            except Exception as e:
                logger.warning(f"Error parsing result: {str(e)}")
                continue
        
        return results
    
    def get_instance_stats(self) -> Dict[str, Any]:
        """Get current instance statistics for debugging"""
        return {
            'primary_instance': self.primary_instance,
            'total_instances': len(self.instances),
            'instance_stats': self.instance_stats,
            'available_instances': len([i for i in self.instances 
                                      if self.instance_stats[i]['failures'] < 5])
        }


# Test function
def test_searxng_engine():
    """Test the SearxNG engine"""
    engine = SearxNGEngine()
    
    print("🧪 Testing SearxNG Engine...")
    print(f"Primary instance: {engine.primary_instance}")
    
    # Test search
    results = engine.search("Python programming", max_results=5)
    
    if results and results.get('sources'):
        print(f"\n✅ Found {results['total_results']} results:")
        for i, result in enumerate(results['sources'], 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Snippet: {result['snippet'][:100]}...")
            print()
    else:
        print("❌ No results found")
        if results and 'error' in results:
            print(f"Error: {results['error']}")
    
    # Show stats
    stats = engine.get_instance_stats()
    print(f"\n📊 Instance Stats:")
    print(f"Available instances: {stats['available_instances']}/{stats['total_instances']}")


if __name__ == "__main__":
    test_searxng_engine() 