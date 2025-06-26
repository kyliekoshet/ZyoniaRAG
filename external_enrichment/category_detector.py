"""
Category detection module for parsing user queries and identifying priority search categories.
"""

import re
from typing import List, Dict, Tuple, Optional

# Import from the external_enrichment config
try:
    from .config import SEARCH_CATEGORIES
except ImportError:
    # When running from parent directory
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'external_enrichment'))
    from external_enrichment.config import SEARCH_CATEGORIES


class CategoryDetector:
    """Detects search categories from user queries and determines priority."""
    
    def __init__(self):
        self.categories = SEARCH_CATEGORIES
        
    def detect_categories(self, query: str) -> Tuple[Optional[str], List[str]]:
        """
        Analyze user query to detect requested categories.
        
        Args:
            query: User's search query
            
        Returns:
            Tuple of (priority_category, all_detected_categories)
        """
        query_lower = query.lower()
        detected = []
        scores = {}
        
        # Check each category for keyword and pattern matches
        for category, config in self.categories.items():
            score = 0
            
            # Check keyword matches
            for keyword in config["keywords"]:
                if keyword in query_lower:
                    score += 1
            
            # Check pattern matches (higher weight)
            if "patterns" in config:
                for pattern in config["patterns"]:
                    if re.search(pattern, query_lower, re.IGNORECASE):
                        score += 3  # Patterns get higher weight
                        
            if score > 0:
                scores[category] = score
                detected.append(category)
        
        # If no specific categories detected, default to general_info
        if not detected:
            detected = ["general_info"]
            scores["general_info"] = 1
            
        # Priority is the category with highest score
        priority_category = max(scores, key=scores.get) if scores else "general_info"
        
        return priority_category, detected
    
    def get_remaining_categories(self, detected_categories: List[str]) -> List[str]:
        """
        Get categories not yet searched for background processing.
        
        Args:
            detected_categories: Categories already detected/searched
            
        Returns:
            List of remaining categories for background search
        """
        all_categories = list(self.categories.keys())
        return [cat for cat in all_categories if cat not in detected_categories]
    
    def extract_neighborhood(self, query: str) -> Optional[str]:
        """
        Extract neighborhood name from query.
        
        Args:
            query: User's search query
            
        Returns:
            Neighborhood name if found, None otherwise
        """
        # Major Spanish cities and international cities for enhanced pattern matching
        spanish_cities = ['madrid', 'barcelona', 'valencia', 'sevilla', 'seville', 'bilbao', 'zaragoza', 
                         'granada', 'córdoba', 'cordoba', 'salamanca', 'toledo', 'santiago', 'vigo', 
                         'palma', 'san sebastian', 'donostia', 'oviedo', 'santander', 'pamplona']
        
        international_cities = ['london', 'paris', 'berlin', 'rome', 'amsterdam', 'vienna', 'prague', 
                              'lisbon', 'porto', 'athens', 'dublin', 'stockholm', 'oslo', 'copenhagen',
                              'brussels', 'zurich', 'geneva', 'milan', 'florence', 'venice', 'budapest',
                              'warsaw', 'beirut', 'istanbul', 'barcelona', 'valencia', 'lyon', 'marseille']
        
        all_cities = spanish_cities + international_cities
        
        # Enhanced patterns for neighborhood mentions (in order of specificity)
        patterns = [
            # Spanish city patterns - most specific first
            r'in\s+([A-Za-z\sñáéíóúü,\-\']+?)\s+(Madrid|Barcelona|Valencia|Sevilla|Seville|Bilbao|Granada|Zaragoza)',
            r'([A-Za-z\sñáéíóúü,\-\']+?)\s+(Madrid|Barcelona|Valencia|Sevilla|Seville|Bilbao|Granada|Zaragoza)\s+(?:crime|safety|clean|investment|area|neighborhood|barrio|distrito)',
            r'([A-Za-z\sñáéíóúü,\-\']+?)\s+(Madrid|Barcelona|Valencia|Sevilla|Seville|Bilbao|Granada|Zaragoza)(?:\s|$|[.!?])',
            
            # International city patterns
            r'in\s+([A-Za-z\s,\-\']+?)\s+(London|Paris|Berlin|Rome|Amsterdam|Vienna|Prague|Lisbon|Athens|Dublin)',
            r'([A-Za-z\s,\-\']+?)\s+(London|Paris|Berlin|Rome|Amsterdam|Vienna|Prague|Lisbon|Athens|Dublin)\s+(?:crime|safety|clean|investment|area|neighborhood|district)',
            r'([A-Za-z\s,\-\']+?)\s+(London|Paris|Berlin|Rome|Amsterdam|Vienna|Prague|Lisbon|Athens|Dublin)(?:\s|$|[.!?])',
            
            # Generic patterns for any location
            r'in\s+([A-Za-z\sñáéíóúü,\-\']+?)(?:\s+(?:spain|españa|lebanon|france|uk|italy|germany|portugal))?(?:\s|$|[.!?])',
            r'about\s+([A-Za-z\sñáéíóúü,\-\']+?)(?:\s+(?:spain|españa|lebanon|france|uk|italy|germany|portugal))?(?:\s|$|[.!?])',
            r'(?:^|\s)([A-Za-z\sñáéíóúü,\-\']{4,})(?:\s+(?:crime|safety|clean|investment|area|neighborhood|barrio|distrito))',
            
            # Legacy Madrid-specific patterns (keep for backward compatibility)
            r'in\s+([A-Za-z\sñáéíóú,]+?)\s+Madrid',
            r'([A-Za-z\sñáéíóú,]+?)\s+Madrid\s+(?:crime|safety|clean|investment|area|neighborhood)',
            r'([A-Za-z\sñáéíóú,]+?)\s+Madrid(?:\s|$|[.!?])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:  # Pattern with city
                    neighborhood = match.group(1).strip()
                    city = match.group(2).strip()
                else:  # Pattern without explicit city
                    neighborhood = match.group(1).strip()
                    city = None
                
                # Clean up common words (but keep important descriptors)
                cleanup_words = ['the', 'a', 'an', 'area', 'neighborhood', 'district', 'barrio', 'distrito',
                               'what', 'how', 'is', 'rate', 'investment', 'potential', 'crime', 
                               'safety', 'like', 'do', 'people', 'think', 'about', 'tell', 'me', 'this']
                
                words = neighborhood.split()
                cleaned_words = [w for w in words if w.lower() not in cleanup_words and len(w) > 1]
                
                if cleaned_words:
                    result = ' '.join(cleaned_words)
                    
                    # Add city if we captured it in the pattern
                    if city:
                        result = f"{result}, {city}"
                    # Auto-detect city context for known Spanish neighborhoods
                    elif not city and 'madrid' not in result.lower():
                        madrid_neighborhoods = ['salamanca', 'latina', 'moncloa', 'almagro', 'chamartin', 
                                              'malasaña', 'malasana', 'chueca', 'chamberi', 'retiro', 
                                              'lavapies', 'sol', 'centro', 'arguelles', 'tetuan']
                        barcelona_neighborhoods = ['eixample', 'gracia', 'born', 'raval', 'barceloneta', 
                                                 'sarria', 'pedralbes', 'sant gervasi', 'poble sec']
                        valencia_neighborhoods = ['ciutat vella', 'eixample', 'extramurs', 'campanar', 
                                                'poblats maritims', 'algiros']
                        
                        neighborhood_lower = result.lower()
                        if any(name in neighborhood_lower for name in madrid_neighborhoods):
                            result = f"{result}, Madrid"
                        elif any(name in neighborhood_lower for name in barcelona_neighborhoods):
                            result = f"{result}, Barcelona"
                        elif any(name in neighborhood_lower for name in valencia_neighborhoods):
                            result = f"{result}, Valencia"
                    
                    return result
        
        return None
    
    def analyze_query(self, query: str) -> Dict:
        """
        Complete analysis of user query.
        
        Args:
            query: User's search query
            
        Returns:
            Dictionary with analysis results
        """
        neighborhood = self.extract_neighborhood(query)
        priority_category, detected_categories = self.detect_categories(query)
        remaining_categories = self.get_remaining_categories(detected_categories)
        
        return {
            "neighborhood": neighborhood,
            "priority_category": priority_category,
            "detected_categories": detected_categories,
            "background_categories": remaining_categories,
            "query": query
        }


def test_category_detector():
    """Test function for category detection."""
    detector = CategoryDetector()
    
    test_queries = [
        "What's the crime rate in Soho, London?",
        "Is Malasana Madrid a clean neighborhood?",
        "Tell me about investment potential in Chamberi",
        "What do people think about living in La Latina?",
        "Information about Salamanca district Madrid"
    ]
    
    for query in test_queries:
        result = detector.analyze_query(query)
        print(f"\nQuery: {query}")
        print(f"Neighborhood: {result['neighborhood']}")
        print(f"Priority: {result['priority_category']}")
        print(f"Detected: {result['detected_categories']}")
        print(f"Background: {result['background_categories']}")


if __name__ == "__main__":
    test_category_detector() 