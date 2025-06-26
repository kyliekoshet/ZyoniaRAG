#!/usr/bin/env python3
"""
Simple neighborhood search script with automatic JSON file saving.
Usage: python3 search_neighborhood.py "Neighborhood Name" "Your question"
"""

import sys
import os
import json
import time
from datetime import datetime

# Add external_enrichment to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'external_enrichment'))

from category_detector import CategoryDetector
from duckduckgo_engine import DuckDuckGoEngine
from result_saver import ResultSaver
from external_enrichment.config import SEARCH_CATEGORIES


def search_neighborhood(neighborhood, query):
    """
    Search for neighborhood information and save results to JSON file.
    
    Args:
        neighborhood: Neighborhood name (e.g., "Chamartin, Madrid")
        query: User's question (e.g., "What's the crime rate?")
        
    Returns:
        Dictionary with search results and file path
    """
    print(f"🏙️ Neighborhood Search System")
    print("=" * 60)
    print(f"📍 Neighborhood: {neighborhood}")
    print(f"🔍 Query: {query}")
    print()
    
    # Initialize components
    try:
        detector = CategoryDetector()
        engine = DuckDuckGoEngine()
        saver = ResultSaver()
        
        # Analyze query to detect category and neighborhood
        analysis = detector.analyze_query(f"{query} {neighborhood}")
        
        # Use detected neighborhood if available, otherwise use provided
        final_neighborhood = analysis.get('neighborhood') or neighborhood
        analysis['neighborhood'] = final_neighborhood
        
        print(f"🎯 Priority Category: {analysis['priority_category']}")
        print(f"🔄 Background Categories: {', '.join(analysis['background_categories'])}")
        print()
        
        # Generate search terms (multiple for better coverage)
        category_config = SEARCH_CATEGORIES[analysis['priority_category']]
        primary_search_term = category_config['search_terms'][0].format(neighborhood=final_neighborhood)
        all_search_terms = [term.format(neighborhood=final_neighborhood) for term in category_config['search_terms']]
        
        print(f"🔎 Searching with multiple terms for better coverage...")
        print(f"Primary: {primary_search_term}")
        
        # Perform search with structured extraction
        start_time = time.time()
        result = engine.search(
            primary_search_term, 
            enhance_content=True, 
            add_confidence=True,
            category=analysis['priority_category'],
            neighborhood=final_neighborhood
        )
        search_time = time.time() - start_time
        
        # Create response
        response = {
            'neighborhood': final_neighborhood,
            'query': query,
            'priority_category': analysis['priority_category'],
            'instant_results': {
                analysis['priority_category']: result
            },
            'background_categories': analysis['background_categories'],
            'status': 'priority_complete_background_processing',
            'response_time': f"{search_time:.2f}s",
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Search completed in {search_time:.2f}s")
        print(f"📊 Found {result['total_results']} results")
        
        # Save to file
        print()
        print("💾 Saving results...")
        saved_file = saver.save_search_result(response, final_neighborhood, 'neighborhood_search')
        
        if saved_file:
            response['saved_to_file'] = saved_file
            
            # Show top results
            if result['sources']:
                print()
                print("📝 Top Results:")
                for i, source in enumerate(result['sources'][:3], 1):
                    print(f"\n{i}. {source['title']}")
                    print(f"   🔗 {source['url']}")
                    print(f"   📄 {source['snippet'][:80]}...")
            
            print()
            print("📋 SUMMARY:")
            print("=" * 40)
            print(f"✅ Results saved to: {saved_file}")
            print(f"📊 Total results: {result['total_results']}")
            print(f"⏱️ Response time: {search_time:.2f}s")
            print(f"🎯 Category: {analysis['priority_category']}")
            print(f"🔄 Background categories: {len(analysis['background_categories'])}")
            
            return response
        else:
            print("❌ Failed to save results")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Main function for command line usage."""
    if len(sys.argv) < 3:
        print("🏙️ Neighborhood Search System")
        print("=" * 50)
        print("Usage: python3 search_neighborhood.py 'Neighborhood' 'Question'")
        print()
        print("Examples:")
        print("  python3 search_neighborhood.py 'Chamartin, Madrid' 'What is the crime rate?'")
        print("  python3 search_neighborhood.py 'Soho, London' 'Is it clean and safe?'")
        print("  python3 search_neighborhood.py 'Malasana, Madrid' 'Good for investment?'")
        print()
        print("Available categories:")
        for category, config in SEARCH_CATEGORIES.items():
            keywords = ', '.join(config['keywords'][:3])
            print(f"  • {category}: {keywords}...")
        return 1
    
    neighborhood = sys.argv[1]
    query = sys.argv[2]
    
    result = search_neighborhood(neighborhood, query)
    
    if result:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main()) 