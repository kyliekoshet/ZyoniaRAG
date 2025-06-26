import time
import argparse
import json
from typing import Dict
from langchain_community.tools.searx_search.tool import SearxSearchRun
from langchain_community.utilities.searx_search import SearxSearchWrapper

def fetch_searx_enrichment_data(zone_name: str) -> Dict[str, str]:
    """
    Fetches raw enrichment information for a given property zone using SearxNG.

    This function performs targeted searches for different enrichment signals
    (crime rate, cleanliness, public perception, investment potential) and
    returns the raw search result snippets for each category.

    This raw data can then be passed to a downstream LLM to be summarized.

    Args:
        zone_name: The name of the area to search for (e.g., "Salamanca district, Madrid").

    Returns:
        A dictionary where keys are enrichment categories and values are the
        raw string of search result snippets.
    """
    # Point to a public SearxNG instance and disable SSL verification  
    searx_host = "https://searx.projectlounge.pw"
    wrapper = SearxSearchWrapper(searx_host=searx_host, unsecure=True)
    
    # Manually instantiate the tool with the configured wrapper
    search = SearxSearchRun(wrapper=wrapper)
    
    enrichment_signals = {
        "crime_rate": f"crime rate statistics {zone_name}",
        "cleanliness": f"cleanliness and sanitation {zone_name}",
        "public_perception": f"public perception and reviews of {zone_name}",
        "investment_potential": f"real estate investment potential {zone_name}",
    }

    enriched_data: Dict[str, str] = {}
    
    print(f"--- Fetching enrichment data for: {zone_name} via SearxNG ---")
    for signal, query in enrichment_signals.items():
        print(f"Searching for: {query}")
        results = search.run(query)
        enriched_data[signal] = results
        time.sleep(1) # Be respectful to the public instance

    return enriched_data

def main():
    """
    Main function to run the enrichment tool from the command line.
    """
    parser = argparse.ArgumentParser(
        description="Fetch enrichment data for a given geographical zone using SearxNG."
    )
    parser.add_argument(
        "zone_name",
        type=str,
        help="The name of the area to search for (e.g., 'Salamanca district, Madrid').",
    )
    args = parser.parse_args()

    # Call the core function with the provided zone name
    data = fetch_searx_enrichment_data(args.zone_name)

    # Print the data as a JSON object for easy parsing
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main() 