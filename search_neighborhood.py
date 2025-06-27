#!/usr/bin/env python3
"""
Enhanced Neighborhood Search System
Searches for neighborhood information using SearxNG with multiple fallback instances
"""

import sys
import time
import json
from datetime import datetime

# Import our enhanced components
from external_enrichment.category_detector import CategoryDetector
from external_enrichment.searxng_engine import SearxNGEngine
from external_enrichment.result_saver import ResultSaver

def search_single_category(engine, neighborhood, category, fast_mode=False):
    """
    Search for a single category with error handling.
    
    Args:
        engine: SearxNGEngine instance
        neighborhood: Neighborhood name
        category: Category to search for
        fast_mode: If True, disables expensive operations for faster response
        
    Returns:
        Tuple of (category, result_dict)
    """
    try:
        # Import category-specific search terms
        from external_enrichment.config import SEARCH_SETTINGS
        
        # Get category-specific search terms
        search_terms = SEARCH_SETTINGS.get(category, {}).get('search_terms', [])
        if search_terms:
            query = f"{neighborhood} {search_terms[0]}"
        else:
            query = f"{neighborhood} {category}"
        
        print(f"🔎 Using enhanced search term: {query}")
        
        # Search with fast mode settings
        if fast_mode:
            result = engine.search(
                query=query,
                enhance_content=False,  # Skip web scraping (saves 10-15s)
                add_confidence=False,   # Skip confidence scoring (saves 2-3s)
                category=category,
                neighborhood=neighborhood,
                max_results=5  # Fewer results for speed
            )
        else:
            result = engine.search(
                query=query,
                enhance_content=True,
                add_confidence=True,
                category=category,
                neighborhood=neighborhood,
                max_results=10
            )
            
        return category, result
        
    except Exception as e:
        print(f"❌ Error searching {category}: {str(e)}")
        return category, {
            "sources": [],
            "search_term": query if 'query' in locals() else f"{neighborhood} {category}",
            "search_engine": "searxng",
            "error": str(e),
            "total_results": 0
        }

def main():
    if len(sys.argv) < 3:
        print("Usage: python search_neighborhood.py \"<neighborhood>\" \"<query>\" [--fast]")
        print("Example: python search_neighborhood.py \"Salamanca, Madrid\" \"Is it good for investment?\" --fast")
        sys.exit(1)
    
    neighborhood = sys.argv[1]
    query = sys.argv[2]
    fast_mode = "--fast" in sys.argv
    
    print("🏙️ Neighborhood Search System")
    print("=" * 60)
    print(f"📍 Neighborhood: {neighborhood}")
    print(f"🔍 Query: {query}")
    
    if fast_mode:
        print("⚡ Fast Mode: ENABLED (reduced accuracy for speed)")
    else:
        print("🔧 Standard Mode: Full enhancement (slower but more accurate)")
    
    start_time = time.time()
    
    try:
        # Initialize components
        detector = CategoryDetector()
        engine = SearxNGEngine()
        saver = ResultSaver()
        
        # Detect category
        category_result = detector.analyze_query(query)
        priority_category = category_result['priority_category']
        
        print(f"🎯 Priority Category: {priority_category}")
        
        # Process only the priority category for efficiency
        print(f"\n📊 Processing priority category only: {priority_category}")
        print("🚀 Processing priority category...")
        
        category, result = search_single_category(engine, neighborhood, priority_category, fast_mode)
        
        # Create final results structure
        final_results = {
            "neighborhood": neighborhood,
            "query": query,
            "priority_category": priority_category,
            "fast_mode": fast_mode,
            "instant_results": {
                priority_category: result
            },
            "search_metadata": {
                "total_time": f"{time.time() - start_time:.2f}s",
                "timestamp": datetime.now().isoformat(),
                "search_engine": "searxng",
                "mode": "fast" if fast_mode else "standard"
            }
        }
        
        # Calculate and display timing
        elapsed_time = time.time() - start_time
        print(f"✅ Search completed in {elapsed_time:.2f}s")
        
        # Display results summary
        sources = result.get('sources', [])
        print(f"📊 Found {len(sources)} results")
        
        # Save results
        print("\n💾 Saving results...")
        filename = saver.save_search_result(final_results, neighborhood, 'neighborhood_search')
        print(f"✅ Results saved to: {filename}")
        
        # Display top results
        if sources:
            print(f"\n📝 Top Results:")
            print()
            for i, source in enumerate(sources[:3], 1):
                title = source.get('title', 'No title')[:80]
                url = source.get('url', 'No URL')
                snippet = source.get('snippet', 'No description')[:80]
                
                print(f"{i}. {title}")
                print(f"   🔗 {url}")
                print(f"   📄 {snippet}...")
                print()
        
        # Display structured data summary (if available and not in fast mode)
        if not fast_mode and 'structured_summary' in result:
            summary = result['structured_summary']
            metrics_count = len(summary.get('combined_metrics', {}))
            facts_count = len(summary.get('key_facts', []))
            data_quality = summary.get('data_quality', 'unknown')
            
            print(f"📊 Structured Data Extracted:")
            print(f"   • {metrics_count} metrics, {facts_count} facts")
            print(f"   • Data quality: {data_quality}")
        elif fast_mode:
            print(f"📊 Structured Data: Skipped in fast mode")
        
        # Final summary
        print(f"\n📋 SUMMARY:")
        print("=" * 40)
        print(f"✅ Results saved to: {filename}")
        print(f"📊 Total results: {len(sources)}")
        print(f"⏱️ Response time: {elapsed_time:.2f}s")
        print(f"🎯 Category: {priority_category}")
        if fast_mode:
            print(f"⚡ Mode: Fast (accuracy reduced for speed)")
        else:
            print(f"🔧 Mode: Standard (full enhancement)")
            
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 