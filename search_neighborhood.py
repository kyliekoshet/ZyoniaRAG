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
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add external_enrichment to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'external_enrichment'))

from category_detector import CategoryDetector
from duckduckgo_engine import DuckDuckGoEngine
from result_saver import ResultSaver
from external_enrichment.config import SEARCH_CATEGORIES


def search_single_category(engine, neighborhood, category):
    """
    Search for a single category with error handling.
    
    Args:
        engine: DuckDuckGoEngine instance
        neighborhood: Neighborhood name
        category: Category to search for
        
    Returns:
        Tuple of (category, result_dict)
    """
    try:
        category_config = SEARCH_CATEGORIES[category]
        search_term = category_config['search_terms'][0].format(neighborhood=neighborhood)
        
        print(f"🔍 Searching {category}: {search_term}")
        
        result = engine.search(
            search_term,
            enhance_content=True,
            add_confidence=True,
            category=category,
            neighborhood=neighborhood
        )
        
        return (category, result)
        
    except Exception as e:
        print(f"❌ Error searching {category}: {e}")
        return (category, {
            "sources": [],
            "search_term": f"{neighborhood} {category}",
            "search_engine": "duckduckgo",
            "error": str(e),
            "total_results": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })


def search_neighborhood(neighborhood, query):
    """
    Search for neighborhood information across ALL categories and save results to JSON file.
    
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
        
        # Get all categories to search
        all_categories = [analysis['priority_category']] + analysis['background_categories']
        print(f"📊 Processing {len(all_categories)} categories: {', '.join(all_categories)}")
        print()
        
        # Search all categories sequentially to avoid rate limits
        start_time = time.time()
        all_results = {}
        
        print("🚀 Starting sequential category searches...")
        for i, category in enumerate(all_categories, 1):
            print(f"🔍 Processing category {i}/{len(all_categories)}: {category}")
            category, result = search_single_category(engine, final_neighborhood, category)
            all_results[category] = result
            print(f"✅ Completed {category}: {result['total_results']} results")
            
            # Add delay between categories to respect rate limits
            if i < len(all_categories):
                print(f"⏳ Waiting 6 seconds before next category...")
                time.sleep(6)
        
        search_time = time.time() - start_time
        
        # Create response with all category results
        response = {
            'neighborhood': final_neighborhood,
            'query': query,
            'priority_category': analysis['priority_category'],
            'all_categories_results': all_results,
            'background_categories': analysis['background_categories'],
            'status': 'all_categories_complete',
            'response_time': f"{search_time:.2f}s",
            'timestamp': datetime.now().isoformat(),
            'total_categories_processed': len(all_categories),
            'categories_with_results': len([cat for cat, res in all_results.items() if res['total_results'] > 0])
        }
        
        print(f"✅ All searches completed in {search_time:.2f}s")
        
        # Calculate total results across all categories
        total_results = sum(result['total_results'] for result in all_results.values())
        print(f"📊 Total results across all categories: {total_results}")
        
        # Save to file
        print()
        print("💾 Saving comprehensive results...")
        saved_file = saver.save_search_result(response, final_neighborhood, 'comprehensive_neighborhood_search')
        
        if saved_file:
            response['saved_to_file'] = saved_file
            
            # Show summary of results by category
            print()
            print("📝 Results Summary by Category:")
            print("=" * 50)
            for category in all_categories:
                result = all_results[category]
                status = "✅" if result['total_results'] > 0 else "❌"
                print(f"{status} {category.replace('_', ' ').title()}: {result['total_results']} results")
                
                # Show structured data summary if available
                if 'structured_summary' in result and result['structured_summary']:
                    summary = result['structured_summary']
                    metrics_count = len(summary.get('combined_metrics', {}))
                    facts_count = len(summary.get('key_facts', []))
                    quality = summary.get('data_quality', 'unknown')
                    if metrics_count > 0 or facts_count > 0:
                        print(f"   📊 Extracted: {metrics_count} metrics, {facts_count} facts, {quality} quality")
            
            print()
            print("📋 COMPREHENSIVE SUMMARY:")
            print("=" * 40)
            print(f"✅ Results saved to: {saved_file}")
            print(f"📊 Total results: {total_results}")
            print(f"⏱️ Response time: {search_time:.2f}s")
            print(f"🎯 Priority category: {analysis['priority_category']}")
            print(f"🔄 Categories processed: {len(all_categories)}/5")
            print(f"📈 Categories with data: {response['categories_with_results']}/{len(all_categories)}")
            
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