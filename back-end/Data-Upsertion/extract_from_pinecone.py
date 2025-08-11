"""
Pinecone Data Extraction Script

This script extracts all data from a Pinecone index and saves it to various formats
for analysis, backup, or migration purposes.

Author: Asset Management Chatbot System
Phase: Data Extraction and Analysis
"""

import os
import pandas as pd
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from pinecone import Pinecone
import logging
import time
from datetime import datetime

def clean_data_for_json(data: Any) -> Any:
    """
    Recursively clean data to make it JSON serializable.
    
    Args:
        data: Data to clean
        
    Returns:
        JSON-serializable version of the data
    """
    if isinstance(data, dict):
        return {k: clean_data_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    elif hasattr(data, '__dict__'):
        # Convert objects with attributes to dictionaries
        try:
            obj_dict = {}
            for key, value in data.__dict__.items():
                if not key.startswith('_'):  # Skip private attributes
                    obj_dict[key] = clean_data_for_json(value)
            return obj_dict
        except:
            return str(data)
    elif hasattr(data, 'metadata') and hasattr(data, 'id'):
        # Handle Vector objects specifically
        return {
            'id': getattr(data, 'id', ''),
            'values': list(getattr(data, 'values', [])) if hasattr(data, 'values') else [],
            'metadata': dict(getattr(data, 'metadata', {})) if hasattr(data, 'metadata') else {},
            'score': getattr(data, 'score', 0) if hasattr(data, 'score') else 0
        }
    else:
        # For primitive types and other serializable objects
        try:
            json.dumps(data)  # Test if it's serializable
            return data
        except:
            return str(data)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PineconeDataExtractor:
    """
    Handles extraction of all data from a Pinecone index.
    """
    
    def __init__(self, index_name: Optional[str] = None):
        """
        Initialize the extractor with configuration from environment variables.
        
        Args:
            index_name: Optional custom index name (defaults to env variable)
        """
        # Load environment variables
        load_dotenv()
        
        self.index_name = index_name or os.getenv('PINECONE_INDEX_NAME', 'hkp-amcdata')
        
        # Initialize Pinecone client
        self._initialize_pinecone_client()
        
        # Configuration
        self.batch_size = 100  # Fetch batch size
        self.query_dimension = 1536  # text-embedding-3-small dimension
        
    def _initialize_pinecone_client(self) -> None:
        """Initialize Pinecone client and connect to index."""
        try:
            self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            
            # Check if index exists
            if self.index_name not in self.pc.list_indexes().names():
                raise ValueError(f"Index '{self.index_name}' not found in Pinecone")
            
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
            # Get index stats
            stats = self.index.describe_index_stats()
            logger.info(f"Index stats: {stats}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client: {e}")
            raise
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vector_count': stats.get('total_vector_count', 0),
                'dimension': stats.get('dimension', 0),
                'index_fullness': stats.get('index_fullness', 0),
                'namespaces': stats.get('namespaces', {}),
                'extraction_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}
    
    def extract_all_vector_ids(self) -> List[str]:
        """
        Extract all vector IDs from the index using the list operation.
        
        Returns:
            List of all vector IDs
        """
        logger.info("Extracting all vector IDs...")
        all_ids = []
        
        try:
            # Use query with a dummy vector to get all IDs
            # This is a workaround since Pinecone doesn't have a direct list_all method
            dummy_vector = [0.0] * self.query_dimension
            
            # Query to get some results first
            results = self.index.query(
                vector=dummy_vector,
                top_k=10000,  # Maximum allowed
                include_metadata=False,
                include_values=False
            )
            
            # Extract IDs from results
            matches = getattr(results, 'matches', [])
            for match in matches:
                all_ids.append(match['id'])
            
            logger.info(f"Extracted {len(all_ids)} vector IDs using query method")
            
        except Exception as e:
            logger.warning(f"Query method failed: {e}")
            logger.info("Trying alternative extraction methods...")
            
            # Alternative: Try to fetch using known pattern (if any)
            # This would require knowledge of your ID pattern
            # For now, we'll proceed with what we have
            
        return all_ids
    
    def fetch_vectors_batch(self, ids: List[str]) -> Dict[str, Any]:
        """
        Fetch a batch of vectors by their IDs.
        
        Args:
            ids: List of vector IDs to fetch
            
        Returns:
            Dictionary containing fetched vectors
        """
        try:
            response = self.index.fetch(ids=ids)
            # Convert FetchResponse to dictionary format
            return {
                'vectors': dict(response.vectors) if hasattr(response, 'vectors') else {},
                'namespace': getattr(response, 'namespace', ''),
                'usage': getattr(response, 'usage', {})
            }
        except Exception as e:
            logger.error(f"Failed to fetch batch of {len(ids)} vectors: {e}")
            return {'vectors': {}}
    
    def extract_all_data(self) -> Dict[str, Any]:
        """
        Extract all data from the Pinecone index.
        
        Returns:
            Dictionary containing all extracted data
        """
        logger.info("Starting complete data extraction from Pinecone...")
        
        # Get index statistics
        stats = self.get_index_stats()
        logger.info(f"Index contains {stats.get('total_vector_count', 0)} vectors")
        
        # Extract all vector IDs
        all_ids = self.extract_all_vector_ids()
        
        if not all_ids:
            logger.warning("No vector IDs found. Trying alternative extraction...")
            return self._alternative_extraction()
        
        # Fetch all vectors in batches
        all_vectors = {}
        total_batches = (len(all_ids) + self.batch_size - 1) // self.batch_size
        
        for i in range(0, len(all_ids), self.batch_size):
            batch_ids = all_ids[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            
            logger.info(f"Fetching batch {batch_num}/{total_batches} ({len(batch_ids)} vectors)")
            
            batch_data = self.fetch_vectors_batch(batch_ids)
            
            if 'vectors' in batch_data:
                all_vectors.update(batch_data['vectors'])
            
            # Rate limiting
            time.sleep(0.1)
        
        logger.info(f"Successfully extracted {len(all_vectors)} vectors")
        
        return {
            'index_stats': stats,
            'vectors': all_vectors,
            'extraction_summary': {
                'total_vectors_extracted': len(all_vectors),
                'extraction_date': datetime.now().isoformat(),
                'index_name': self.index_name
            }
        }
    
    def _alternative_extraction(self) -> Dict[str, Any]:
        """
        Alternative extraction method using namespace queries.
        
        Returns:
            Dictionary containing extracted data
        """
        logger.info("Using alternative extraction method...")
        
        stats = self.get_index_stats()
        all_data = {
            'index_stats': stats,
            'vectors': {},
            'extraction_summary': {
                'total_vectors_extracted': 0,
                'extraction_date': datetime.now().isoformat(),
                'index_name': self.index_name,
                'method': 'alternative_namespace_query'
            }
        }
        
        # Try to query each namespace separately if they exist
        namespaces = stats.get('namespaces', {})
        
        if namespaces:
            for namespace_name in namespaces.keys():
                logger.info(f"Extracting from namespace: {namespace_name}")
                namespace_data = self._extract_from_namespace(namespace_name)
                all_data['vectors'].update(namespace_data)
        else:
            # Try default namespace
            logger.info("Extracting from default namespace")
            namespace_data = self._extract_from_namespace("")
            all_data['vectors'].update(namespace_data)
        
        all_data['extraction_summary']['total_vectors_extracted'] = len(all_data['vectors'])
        return all_data
    
    def _extract_from_namespace(self, namespace: str = "") -> Dict[str, Any]:
        """
        Extract vectors from a specific namespace using query.
        
        Args:
            namespace: Namespace to extract from
            
        Returns:
            Dictionary of vectors from the namespace
        """
        vectors = {}
        
        try:
            # Create a dummy vector for querying
            dummy_vector = [0.0] * self.query_dimension
            
            # Query the namespace
            results = self.index.query(
                vector=dummy_vector,
                top_k=10000,
                include_metadata=True,
                include_values=True,
                namespace=namespace
            )
            
            # Process results
            matches = getattr(results, 'matches', [])
            for match in matches:
                vectors[match['id']] = {
                    'id': match['id'],
                    'values': getattr(match, 'values', []),
                    'metadata': getattr(match, 'metadata', {}),
                    'score': getattr(match, 'score', 0)
                }
            
            logger.info(f"Extracted {len(vectors)} vectors from namespace '{namespace}'")
            
        except Exception as e:
            logger.error(f"Failed to extract from namespace '{namespace}': {e}")
        
        return vectors
    
    def save_to_json(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Save extracted data to JSON file.
        
        Args:
            data: Data to save
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pinecone_extraction_{self.index_name}_{timestamp}.json"
        
        filepath = os.path.join(os.getcwd(), filename)
        
        try:
            # Clean data to make it JSON serializable
            clean_data = clean_data_for_json(data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(clean_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data saved to JSON file: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save JSON file: {e}")
            raise
    
    def save_metadata_to_csv(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Save metadata to CSV file for easier analysis.
        
        Args:
            data: Extracted data
            filename: Optional custom filename
            
        Returns:
            Path to saved CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pinecone_metadata_{self.index_name}_{timestamp}.csv"
        
        filepath = os.path.join(os.getcwd(), filename)
        
        try:
            # Extract metadata from all vectors
            metadata_list = []
            
            for vector_id, vector_data in data.get('vectors', {}).items():
                # Handle Vector objects properly
                if hasattr(vector_data, 'metadata'):
                    metadata = getattr(vector_data, 'metadata', {}) or {}
                else:
                    metadata = vector_data.get('metadata', {}) if isinstance(vector_data, dict) else {}
                
                if metadata:
                    metadata = dict(metadata)  # Convert to dict if it's not already
                    metadata['vector_id'] = vector_id
                    
                    # Get score if available
                    if hasattr(vector_data, 'score'):
                        metadata['score'] = getattr(vector_data, 'score', 0)
                    else:
                        metadata['score'] = vector_data.get('score', 0) if isinstance(vector_data, dict) else 0
                    
                    metadata_list.append(metadata)
            
            # Create DataFrame and save to CSV
            if metadata_list:
                df = pd.DataFrame(metadata_list)
                df.to_csv(filepath, index=False, encoding='utf-8')
                logger.info(f"Metadata saved to CSV file: {filepath}")
                logger.info(f"CSV contains {len(df)} rows and {len(df.columns)} columns")
            else:
                logger.warning("No metadata found to save to CSV")
                return ""
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save CSV file: {e}")
            raise
    
    def analyze_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the extracted data and provide insights.
        
        Args:
            data: Extracted data
            
        Returns:
            Analysis results
        """
        logger.info("Analyzing extracted data...")
        
        vectors = data.get('vectors', {})
        analysis = {
            'total_vectors': len(vectors),
            'metadata_analysis': {},
            'fund_analysis': {},
            'column_analysis': {}
        }
        
        if not vectors:
            return analysis
        
        # Analyze metadata
        all_metadata_keys = set()
        fund_names = set()
        columns = set()
        
        for vector_data in vectors.values():
            # Handle Vector objects properly
            if hasattr(vector_data, 'metadata'):
                metadata = getattr(vector_data, 'metadata', {}) or {}
            else:
                metadata = vector_data.get('metadata', {}) if isinstance(vector_data, dict) else {}
            
            if metadata:
                all_metadata_keys.update(metadata.keys())
                
                if 'fund_name' in metadata:
                    fund_names.add(metadata['fund_name'])
                
                if 'column' in metadata:
                    columns.add(metadata['column'])
        
        analysis['metadata_analysis'] = {
            'unique_metadata_keys': list(all_metadata_keys),
            'total_metadata_keys': len(all_metadata_keys)
        }
        
        analysis['fund_analysis'] = {
            'unique_funds': list(fund_names),
            'total_funds': len(fund_names)
        }
        
        analysis['column_analysis'] = {
            'unique_columns': list(columns),
            'total_columns': len(columns)
        }
        
        logger.info(f"Analysis complete: {len(fund_names)} funds, {len(columns)} columns, {len(vectors)} total vectors")
        
        return analysis


def main(save_formats: List[str] = None):
    """
    Main execution function.
    
    Args:
        save_formats: List of formats to save ('json', 'csv', 'both')
    """
    if save_formats is None:
        save_formats = ['both']
    
    try:
        # Initialize extractor
        extractor = PineconeDataExtractor()
        
        # Extract all data
        logger.info("Starting data extraction process...")
        extracted_data = extractor.extract_all_data()
        
        # Analyze data
        analysis = extractor.analyze_extracted_data(extracted_data)
        logger.info(f"Extraction Summary:")
        logger.info(f"  Total Vectors: {analysis['total_vectors']}")
        logger.info(f"  Unique Funds: {analysis['fund_analysis']['total_funds']}")
        logger.info(f"  Unique Columns: {analysis['column_analysis']['total_columns']}")
        
        # Save data in requested formats
        saved_files = []
        
        if 'json' in save_formats or 'both' in save_formats:
            json_file = extractor.save_to_json(extracted_data)
            saved_files.append(json_file)
        
        if 'csv' in save_formats or 'both' in save_formats:
            csv_file = extractor.save_metadata_to_csv(extracted_data)
            if csv_file:
                saved_files.append(csv_file)
        
        logger.info("✅ Data extraction completed successfully!")
        logger.info(f"Files saved: {saved_files}")
        
        return extracted_data, analysis
        
    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments for save format
    save_formats = ['both']  # Default
    
    if len(sys.argv) > 1:
        format_arg = sys.argv[1].lower()
        if format_arg in ['json', 'csv', 'both']:
            save_formats = [format_arg]
        else:
            logger.warning(f"Unknown format '{format_arg}'. Using default 'both'")
    
    logger.info(f"🚀 Starting Pinecone data extraction (format: {save_formats})")
    
    main(save_formats=save_formats)