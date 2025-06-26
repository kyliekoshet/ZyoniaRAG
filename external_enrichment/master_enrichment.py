"""
Master enrichment module for creating comprehensive neighborhood files.
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from .result_saver import ResultSaver
    from .config import SEARCH_CATEGORIES
except ImportError:
    from result_saver import ResultSaver
    from config import SEARCH_CATEGORIES


class MasterEnrichment:
    """Creates comprehensive neighborhood enrichment files from individual category results."""
    
    def __init__(self, results_dir: str = "../enrichment_results"):
        self.results_dir = results_dir
        self.result_saver = ResultSaver(results_dir)
    
    def _normalize_neighborhood(self, neighborhood: str) -> str:
        """Normalize neighborhood name for consistent matching."""
        # Remove commas first, then replace spaces and dashes with underscores
        normalized = neighborhood.lower()
        normalized = normalized.replace(",", "")  # Remove commas completely
        normalized = normalized.replace(" ", "_")   # Replace spaces with underscores
        normalized = normalized.replace("-", "_")   # Replace dashes with underscores
        # Remove any double underscores that might result
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")
    
    def find_neighborhood_files(self, neighborhood: str) -> List[str]:
        """
        Find all JSON files for a specific neighborhood.
        
        Args:
            neighborhood: Neighborhood name
            
        Returns:
            List of file paths for this neighborhood
        """
        if not os.path.exists(self.results_dir):
            return []
        
        neighborhood_lower = neighborhood.lower()
        matching_files = []
        
        # First try exact normalized matching
        normalized = self._normalize_neighborhood(neighborhood)
        pattern = os.path.join(self.results_dir, f"{normalized}_*.json")
        exact_files = glob.glob(pattern)
        matching_files.extend(exact_files)
        
        # Then try fuzzy matching for complex filenames
        for filename in os.listdir(self.results_dir):
            if not filename.endswith('.json') or 'complete_enrichment' in filename:
                continue
            
            filepath = os.path.join(self.results_dir, filename)
            if filepath in matching_files:
                continue  # Already found via exact match
            
            filename_lower = filename.lower()
            
            # Check if this file belongs to the neighborhood
            neighborhood_parts = neighborhood_lower.replace(',', '').split()
            
            # For "Malasaña, Madrid" check if both "malasaña" and "madrid" are in filename
            if len(neighborhood_parts) >= 2:
                if all(part in filename_lower for part in neighborhood_parts):
                    matching_files.append(filepath)
            # For single word neighborhoods
            elif len(neighborhood_parts) == 1 and neighborhood_parts[0] in filename_lower:
                matching_files.append(filepath)
        
        # Filter out master enrichment files to avoid recursion
        individual_files = [f for f in matching_files if "complete_enrichment" not in f and "master_enrichment" not in f]
        
        return sorted(list(set(individual_files)), key=os.path.getmtime)
    
    def load_individual_results(self, neighborhood: str) -> Dict[str, Any]:
        """
        Load and organize all individual category results for a neighborhood.
        
        Args:
            neighborhood: Neighborhood name
            
        Returns:
            Dictionary organized by category
        """
        files = self.find_neighborhood_files(neighborhood)
        categories_data = {}
        metadata = {
            'files_processed': [],
            'total_files': len(files),
            'last_updated': None
        }
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract category and results
                priority_category = data.get('priority_category')
                if priority_category and 'instant_results' in data:
                    category_result = data['instant_results'].get(priority_category)
                    if category_result:
                        categories_data[priority_category] = {
                            **category_result,
                            'query': data.get('query'),
                            'search_timestamp': data.get('timestamp'),
                            'source_file': os.path.basename(file_path)
                        }
                
                # Track metadata
                metadata['files_processed'].append(os.path.basename(file_path))
                file_time = data.get('timestamp', data.get('saved_at'))
                if file_time:
                    if not metadata['last_updated'] or file_time > metadata['last_updated']:
                        metadata['last_updated'] = file_time
                        
            except Exception as e:
                print(f"Warning: Could not process file {file_path}: {e}")
        
        return categories_data, metadata
    
    def create_master_enrichment(self, neighborhood: str, 
                                force_update: bool = False) -> Optional[str]:
        """
        Create a comprehensive master enrichment file for a neighborhood.
        
        Args:
            neighborhood: Neighborhood name
            force_update: Force creation even if recent master file exists
            
        Returns:
            Path to created master file, or None if failed
        """
        print(f"🏗️ Creating master enrichment for {neighborhood}")
        
        # Check if recent master file exists
        if not force_update:
            existing_master = self._find_existing_master(neighborhood)
            if existing_master:
                print(f"📁 Recent master file exists: {existing_master}")
                return existing_master
        
        # Load individual results
        categories_data, metadata = self.load_individual_results(neighborhood)
        
        if not categories_data:
            print(f"❌ No individual results found for {neighborhood}")
            return None
        
        # Create comprehensive enrichment
        master_enrichment = {
            'neighborhood': neighborhood,
            'enrichment_type': 'complete_neighborhood_analysis',
            'enrichment_summary': {
                'total_categories': len(categories_data),
                'available_categories': list(categories_data.keys()),
                'missing_categories': [cat for cat in SEARCH_CATEGORIES.keys() 
                                     if cat not in categories_data],
                'completeness_percentage': round((len(categories_data) / len(SEARCH_CATEGORIES)) * 100, 1)
            },
            'category_results': categories_data,
            'metadata': metadata,
            'created_at': datetime.now().isoformat(),
            'master_file_version': '1.0'
        }
        
        # Add neighborhood overview
        master_enrichment['neighborhood_overview'] = self._generate_overview(categories_data)
        
        # Save master file
        saved_path = self.result_saver.save_search_result(
            master_enrichment, 
            neighborhood, 
            'complete_enrichment'
        )
        
        if saved_path:
            print(f"✅ Master enrichment created: {saved_path}")
            print(f"📊 Includes {len(categories_data)} categories:")
            for category in categories_data.keys():
                print(f"   • {category}")
        
        return saved_path
    
    def _find_existing_master(self, neighborhood: str, max_age_hours: int = 1) -> Optional[str]:
        """Check if a recent master enrichment file exists."""
        normalized = self._normalize_neighborhood(neighborhood)
        pattern = os.path.join(self.results_dir, f"{normalized}_complete_enrichment_*.json")
        
        files = glob.glob(pattern)
        if not files:
            return None
        
        # Get most recent file
        latest_file = max(files, key=os.path.getmtime)
        
        # Check if it's recent enough
        file_age_hours = (datetime.now().timestamp() - os.path.getmtime(latest_file)) / 3600
        if file_age_hours <= max_age_hours:
            return latest_file
        
        return None
    
    def _generate_overview(self, categories_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate a text overview of the neighborhood based on available data."""
        overview = {}
        
        for category, data in categories_data.items():
            sources = data.get('sources', [])
            if sources:
                # Include full snippets from all sources instead of truncating
                all_snippets = []
                for source in sources:
                    snippet = source.get('snippet', '')
                    if snippet and len(snippet.strip()) > 20:  # Only include substantial content
                        all_snippets.append(snippet)
                
                # Combine all snippets with separator
                if all_snippets:
                    overview[category] = " | ".join(all_snippets)
                else:
                    overview[category] = "No detailed information available."
        
        return overview
    
    def auto_create_masters(self) -> List[str]:
        """
        Automatically create master files for all neighborhoods with individual results.
        
        Returns:
            List of created master file paths
        """
        print("🤖 Auto-creating master enrichment files...")
        
        # Find all neighborhoods with individual files
        neighborhoods = set()
        
        if os.path.exists(self.results_dir):
            for filename in os.listdir(self.results_dir):
                if filename.endswith('.json') and 'complete_enrichment' not in filename:
                    # Try to extract neighborhood from the filename
                    # Look for common patterns like "city_name" or "neighborhood_city"
                    parts = filename.replace('.json', '').split('_')
                    
                    # Look for Madrid files specifically and other patterns
                    if 'madrid' in filename.lower():
                        madrid_idx = next(i for i, part in enumerate(parts) if 'madrid' in part.lower())
                        
                        # Try to find the neighborhood part before madrid
                        if madrid_idx > 0:
                            # Take the part before madrid as neighborhood
                            neighborhood_part = parts[madrid_idx - 1]
                            if neighborhood_part not in ['the', 'in', 'of', 'potential', 'investment', 'crime', 'rate']:
                                neighborhood = f"{neighborhood_part.title()}, Madrid"
                                neighborhoods.add(neighborhood)
                        
                        # Also try combining multiple parts before madrid
                        if madrid_idx > 1:
                            # Check if there are two parts before madrid (e.g., "el rastro")
                            prev_parts = parts[max(0, madrid_idx-2):madrid_idx]
                            if len(prev_parts) >= 2 and all(p not in ['the', 'in', 'of', 'potential', 'investment'] for p in prev_parts):
                                neighborhood = f"{' '.join(prev_parts).title()}, Madrid"
                                neighborhoods.add(neighborhood)
                    
                    # For non-Madrid files, try other patterns
                    else:
                        # Skip if it's clearly not a neighborhood file
                        if any(skip in filename for skip in ['search', 'complete', 'master']):
                            continue
                        
                        # Try to extract from first few parts
                        if len(parts) >= 2:
                            # Take first 1-2 parts as potential neighborhood
                            neighborhood = ' '.join(parts[:2]).title()
                            neighborhoods.add(neighborhood)
        
        print(f"🔍 Found potential neighborhoods: {list(neighborhoods)}")
        
        created_files = []
        for neighborhood in neighborhoods:
            print(f"🏗️ Attempting to create master for: {neighborhood}")
            
            # Check if we actually have files for this neighborhood
            individual_files = self.find_neighborhood_files(neighborhood)
            if len(individual_files) >= 2:
                master_file = self.create_master_enrichment(neighborhood)
                if master_file:
                    created_files.append(master_file)
            else:
                print(f"⚠️ Only {len(individual_files)} files found for {neighborhood}, skipping")
        
        print(f"📁 Created {len(created_files)} master enrichment files")
        return created_files
    
    def create_master_for_similar_files(self, base_neighborhood: str = None) -> List[str]:
        """
        Create master files by grouping similar files together.
        Useful for handling complex filenames.
        
        Args:
            base_neighborhood: Optional base neighborhood to focus on
            
        Returns:
            List of created master file paths
        """
        print("🤖 Creating masters for similar files...")
        
        if not os.path.exists(self.results_dir):
            return []
        
        # Group files by similarity
        file_groups = {}
        
        for filename in os.listdir(self.results_dir):
            if not filename.endswith('.json') or 'complete_enrichment' in filename:
                continue
            
            # Extract key parts from filename to group similar files
            lower_name = filename.lower()
            
            # Group Madrid files by neighborhood mentions
            if 'madrid' in lower_name:
                if 'malasaña' in lower_name or 'malasana' in lower_name:
                    key = "Malasaña, Madrid"
                elif 'chamartin' in lower_name:
                    key = "Chamartin, Madrid"
                elif 'salamanca' in lower_name:
                    key = "Salamanca, Madrid"
                elif 'centro' in lower_name:
                    key = "Centro, Madrid"
                else:
                    key = "Madrid"
                
                if key not in file_groups:
                    file_groups[key] = []
                file_groups[key].append(filename)
        
        print(f"📊 Found file groups: {list(file_groups.keys())}")
        
        created_files = []
        for neighborhood, files in file_groups.items():
            if len(files) >= 2:
                print(f"🏗️ Creating master for {neighborhood} ({len(files)} files)")
                master_file = self.create_master_enrichment(neighborhood, force_update=True)
                if master_file:
                    created_files.append(master_file)
        
        return created_files


def test_master_enrichment():
    """Test function for master enrichment."""
    enricher = MasterEnrichment()
    
    # Test with Chamartin Madrid (we know we have files for this)
    neighborhood = "Chamartin, Madrid"
    
    print(f"Testing master enrichment for: {neighborhood}")
    print(f"Normalized neighborhood: {enricher._normalize_neighborhood(neighborhood)}")
    
    # Check what files exist
    print(f"Looking in directory: {enricher.results_dir}")
    if os.path.exists(enricher.results_dir):
        all_files = os.listdir(enricher.results_dir)
        json_files = [f for f in all_files if f.endswith('.json')]
        print(f"All JSON files in directory: {json_files}")
    
    # Find individual files
    files = enricher.find_neighborhood_files(neighborhood)
    print(f"Found {len(files)} individual files:")
    for file in files:
        print(f"  - {os.path.basename(file)}")
    
    # Create master enrichment
    master_file = enricher.create_master_enrichment(neighborhood, force_update=True)
    
    if master_file:
        print(f"✅ Master file created: {master_file}")
    else:
        print("❌ Failed to create master file")


if __name__ == "__main__":
    test_master_enrichment() 