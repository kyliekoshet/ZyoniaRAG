"""
Configuration settings for the hybrid search strategy system.
"""

# Note: SearxNG instances removed as system now uses DuckDuckGo only

# Search Categories Configuration
SEARCH_CATEGORIES = {
    "crime_rate": {
        "keywords": ["crime", "safety", "security", "dangerous", "theft", "robbery", "safe", "unsafe", "violence", "police", "seguridad", "crimen", "delincuencia"],
        "patterns": [
            r"crime\s*rate",
            r"how\s+safe",
            r"is\s+\w+\s+safe",
            r"safety\s+in",
            r"dangerous\s+area",
            r"seguridad\s+en",
            r"es\s+seguro"
        ],
        "search_terms": [
            "{neighborhood} crime rate safety statistics security",
            "{neighborhood} police reports crime statistics data",
            "{neighborhood} safety guide dangerous areas avoid",
            "{neighborhood} seguridad delincuencia estadisticas",
            "{neighborhood} neighborhood safety walking night"
        ]
    },
    "cleanliness": {
        "keywords": ["clean", "dirty", "garbage", "maintenance", "sanitation", "hygiene", "tidy", "messy", "limpio", "sucio", "limpieza", "well-maintained", "street cleaning", "waste management"],
        "patterns": [
            r"how\s+clean",
            r"cleanliness",
            r"clean\s+is",
            r"maintenance",
            r"well\s*maintained",
            r"street\s*cleaning",
            r"garbage\s*collection",
            r"qué\s+tal\s+la\s+limpieza",
            r"está\s+limpio"
        ],
        "search_terms": [
            "{neighborhood} clean streets well maintained neighborhood",
            "{neighborhood} garbage collection street cleaning services",
            "{neighborhood} public spaces maintenance cleanliness",
            "{neighborhood} limpieza calles mantenimiento urbano",
            "{neighborhood} neighborhood upkeep clean safe area",
            "{neighborhood} waste management street maintenance",
            "{neighborhood} well kept clean public areas"
        ]
    },
    "public_perception": {
        "keywords": ["opinion", "review", "reputation", "perception", "experience", "think", "feel", "locals", "residents", "opinión", "reseñas", "experiencia"],
        "patterns": [
            r"what.*think",
            r"people\s+say",
            r"reputation",
            r"living\s+experience",
            r"resident.*opinion",
            r"qué.*opinan",
            r"experiencia.*vivir"
        ],
        "search_terms": [
            "{neighborhood} resident reviews living experience",
            "{neighborhood} locals opinions neighborhood life",
            "{neighborhood} what people say about living",
            "{neighborhood} opiniones residentes experiencia",
            "{neighborhood} neighborhood reputation community feel"
        ]
    },
    "investment_potential": {
        "keywords": ["investment", "property", "real estate", "market", "prices", "buy", "invest", "value", "appreciation", "inversión", "inmobiliario", "precios"],
        "patterns": [
            r"investment\s+potential",
            r"should.*invest",
            r"real\s+estate",
            r"property\s+market",
            r"buy.*property",
            r"potencial.*inversión",
            r"mercado.*inmobiliario"
        ],
        "search_terms": [
            "{neighborhood} real estate investment market analysis",
            "{neighborhood} property prices trends investment guide",
            "{neighborhood} housing market investment opportunities",
            "{neighborhood} inversión inmobiliaria mercado precios",
            "{neighborhood} buy property investment potential value"
        ]
    },
    "general_info": {
        "keywords": ["about", "information", "overview", "description", "tell", "guide", "what", "like", "información", "sobre", "guía"],
        "patterns": [
            r"tell.*about",
            r"what.*like",
            r"information.*about",
            r"overview",
            r"guide.*to",
            r"información.*sobre",
            r"cómo.*es"
        ],
        "search_terms": [
            "{neighborhood} neighborhood guide amenities lifestyle",
            "{neighborhood} area overview attractions restaurants",
            "{neighborhood} living guide local life culture",
            "{neighborhood} guía barrio información general",
            "{neighborhood} what to know local attractions dining"
        ]
    }
}

# System Settings
SEARCH_SETTINGS = {
    "priority_timeout": 3.0,  # Max time for priority search (seconds)
    "background_timeout": 10.0,  # Max time for background searches
    "max_results_per_category": 5,  # Number of search results per category
    "cache_ttl_hours": 24,  # Cache time-to-live in hours
    "retry_attempts": 3,  # Number of retry attempts per instance
    "delay_between_searches": 3.0,  # Delay between searches (increased for rate limiting)
    "fallback_delay": 5.0,  # Delay before trying next instance (increased)
    "rate_limit_backoff": 10.0,  # Backoff time when rate limited
    "max_searches_per_minute": 15  # Maximum searches per minute
}

# Result formatting
RESULT_FORMAT = {
    "include_urls": True,
    "include_snippets": True,
    "include_timestamps": True,
    "include_search_metadata": True
} 