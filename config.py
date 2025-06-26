# System Settings
SEARCH_SETTINGS = {
    "priority_timeout": 5.0,  # Max time for priority search (seconds)
    "background_timeout": 15.0,  # Max time for background searches
    "max_results_per_category": 10,  # Number of search results per category (increased)
    "cache_ttl_hours": 24,  # Cache time-to-live in hours
    "retry_attempts": 3,  # Number of retry attempts per instance
    "delay_between_searches": 3.0,  # Delay between searches (increased for rate limiting)
    "fallback_delay": 5.0,  # Delay before trying next instance (increased)
    "rate_limit_backoff": 10.0,  # Backoff time when rate limited
    "max_searches_per_minute": 15,  # Maximum searches per minute
    "multiple_search_terms": True,  # Use multiple search terms per category
    "max_search_terms_per_category": 3  # How many different search terms to try per category
} 