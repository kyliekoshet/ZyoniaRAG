"""
Confidence scoring module for evaluating the quality and reliability of search results.
Provides confidence scores (0-100) to help RAG systems weight information appropriately.
"""

import re
import math
from datetime import datetime, timedelta
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Analyzes search results and assigns confidence scores for RAG optimization."""
    
    def __init__(self):
        # Source authority scores based on domain reliability
        self.authority_scores = {
            # Government/Official Sources (35-40 points)
            'gov.es': 40, 'madrid.es': 40, 'bcn.cat': 40, 'barcelona.cat': 40,
            'juntadeandalucia.es': 38, 'valencia.es': 38, 'sevilla.org': 38,
            'ine.es': 40, 'policia.es': 38, 'guardiacivil.es': 38,
            'gov.uk': 38, 'police.uk': 38, 'statistics.gov.uk': 38,
            'insee.fr': 38, 'gov.fr': 38, 'data.gov': 40,
            
            # Academic/Research Institutions (30-35 points)
            'edu': 35, 'ac.uk': 35, 'univ-': 33, 'csic.es': 35,
            'mit.edu': 35, 'ox.ac.uk': 35, 'cam.ac.uk': 35,
            
            # Established Media/News (25-30 points)
            'bbc.com': 30, 'theguardian.com': 30, 'elpais.com': 30,
            'lavanguardia.com': 28, 'elmundo.es': 28, 'abc.es': 28,
            'reuters.com': 30, 'lemonde.fr': 28, 'corriere.it': 28,
            
            # Official Tourism/City Guides (25-28 points)
            'bcn.travel': 28, 'timeout.com': 27, 'lonelyplanet.com': 28,
            'turismomadrid.es': 28, 'andalucia.org': 27,
            
            # Real Estate Platforms (20-28 points)
            'idealista.com': 28, 'fotocasa.es': 27, 'pisos.com': 26,
            'numbeo.com': 25, 'expatistan.com': 24, 'livingcost.org': 23,
            'rightmove.co.uk': 27, 'zoopla.co.uk': 26,
            
            # Travel/Review Aggregators (15-25 points)
            'tripadvisor.com': 20, 'booking.com': 18, 'airbnb.com': 19,
            'hostelworld.com': 17, 'hotels.com': 18,
            
            # Expat/Local Community Sites (18-22 points)
            'expatexchange.com': 22, 'internations.org': 21,
            'thelocal.es': 20, 'madrid-metropolitan.com': 19,
            
            # General Travel Blogs/Guides (10-18 points)
            'travelpander.com': 16, 'nomadicfanatic.com': 14,
            'backpackerguide.com': 15, 'budgettravel.com': 16,
            
            # Personal Blogs/Low Authority (5-12 points)
            'wordpress.com': 10, 'blogspot.com': 8, 'medium.com': 12,
            'wix.com': 8, 'weebly.com': 7
        }
        
        # Keywords that indicate high-quality, data-driven content
        self.quality_indicators = {
            'high': ['statistics', 'data', 'research', 'study', 'survey', 'report', 
                    'analysis', 'oficial', 'government', 'police', 'crime rate',
                    'estadísticas', 'datos', 'investigación', 'estudio'],
            'medium': ['guide', 'review', 'experience', 'local', 'resident',
                      'neighborhood', 'area', 'district', 'guía', 'experiencia'],
            'low': ['blog', 'opinion', 'personal', 'think', 'feel', 'maybe']
        }
        
        # Recency bonus factors
        self.recency_weights = {
            30: 10,    # Last 30 days: full points
            90: 8,     # Last 3 months: high points  
            365: 6,    # Last year: medium points
            730: 4,    # Last 2 years: some points
            1095: 2    # Last 3 years: minimal points
        }
    
    def get_domain_authority(self, url: str) -> int:
        """Get authority score for a domain."""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Direct domain match
            if domain in self.authority_scores:
                return self.authority_scores[domain]
            
            # Pattern matching for subdomains and common patterns
            for pattern, score in self.authority_scores.items():
                if pattern in domain:
                    return score
            
            # Special handling for common patterns
            if '.edu' in domain or '.ac.' in domain:
                return 35
            elif '.gov' in domain:
                return 38
            elif 'university' in domain or 'univ' in domain:
                return 33
            elif 'police' in domain or 'government' in domain:
                return 36
            
            # Default score for unknown domains
            return 15
            
        except Exception as e:
            logger.warning(f"Error parsing domain from {url}: {e}")
            return 10
    
    def analyze_content_quality(self, title: str, snippet: str, search_context: str) -> Dict[str, int]:
        """Analyze content quality across multiple dimensions."""
        content = f"{title} {snippet}".lower()
        search_lower = search_context.lower()
        
        # Neighborhood specificity (0-10)
        neighborhood_score = 0
        neighborhood_terms = ['neighborhood', 'district', 'area', 'barrio', 'distrito', 
                             'zone', 'quarter', 'sector']
        for term in neighborhood_terms:
            if term in content:
                neighborhood_score += 2
        neighborhood_score = min(neighborhood_score, 10)
        
        # Query relevance (0-10) 
        relevance_score = 0
        search_words = search_lower.split()
        for word in search_words:
            if len(word) > 3 and word in content:
                relevance_score += 1
        relevance_score = min(int(relevance_score * 1.5), 10)
        
        # Content depth (0-10)
        depth_score = 0
        high_indicators = sum(1 for indicator in self.quality_indicators['high'] if indicator in content)
        medium_indicators = sum(1 for indicator in self.quality_indicators['medium'] if indicator in content)
        low_indicators = sum(1 for indicator in self.quality_indicators['low'] if indicator in content)
        
        depth_score = min(high_indicators * 3 + medium_indicators * 2 - low_indicators, 10)
        depth_score = max(depth_score, 0)
        
        # Data richness (0-10)
        data_patterns = [r'\d+%', r'\d+\.\d+', r'statistics', r'data', r'rate', r'index']
        data_score = sum(2 for pattern in data_patterns if re.search(pattern, content))
        data_score = min(data_score, 10)
        
        return {
            'neighborhood_specificity': neighborhood_score,
            'query_relevance': relevance_score, 
            'content_depth': depth_score,
            'data_richness': data_score
        }
    
    def estimate_content_recency(self, title: str, snippet: str) -> int:
        """Estimate content recency and assign score (0-10)."""
        content = f"{title} {snippet}".lower()
        
        # Look for year indicators
        current_year = datetime.now().year
        recent_years = [str(year) for year in range(current_year-1, current_year+2)]
        
        recency_score = 0
        for year in recent_years:
            if year in content:
                if year == str(current_year):
                    recency_score = 10
                elif year == str(current_year-1):
                    recency_score = 8
                break
        
        # Look for recent update indicators
        recent_indicators = ['updated', 'recent', 'latest', 'current', '2025', '2024']
        for indicator in recent_indicators:
            if indicator in content:
                recency_score = max(recency_score, 6)
                break
        
        # Default moderate score if no clear indicators
        if recency_score == 0:
            recency_score = 5
            
        return recency_score
    
    def calculate_confidence_score(self, source: Dict, search_context: str = "") -> Dict[str, any]:
        """Calculate comprehensive confidence score for a source."""
        try:
            # Domain authority (40 points max)
            authority_score = self.get_domain_authority(source.get('url', ''))
            
            # Content quality analysis (40 points max)
            title = source.get('title', '')
            snippet = source.get('snippet', '')
            
            quality_metrics = self.analyze_content_quality(title, snippet, search_context)
            content_quality_score = sum(quality_metrics.values())  # Max 40
            
            # Technical quality (10 points max)
            technical_score = 0
            if source.get('content_enhanced', False):
                technical_score += 5
            if len(snippet) > 100:  # Substantial content
                technical_score += 3
            if source.get('url') != 'No URL':
                technical_score += 2
                
            # Recency estimate (10 points max)
            recency_score = self.estimate_content_recency(title, snippet)
            
            # Calculate total confidence (0-100)
            total_confidence = authority_score + content_quality_score + technical_score + recency_score
            total_confidence = min(total_confidence, 100)
            
            # Determine confidence level
            if total_confidence >= 80:
                confidence_level = "very_high"
            elif total_confidence >= 65:
                confidence_level = "high"
            elif total_confidence >= 50:
                confidence_level = "medium"
            elif total_confidence >= 35:
                confidence_level = "low"
            else:
                confidence_level = "very_low"
            
            return {
                'confidence_score': total_confidence,
                'confidence_level': confidence_level,
                'score_breakdown': {
                    'domain_authority': authority_score,
                    'content_quality': content_quality_score,
                    'technical_quality': technical_score,
                    'recency_estimate': recency_score
                },
                'quality_metrics': quality_metrics,
                'rag_weight': total_confidence / 100.0  # Normalized for RAG weighting
            }
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return {
                'confidence_score': 25,
                'confidence_level': "low",
                'score_breakdown': {'error': str(e)},
                'rag_weight': 0.25
            }
    
    def score_search_results(self, results: Dict, search_context: str = "") -> Dict:
        """Score all sources in search results and add confidence metadata."""
        if not results.get('sources'):
            return results
        
        scored_sources = []
        confidence_summary = {
            'very_high': 0, 'high': 0, 'medium': 0, 'low': 0, 'very_low': 0
        }
        total_scores = []
        
        for source in results['sources']:
            confidence_data = self.calculate_confidence_score(source, search_context)
            
            # Add confidence data to source
            enhanced_source = source.copy()
            enhanced_source.update(confidence_data)
            scored_sources.append(enhanced_source)
            
            # Track summary stats
            confidence_summary[confidence_data['confidence_level']] += 1
            total_scores.append(confidence_data['confidence_score'])
        
        # Calculate aggregate confidence metrics
        avg_confidence = sum(total_scores) / len(total_scores) if total_scores else 0
        max_confidence = max(total_scores) if total_scores else 0
        high_quality_count = confidence_summary['very_high'] + confidence_summary['high']
        
        # Update results with confidence data
        enhanced_results = results.copy()
        enhanced_results['sources'] = scored_sources
        enhanced_results['confidence_analysis'] = {
            'average_confidence': round(avg_confidence, 1),
            'max_confidence': max_confidence,
            'high_quality_sources': high_quality_count,
            'total_sources': len(scored_sources),
            'confidence_distribution': confidence_summary,
            'overall_reliability': 'high' if avg_confidence >= 70 else 'medium' if avg_confidence >= 50 else 'low'
        }
        
        return enhanced_results


def test_confidence_scorer():
    """Test the confidence scoring system."""
    scorer = ConfidenceScorer()
    
    # Test sources
    test_sources = [
        {
            'title': 'Madrid Crime Statistics 2024 - Official Police Report',
            'url': 'https://policia.es/madrid-crime-stats',
            'snippet': 'Official crime statistics for Madrid districts show Salamanca has a crime rate of 2.1 per 1000 residents...',
            'content_enhanced': True
        },
        {
            'title': 'My Experience Living in Salamanca - Travel Blog',
            'url': 'https://mytravelblog.wordpress.com/salamanca',
            'snippet': 'I think Salamanca is pretty safe, but maybe avoid walking alone at night...',
            'content_enhanced': False
        }
    ]
    
    # Test results structure
    test_results = {
        'sources': test_sources,
        'total_results': 2
    }
    
    # Score the results
    scored_results = scorer.score_search_results(test_results, "crime rate Salamanca Madrid")
    
    print("Confidence Scoring Test Results:")
    print("=" * 50)
    for i, source in enumerate(scored_results['sources'], 1):
        print(f"\nSource {i}: {source['title'][:50]}...")
        print(f"Confidence Score: {source['confidence_score']}/100")
        print(f"Confidence Level: {source['confidence_level']}")
        print(f"RAG Weight: {source['rag_weight']:.2f}")
        print(f"Domain Authority: {source['score_breakdown']['domain_authority']}")
    
    print(f"\nOverall Analysis:")
    print(f"Average Confidence: {scored_results['confidence_analysis']['average_confidence']}")
    print(f"Overall Reliability: {scored_results['confidence_analysis']['overall_reliability']}")


if __name__ == "__main__":
    test_confidence_scorer() 