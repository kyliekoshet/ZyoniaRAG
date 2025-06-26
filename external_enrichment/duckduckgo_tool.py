import time
from langchain_community.tools import DuckDuckGoSearchResults
from typing import Dict

def get_zone_enrichment_data(zone_name: str) -> Dict[str, str]:
    """
    Fetches raw enrichment information for a given property zone using DuckDuckGo.

    This function performs targeted searches for different enrichment signals
    (crime rate, cleanliness, public perception, investment potential) and
    returns the raw search result snippets for each category.

    This raw data can then be passed to a downstream LLM (like in the LLM Manager)
    to be summarized into the final structured format.

    Args:
        zone_name: The name of the area to search for (e.g., "Salamanca district, Madrid").

    Returns:
        A dictionary where keys are enrichment categories and values are the
        raw string of search result snippets.
    """
    search = DuckDuckGoSearchResults()
    
    enrichment_signals = {
        "crime_rate": f"crime rate statistics {zone_name}",
        "cleanliness": f"cleanliness and sanitation {zone_name}",
        "public_perception": f"public perception and reviews of {zone_name}",
        "investment_potential": f"real estate investment potential {zone_name}",
    }

    enriched_data: Dict[str, str] = {}
    
    print(f"--- Fetching enrichment data for: {zone_name} ---")
    for signal, query in enrichment_signals.items():
        print(f"Searching for: {query}")
        results = search.run(query)
        enriched_data[signal] = results
        time.sleep(1) # Add a 1-second delay to avoid rate limiting

    return enriched_data 