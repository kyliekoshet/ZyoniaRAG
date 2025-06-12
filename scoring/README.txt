Scoring Engine Module (FR-3.2)
=============================

This module provides functions to compute a weighted score (0–100) for real estate properties based on user preferences, and to rank multiple properties accordingly.

Assumptions:
------------
- Property data is provided as a list of dictionaries, each with at least an 'id' and numeric fields (e.g., 'price', 'size', 'amenities').
- User weights are provided as a dictionary mapping field names to numeric weights (e.g., {'price': -10, 'size': 5, 'amenities': 2}). Negative weights mean lower values are preferred.
- Only fields present in both the property and the weights are considered for scoring.
- Numeric fields are min-max normalized across the provided properties. If all values are the same, normalization returns 0.5 for all.
- Non-numeric or missing values are ignored for scoring.
- The scoring logic is data-driven and can be easily adapted to new fields or formats.

What to Review When Dataset Arrives:
-----------------------------------
- Confirm the actual property field names and types (e.g., is 'size' always numeric? Are amenities a count or a list?).
- Check for any additional fields that should be included in scoring.
- Validate that all properties have unique IDs.
- Review the range and distribution of numeric fields for normalization.
- Adjust normalization or scoring logic if categorical or boolean fields are to be included.

Integration Notes:
------------------
- The module is plug-in ready for use after RAG retrieval, for side-by-side comparison tables, or for integration with user preference memory.
- To use, call `rank_properties(properties, weights)` with your property list and user weights.
- The code is dependency-light (only standard Python and typing).
- For integration, ensure that the property and weight formats match the expected input.

See `test_scoring_engine.py` for example usage and tests. 