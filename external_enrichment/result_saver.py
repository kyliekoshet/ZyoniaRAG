"""
Result saver module for automatically saving search results to JSON files.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))


class ResultSaver:
    """Handles saving search results to JSON files in enrichment_results directory."""
    
    def __init__(self, results_dir: str = "enrichment_results"):
        self.results_dir = results_dir
        self._ensure_results_dir()
    
    def _ensure_results_dir(self):
        """Ensure results directory exists."""
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir, exist_ok=True)
    
    def _generate_filename(self, neighborhood: str, search_type: str = "rag_optimized") -> str:
        """
        Generate filename following the existing pattern.
        
        Args:
            neighborhood: Neighborhood name (e.g., "Chamartin, Madrid")
            search_type: Type of search (default: "rag_optimized")
            
        Returns:
            Filename like: chamartin_madrid_rag_optimized_20250626_180443.json
        """
        # Normalize neighborhood name
        normalized = neighborhood.lower()
        normalized = normalized.replace(" ", "_")
        normalized = normalized.replace(",", "")
        normalized = normalized.replace("-", "_")
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename
        filename = f"{normalized}_{search_type}_{timestamp}.json"
        
        return filename
    
    def save_search_result(self, search_result: Dict[str, Any], 
                          neighborhood: str = None, 
                          search_type: str = "hybrid_search") -> str:
        """
        Save search result to JSON file.
        
        Args:
            search_result: The search result dictionary
            neighborhood: Neighborhood name (extracted from result if None)
            search_type: Type of search for filename
            
        Returns:
            Path to saved file
        """
        # Extract neighborhood if not provided
        if not neighborhood:
            neighborhood = search_result.get('neighborhood', 'unknown_location')
        
        # Generate filename
        filename = self._generate_filename(neighborhood, search_type)
        filepath = os.path.join(self.results_dir, filename)
        
        # Add metadata
        enhanced_result = {
            **search_result,
            'saved_at': datetime.now().isoformat(),
            'saved_to': filepath,
            'search_type': search_type
        }
        
        # Save to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(enhanced_result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Results saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving results to {filepath}: {e}")
            return None
    
    def save_full_enrichment(self, neighborhood: str, 
                           all_results: Dict[str, Any]) -> str:
        """
        Save complete enrichment results (all categories) to file.
        
        Args:
            neighborhood: Neighborhood name
            all_results: Dictionary with all category results
            
        Returns:
            Path to saved file
        """
        # Format full enrichment result
        full_result = {
            'neighborhood': neighborhood,
            'enrichment_type': 'full_neighborhood_analysis',
            'categories': all_results,
            'total_categories': len(all_results),
            'generated_at': datetime.now().isoformat()
        }
        
        return self.save_search_result(full_result, neighborhood, "full_enrichment")
    
    def list_saved_results(self, neighborhood: str = None) -> list:
        """
        List saved result files, optionally filtered by neighborhood.
        
        Args:
            neighborhood: Filter by neighborhood (optional)
            
        Returns:
            List of saved result files
        """
        if not os.path.exists(self.results_dir):
            return []
        
        files = []
        for filename in os.listdir(self.results_dir):
            if filename.endswith('.json'):
                if neighborhood:
                    normalized = neighborhood.lower().replace(" ", "_").replace(",", "")
                    if normalized in filename.lower():
                        files.append(os.path.join(self.results_dir, filename))
                else:
                    files.append(os.path.join(self.results_dir, filename))
        
        return sorted(files, reverse=True)  # Most recent first


def test_result_saver():
    """Test function for result saver."""
    saver = ResultSaver()
    
    # Test data
    test_result = {
        'neighborhood': 'Chamartin, Madrid',
        'query': 'Test query',
        'priority_category': 'crime_rate',
        'instant_results': {
            'crime_rate': {
                'sources': [
                    {
                        'title': 'Test Source',
                        'url': 'https://example.com',
                        'snippet': 'Test snippet'
                    }
                ],
                'total_results': 1
            }
        },
        'response_time': '2.0s'
    }
    
    # Save test result
    filepath = saver.save_search_result(test_result)
    print(f"Test result saved to: {filepath}")
    
    # List saved results
    saved_files = saver.list_saved_results('Chamartin')
    print(f"Found {len(saved_files)} saved files for Chamartin")


if __name__ == "__main__":
    test_result_saver() 