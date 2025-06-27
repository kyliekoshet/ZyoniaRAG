#!/usr/bin/env python3
"""
Structured Data Extractor for neighborhood search results.
Extracts specific metrics, prices, statistics, and facts from text blobs.
"""

import re
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StructuredExtractor:
    """Extract structured data from search result snippets."""
    
    def __init__(self):
        """Initialize the structured extractor with regex patterns."""
        self.price_patterns = [
            r'€\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per\s*)?(?:m²|metro|square)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*euros?\s*(?:per\s*)?(?:m²|metro|square)',
            r'price.*?€\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*)\s*€/m²',
            r'alcanza\s*los\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*euros?\s*por\s*metro'
        ]
        
        self.percentage_patterns = [
            r'(\d{1,2}(?:\.\d{1,2})?)\s*%\s*(?:annual|yearly|year|interanual)',
            r'incremento.*?(\d{1,2}(?:\.\d{1,2})?)\s*%',
            r'increase.*?(\d{1,2}(?:\.\d{1,2})?)\s*%',
            r'growth.*?(\d{1,2}(?:\.\d{1,2})?)\s*%',
            r'(\d{1,2}(?:\.\d{1,2})?)\s*%.*?increase'
        ]
        
        self.crime_patterns = [
            r'(\d{1,4})\s*(?:cases|incidents|crimes).*?(?:theft|robbery|crime)',
            r'(\d{1,3})\s*incidents?\s*per\s*1,?000\s*residents',
            r'crime\s*rate.*?(\d{1,2}(?:\.\d{1,2})?)',
            r'(\d{1,4})\s*reported.*?crimes?',
            r'safety\s*rating.*?(\d{1,2}(?:\.\d{1,2})?)'
        ]
        
        self.rating_patterns = [
            r'rated?\s*(\d{1,2}(?:\.\d{1,2})?)\s*(?:of|out\s*of|/)\s*(\d{1,2})',
            r'puntuación.*?(\d{1,2}(?:\.\d{1,2})?)\s*sobre\s*(\d{1,2})',
            r'(\d{1,2}(?:\.\d{1,2})?)\s*stars?',
            r'score.*?(\d{1,2}(?:\.\d{1,2})?)'
        ]
        
        self.cleanliness_patterns = [
            r'Air Quality Index.*?(\d{1,3})',
            r'AQI.*?(\d{1,3})',
            r'PM2\.5.*?(\d{1,3})',
            r'air quality.*?(Good|Moderate|Poor|Very Poor|Excellent)',
            r'cleanliness.*?rating.*?(\d{1,2})',
            r'maintenance.*?score.*?(\d{1,2})',
            r'street.*?cleaning.*?(daily|weekly|regular|excellent|good|poor)',
            r'garbage.*?collection.*?(daily|weekly|regular|excellent|good|poor)',
            r'waste.*?management.*?(excellent|good|poor|adequate)'
        ]
        
        self.noise_phrases = [
            'discover detailed insights', 'learn about', 'smart strategies', 
            'comprehensive guide', 'book now', 'see reviews', 'contact us',
            'great deals for', 'lowest rate guaranteed', 'best price guarantee',
            'exclusive deal alerts', 'want exclusive', 'sign in', 'overview reviews',
            'fully refundable rates', 'free cancellation', 'minutes away',
            'this hotel also features', 'all rooms have'
        ]
    
    def extract_prices(self, text: str) -> Dict[str, Any]:
        """Extract price information from text."""
        prices = {}
        
        for pattern in self.price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Clean and convert price
                price_str = matches[0].replace(',', '').replace('.', '')
                try:
                    price = float(price_str)
                    if 1000 <= price <= 50000:  # Reasonable price range for €/m²
                        prices['price_per_sqm'] = price
                        prices['currency'] = 'EUR'
                        break
                except ValueError:
                    continue
        
        # Extract total prices (for projects, investments)
        total_price_patterns = [
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{3})?)\s*euros?\s*(?:project|investment|total)',
            r'project.*?(\d{1,3}(?:,\d{3})*(?:\.\d{3})?)\s*euros?',
            r'investment.*?(\d{1,3}(?:,\d{3})*(?:\.\d{3})?)\s*euros?'
        ]
        
        for pattern in total_price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                price_str = matches[0].replace(',', '').replace('.', '')
                try:
                    price = float(price_str)
                    if price >= 100000:  # Reasonable for total investment
                        prices['total_investment'] = price
                        prices['currency'] = 'EUR'
                        break
                except ValueError:
                    continue
        
        return prices
    
    def extract_percentages(self, text: str) -> Dict[str, float]:
        """Extract percentage data (growth rates, increases, etc.)."""
        percentages = {}
        
        for pattern in self.percentage_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    pct = float(matches[0])
                    if 0 <= pct <= 100:  # Reasonable percentage range
                        if 'annual' in pattern or 'yearly' in pattern or 'interanual' in pattern:
                            percentages['annual_growth'] = pct
                        elif 'trimestral' in text.lower():
                            percentages['quarterly_growth'] = pct
                        else:
                            percentages['growth_rate'] = pct
                        break
                except ValueError:
                    continue
        
        return percentages
    
    def extract_crime_stats(self, text: str) -> Dict[str, Any]:
        """Extract crime and safety statistics."""
        crime_stats = {}
        
        for pattern in self.crime_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    stat = float(matches[0])
                    if 'per 1' in pattern:
                        crime_stats['incidents_per_1000'] = stat
                    elif 'cases' in pattern or 'incidents' in pattern:
                        crime_stats['total_incidents'] = stat
                    elif 'rating' in pattern:
                        crime_stats['safety_rating'] = stat
                    break
                except ValueError:
                    continue
        
        # Extract safety descriptors
        safety_terms = {
            'very safe': 9, 'extremely safe': 9, 'safest': 9,
            'safe': 7, 'generally safe': 7, 'mostly safe': 7,
            'somewhat safe': 5, 'moderately safe': 5,
            'unsafe': 3, 'dangerous': 2, 'high crime': 2, 'high-risk': 2
        }
        
        text_lower = text.lower()
        for term, score in safety_terms.items():
            if term in text_lower:
                crime_stats['safety_descriptor'] = term
                crime_stats['safety_score'] = score
                break
        
        return crime_stats
    
    def extract_ratings(self, text: str) -> Dict[str, Any]:
        """Extract ratings and scores."""
        ratings = {}
        
        for pattern in self.rating_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    if len(matches[0]) == 2:  # Rating with scale (e.g., "4 of 5")
                        rating = float(matches[0][0])
                        scale = float(matches[0][1])
                        normalized_rating = (rating / scale) * 10
                        ratings['rating'] = rating
                        ratings['scale'] = scale
                        ratings['normalized_rating'] = normalized_rating
                    else:
                        rating = float(matches[0])
                        ratings['rating'] = rating
                    break
                except (ValueError, IndexError):
                    continue
        
        return ratings
    
    def extract_cleanliness_stats(self, text: str) -> Dict[str, Any]:
        """Extract cleanliness and environmental quality statistics."""
        cleanliness_stats = {}
        
        for pattern in self.cleanliness_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    if 'Air Quality Index' in pattern or 'AQI' in pattern:
                        aqi = float(matches[0])
                        cleanliness_stats['air_quality_index'] = aqi
                        # Convert AQI to descriptive rating
                        if aqi <= 50:
                            cleanliness_stats['air_quality_rating'] = 'Good'
                        elif aqi <= 100:
                            cleanliness_stats['air_quality_rating'] = 'Moderate'
                        elif aqi <= 150:
                            cleanliness_stats['air_quality_rating'] = 'Poor'
                        else:
                            cleanliness_stats['air_quality_rating'] = 'Very Poor'
                    elif 'PM2.5' in pattern:
                        pm25 = float(matches[0])
                        cleanliness_stats['pm25_level'] = pm25
                    elif 'air quality' in pattern:
                        cleanliness_stats['air_quality_rating'] = matches[0]
                    elif 'cleanliness' in pattern or 'maintenance' in pattern:
                        score = float(matches[0])
                        cleanliness_stats['cleanliness_score'] = score
                    elif 'street' in pattern or 'garbage' in pattern or 'waste' in pattern:
                        service_quality = matches[0].lower()
                        if service_quality in ['daily', 'weekly', 'regular']:
                            cleanliness_stats['service_frequency'] = service_quality
                        elif service_quality in ['excellent', 'good', 'poor', 'adequate']:
                            cleanliness_stats['service_quality'] = service_quality
                    break
                except (ValueError, IndexError):
                    continue
        
        # Extract cleanliness descriptors
        cleanliness_terms = {
            'very clean': 9, 'extremely clean': 9, 'spotless': 9, 'immaculate': 9,
            'clean': 7, 'well-maintained': 7, 'tidy': 7, 'neat': 7,
            'average cleanliness': 5, 'moderately clean': 5,
            'dirty': 3, 'messy': 3, 'poorly maintained': 3,
            'very dirty': 1, 'filthy': 1, 'neglected': 1
        }
        
        text_lower = text.lower()
        for term, score in cleanliness_terms.items():
            if term in text_lower:
                cleanliness_stats['cleanliness_descriptor'] = term
                cleanliness_stats['cleanliness_score'] = score
                break
        
        return cleanliness_stats
    
    def extract_key_facts(self, text: str, category: str) -> List[str]:
        """Extract key factual statements relevant to the category."""
        facts = []
        
        # Category-specific fact patterns
        fact_patterns = {
            'crime_rate': [
                r'[^.]*(?:safe|safety|crime|security|police)[^.]*\.',
                r'[^.]*(?:incidents?|theft|robbery|violence)[^.]*\.',
                r'[^.]*(?:patrol|well-lit|secure)[^.]*\.'
            ],
            'investment_potential': [
                r'[^.]*(?:price|investment|market|growth|appreciation)[^.]*\.',
                r'[^.]*(?:rental|yield|ROI|return)[^.]*\.',
                r'[^.]*(?:demand|supply|development)[^.]*\.'
            ],
            'public_perception': [
                r'[^.]*(?:residents?|locals?|people|community)[^.]*\.',
                r'[^.]*(?:experience|living|life|atmosphere)[^.]*\.',
                r'[^.]*(?:reputation|known for|famous)[^.]*\.'
            ],
            'cleanliness': [
                r'[^.]*(?:clean|maintenance|sanitation|hygiene|well-maintained)[^.]*\.',
                r'[^.]*(?:garbage|waste|environment|air quality|pollution)[^.]*\.',
                r'[^.]*(?:streets?|public spaces?|neighborhood|area)[^.]*\.',
                r'[^.]*(?:AQI|Air Quality Index|PM2\.5)[^.]*\.',
                r'[^.]*(?:street cleaning|waste management|upkeep)[^.]*\.'
            ],
            'general_info': [
                r'[^.]*(?:location|situated|proximity)[^.]*\.',
                r'[^.]*(?:amenities|facilities|services)[^.]*\.',
                r'[^.]*(?:transport|metro|bus|connection)[^.]*\.'
            ]
        }
        
        patterns = fact_patterns.get(category, fact_patterns['general_info'])
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                fact = match.strip()
                if len(fact) > 20 and len(fact) < 200:  # Reasonable fact length
                    # Clean the fact
                    fact = self.clean_text(fact)
                    if fact and not any(noise in fact.lower() for noise in self.noise_phrases):
                        facts.append(fact)
        
        return facts[:5]  # Limit to top 5 facts
    
    def clean_text(self, text: str) -> str:
        """Remove noise and clean text."""
        if not text:
            return ""
        
        # Remove noise phrases
        text_lower = text.lower()
        for noise in self.noise_phrases:
            if noise in text_lower:
                # Replace noise phrase with empty string
                text = re.sub(re.escape(noise), '', text, flags=re.IGNORECASE)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove incomplete sentences at the beginning/end
        sentences = text.split('.')
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and sentence[0].isupper():
                cleaned_sentences.append(sentence)
        
        return '. '.join(cleaned_sentences) + '.' if cleaned_sentences else text
    
    def _validate_metric_context(self, snippet: str, neighborhood: str, metric_name: str, metric_value: Any) -> bool:
        """
        Validate that an extracted metric actually refers to the target neighborhood.
        
        Args:
            snippet: Text snippet where metric was found
            neighborhood: Target neighborhood name
            metric_name: Name of the extracted metric
            metric_value: Value of the extracted metric
            
        Returns:
            True if metric is contextually valid for the neighborhood
        """
        if not neighborhood or not snippet:
            return False
            
        snippet_lower = snippet.lower()
        neighborhood_parts = [part.strip().lower() for part in neighborhood.split(',')]
        primary_neighborhood = neighborhood_parts[0] if neighborhood_parts else neighborhood.lower()
        
        # Check for exclusionary phrases that indicate the metric refers to something else
        exclusionary_phrases = [
            'other areas', 'outskirts', 'surrounding areas', 'nearby areas',
            'different neighborhood', 'another district', 'other districts',
            'outside', 'exterior', 'peripheral', 'suburbs', 'metropolitan area',
            'not in', 'excluding', 'except for', 'apart from'
        ]
        
        # If exclusionary phrases are present, reject immediately
        if any(phrase in snippet_lower for phrase in exclusionary_phrases):
            logger.warning(f"Metric {metric_name}={metric_value} excluded due to exclusionary context")
            return False
        
        # Split into sentences and check each one
        sentences = snippet.split('.')
        for sentence in sentences:
            sentence_lower = sentence.strip().lower()
            
            # If sentence contains the metric value, check if it's neighborhood-specific
            metric_variations = [
                str(metric_value).replace('.0', ''),  # Remove .0 from floats
                str(int(float(metric_value))) if isinstance(metric_value, (int, float)) else str(metric_value),
                f"{metric_value:,.0f}" if isinstance(metric_value, (int, float)) else str(metric_value)  # With commas
            ]
            
            sentence_has_metric = any(var in sentence for var in metric_variations)
            if not sentence_has_metric:
                continue
                
            # Check if the sentence mentions the target neighborhood
            neighborhood_in_sentence = any(part in sentence_lower for part in neighborhood_parts if len(part) > 2)
            
            if neighborhood_in_sentence:
                logger.info(f"Metric {metric_name}={metric_value} validated - found in neighborhood-specific sentence")
                return True
                
            # If no neighborhood mentioned in this sentence, but it's a price/metric sentence
            # and no exclusionary context, be more permissive for very specific contexts
            if (metric_name in ['price_per_sqm', 'annual_growth'] and 
                any(keyword in sentence_lower for keyword in ['real estate', 'property', 'investment', 'market', 'price'])):
                # Only accept if the overall snippet clearly talks about the target neighborhood
                snippet_mentions_neighborhood = any(part in snippet_lower for part in neighborhood_parts if len(part) > 2)
                if snippet_mentions_neighborhood:
                    logger.info(f"Metric {metric_name}={metric_value} validated - real estate context with neighborhood mention")
                    return True
        
        # Conservative rejection if no clear context
        logger.warning(f"No clear neighborhood context found for metric {metric_name}={metric_value}")
        return False
    
    def extract_structured_data(self, snippet: str, category: str, neighborhood: str) -> Dict[str, Any]:
        """
        Main method to extract all structured data from a snippet with context validation.
        
        Args:
            snippet: Raw text snippet from search results
            category: Search category (crime_rate, investment_potential, etc.)
            neighborhood: Neighborhood name for context
            
        Returns:
            Dictionary with structured data
        """
        if not snippet:
            return {}
        
        try:
            structured_data = {
                'original_snippet': snippet,
                'cleaned_snippet': self.clean_text(snippet),
                'extracted_metrics': {},
                'key_facts': [],
                'data_quality': 'low',
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            # Extract category-specific data (raw extraction)
            raw_metrics = {}
            if category == 'investment_potential':
                raw_metrics.update(self.extract_prices(snippet))
                raw_metrics.update(self.extract_percentages(snippet))
            elif category == 'crime_rate':
                raw_metrics.update(self.extract_crime_stats(snippet))
            elif category == 'cleanliness':
                raw_metrics.update(self.extract_cleanliness_stats(snippet))
            elif category == 'public_perception':
                raw_metrics.update(self.extract_ratings(snippet))
            
            # Validate each metric against neighborhood context
            validated_metrics = {}
            for metric_name, metric_value in raw_metrics.items():
                if self._validate_metric_context(snippet, neighborhood, metric_name, metric_value):
                    validated_metrics[metric_name] = metric_value
                else:
                    logger.info(f"Rejected metric {metric_name}={metric_value} - no valid context for {neighborhood}")
            
            structured_data['extracted_metrics'] = validated_metrics
            
            # Extract key facts for all categories
            structured_data['key_facts'] = self.extract_key_facts(snippet, category)
            
            # Assess data quality
            metric_count = len(structured_data['extracted_metrics'])
            fact_count = len(structured_data['key_facts'])
            
            if metric_count >= 2 and fact_count >= 3:
                structured_data['data_quality'] = 'high'
            elif metric_count >= 1 and fact_count >= 2:
                structured_data['data_quality'] = 'medium'
            else:
                structured_data['data_quality'] = 'low'
            
            logger.info(f"Extracted {metric_count} metrics and {fact_count} facts for {neighborhood} {category}")
            return structured_data
            
        except Exception as e:
            logger.error(f"Error in structured extraction: {e}")
            return {
                'original_snippet': snippet,
                'extraction_error': str(e),
                'data_quality': 'error'
            }


def test_structured_extractor():
    """Test function for structured extractor."""
    extractor = StructuredExtractor()
    
    # Test investment data
    investment_text = """
    El precio medio de la vivienda en Tetuán alcanza los 5.044 euros por metro cuadrado, 
    lo que supone un incremento interanual del 14,5% y un aumento trimestral del 5,3%, 
    según los datos de Brains Real Estate. Nuevo proyecto de inversión en Tetuán (Madrid): 
    750.000 euros, con prefunding, para desarrollar apartamentos turísticos.
    """
    
    result = extractor.extract_structured_data(investment_text, 'investment_potential', 'Tetuan')
    print("Investment extraction test:")
    print(f"Metrics: {result.get('extracted_metrics', {})}")
    print(f"Facts: {result.get('key_facts', [])}")
    print(f"Quality: {result.get('data_quality', 'unknown')}")
    
    # Test crime data
    crime_text = """
    Salamanca is one of the safest neighborhoods in Madrid. The local police have reported 
    only 12 incidents per 1,000 residents in the first half of 2023, making it one of the 
    safest places in Madrid. Crime rates are generally low and the area is well-policed.
    """
    
    result = extractor.extract_structured_data(crime_text, 'crime_rate', 'Salamanca')
    print("\nCrime extraction test:")
    print(f"Metrics: {result.get('extracted_metrics', {})}")
    print(f"Facts: {result.get('key_facts', [])}")
    print(f"Quality: {result.get('data_quality', 'unknown')}")


if __name__ == "__main__":
    test_structured_extractor() 