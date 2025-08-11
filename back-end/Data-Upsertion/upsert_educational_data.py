"""
Pinecone Educational Data Upsertion Script - Q&A Pairs Processing

This script reads mutual fund Q&A data from a JSON file and upserts it to Pinecone
using each Q&A pair as a separate vector with comprehensive metadata.

Author: Asset Management Chatbot System
Phase: Educational Data Processing
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import AzureOpenAI
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EducationalDataUpserter:
    """
    Handles the upsertion of educational Q&A data to Pinecone.
    """
    
    def __init__(self, json_path: str, index_name: Optional[str] = None):
        """
        Initialize the upserter with configuration from environment variables.
        
        Args:
            json_path: Path to the JSON file containing Q&A data
            index_name: Optional custom index name (defaults to EDUCATIONAL_DATA_INDEX_NAME)
        """
        # Load environment variables
        load_dotenv()
        
        self.json_path = json_path
        self.index_name = index_name or os.getenv('EDUCATIONAL_DATA_INDEX_NAME', 'hkp-amceducationdata')
        
        # Initialize clients
        self._initialize_openai_client()
        self._initialize_pinecone_client()
        
        # Configuration
        self.batch_size = 100  # Pinecone batch size limit
        self.embedding_dimension = 1536  # text-embedding-3-small dimension
        self.namespace = "educational_qa"  # Namespace for educational data
        
    def _initialize_openai_client(self) -> None:
        """Initialize Azure OpenAI client for embeddings."""
        try:
            # Extract base endpoint from the embedding endpoint URL
            embedding_endpoint = os.getenv('AZURE_OPENAI_EMBEDDING_ENDPOINT')
            base_endpoint = embedding_endpoint.split('/openai/')[0] if embedding_endpoint else None
            
            self.openai_client = AzureOpenAI(
                api_key=os.getenv('AZURE_OPENAI_EMBEDDING_API_KEY'),
                api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview'),
                azure_endpoint=base_endpoint or 'https://hkp-test.openai.azure.com/'
            )
            self.embedding_model = os.getenv('AZURE_OPENAI_EMBEDDINGS_MODEL', 'text-embedding-3-small')
            logger.info("Azure OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise
    
    def _initialize_pinecone_client(self) -> None:
        """Initialize Pinecone client and ensure index exists."""
        try:
            self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            
            # Check if index exists, create if not
            if self.index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
                    )
                )
                # Wait for index to be ready
                logger.info("Waiting for index to be ready...")
                time.sleep(30)
            
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client: {e}")
            raise
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text using Azure OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {text[:50]}... Error: {e}")
            raise
    
    def load_qa_data(self) -> List[Dict[str, Any]]:
        """
        Load Q&A data from JSON file.
        
        Returns:
            List of Q&A dictionaries
        """
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                qa_data = json.load(f)
            
            logger.info(f"Loaded {len(qa_data)} Q&A pairs from {self.json_path}")
            return qa_data
        except Exception as e:
            logger.error(f"Failed to load Q&A data from {self.json_path}: {e}")
            raise
    
    def _create_combined_text(self, qa_pair: Dict[str, Any]) -> str:
        """
        Create combined text for embedding from Q&A pair.
        
        Args:
            qa_pair: Dictionary containing question and answer
            
        Returns:
            Combined text for embedding
        """
        question = qa_pair.get('Question', '').strip()
        answer = qa_pair.get('Answer', '').strip()
        
        # Create a natural language combined text
        combined_text = f"Question: {question}\n\nAnswer: {answer}"
        return combined_text
    
    def _create_metadata(self, qa_pair: Dict[str, Any], vector_id: str) -> Dict[str, Any]:
        """
        Create comprehensive metadata for the Q&A pair.
        
        Args:
            qa_pair: Dictionary containing Q&A data
            vector_id: Unique vector ID
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'vector_id': vector_id,
            'question': qa_pair.get('Question', '').strip(),
            'answer': qa_pair.get('Answer', '').strip(),
            'chunk_number': qa_pair.get('ChunkNumber', 0),
            'source': qa_pair.get('Source', 'Unknown'),
            'data_type': 'educational_qa',
            'topic': 'mutual_funds',
            'upload_timestamp': datetime.now().isoformat(),
            'question_length': len(qa_pair.get('Question', '')),
            'answer_length': len(qa_pair.get('Answer', '')),
            'combined_length': len(self._create_combined_text(qa_pair)),
            'question_words': len(qa_pair.get('Question', '').split()),
            'answer_words': len(qa_pair.get('Answer', '').split())
        }
        
        # Add searchable keywords from question and answer
        combined_text = self._create_combined_text(qa_pair)
        keywords = self._extract_keywords(combined_text)
        metadata['keywords'] = keywords
        
        return metadata
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text for better searchability.
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            List of keywords
        """
        # Remove common words and extract meaningful terms
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 
            'these', 'those', 'they', 'them', 'their', 'what', 'when', 'where', 'why', 'how'
        }
        
        # Extract words, convert to lowercase, and filter
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        keywords = [word for word in words if len(word) > 3 and word not in common_words]
        
        # Get unique keywords and limit the count
        unique_keywords = list(dict.fromkeys(keywords))[:max_keywords]
        return unique_keywords
    
    def _generate_vector_id(self, index: int, qa_pair: Dict[str, Any]) -> str:
        """
        Generate a unique vector ID for the Q&A pair.
        
        Args:
            index: Index of the Q&A pair
            qa_pair: Q&A pair data
            
        Returns:
            Unique vector ID
        """
        chunk_number = qa_pair.get('ChunkNumber', 0)
        # Create a clean, unique ID
        vector_id = f"edu_qa_{chunk_number}_{index:04d}"
        return vector_id
    
    def test_data_processing(self, sample_size: int = 3) -> None:
        """
        Test data processing without uploading to Pinecone.
        
        Args:
            sample_size: Number of Q&A pairs to process for testing
        """
        logger.info("🧪 Testing educational data processing...")
        
        # Load data
        qa_data = self.load_qa_data()
        
        # Process a sample
        sample_data = qa_data[:sample_size]
        
        for idx, qa_pair in enumerate(sample_data):
            logger.info(f"\n📚 Testing Q&A pair {idx + 1}:")
            logger.info(f"Question: {qa_pair.get('Question', '')[:100]}...")
            logger.info(f"Answer: {qa_pair.get('Answer', '')[:100]}...")
            
            # Test combined text creation
            combined_text = self._create_combined_text(qa_pair)
            logger.info(f"Combined text length: {len(combined_text)} characters")
            
            # Test metadata creation
            vector_id = self._generate_vector_id(idx, qa_pair)
            metadata = self._create_metadata(qa_pair, vector_id)
            logger.info(f"Generated metadata keys: {list(metadata.keys())}")
            logger.info(f"Keywords: {metadata.get('keywords', [])}")
            
            # Test embedding generation (optional - comment out to save API calls)
            try:
                logger.info("Testing embedding generation...")
                embedding = self._generate_embedding(combined_text[:1000])  # Limit for testing
                logger.info(f"Embedding dimension: {len(embedding)}")
            except Exception as e:
                logger.warning(f"Embedding test failed: {e}")
    
    def upsert_data(self, start_index: int = 0, limit: Optional[int] = None) -> None:
        """
        Upsert Q&A data to Pinecone.
        
        Args:
            start_index: Index to start processing from
            limit: Optional limit on number of Q&A pairs to process
        """
        logger.info("🚀 Starting educational data upsertion to Pinecone...")
        
        # Load data
        qa_data = self.load_qa_data()
        
        # Apply limits
        if limit:
            qa_data = qa_data[start_index:start_index + limit]
        else:
            qa_data = qa_data[start_index:]
        
        logger.info(f"Processing {len(qa_data)} Q&A pairs starting from index {start_index}")
        
        vectors_to_upsert = []
        
        for idx, qa_pair in enumerate(qa_data):
            try:
                # Generate vector ID
                vector_id = self._generate_vector_id(start_index + idx, qa_pair)
                
                # Create combined text for embedding
                combined_text = self._create_combined_text(qa_pair)
                
                # Generate embedding
                embedding = self._generate_embedding(combined_text)
                
                # Create metadata  [[memory:4260140]]
                metadata = self._create_metadata(qa_pair, vector_id)
                
                # Create vector
                vector = {
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata
                }
                
                vectors_to_upsert.append(vector)
                
                # Log progress
                if (idx + 1) % 10 == 0:
                    logger.info(f"Prepared {idx + 1}/{len(qa_data)} vectors for upsertion")
                
                # Upsert in batches
                if len(vectors_to_upsert) >= self.batch_size:
                    self._upsert_batch(vectors_to_upsert)
                    vectors_to_upsert = []
                    time.sleep(1)  # Rate limiting
                    
            except Exception as e:
                logger.error(f"Failed to process Q&A pair {idx}: {e}")
                continue
        
        # Upsert remaining vectors
        if vectors_to_upsert:
            self._upsert_batch(vectors_to_upsert)
        
        logger.info("✅ Educational data upsertion completed!")
    
    def _upsert_batch(self, vectors: List[Dict[str, Any]]) -> None:
        """
        Upsert a batch of vectors to Pinecone.
        
        Args:
            vectors: List of vectors to upsert
        """
        try:
            response = self.index.upsert(
                vectors=vectors,
                namespace=self.namespace
            )
            logger.info(f"Upserted batch of {len(vectors)} vectors. Response: {response}")
        except Exception as e:
            logger.error(f"Failed to upsert batch: {e}")
            raise
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Pinecone index.
        
        Returns:
            Index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            logger.info(f"Index stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}

def main():
    """Main function to run the educational data upsertion."""
    
    # Path to the Q&A dataset
    json_path = os.path.join("Educational Data Processing", "processed_data", "mutual_funds_qa_dataset.json")
    
    # Check if file exists
    if not os.path.exists(json_path):
        # Try alternative path
        json_path = "mutual_funds_qa_dataset.json"
        if not os.path.exists(json_path):
            logger.error(f"Q&A dataset file not found. Please check the path.")
            return
    
    try:
        # Initialize upserter
        upserter = EducationalDataUpserter(json_path)
        
        # Test processing first
        logger.info("Running test processing...")
        upserter.test_data_processing(sample_size=3)
        
        # Get user confirmation
        user_input = input("\nDo you want to proceed with full upsertion? (y/n): ").strip().lower()
        if user_input == 'y':
            # Full upsertion
            upserter.upsert_data()
            
            # Get final stats
            upserter.get_index_stats()
        else:
            logger.info("Upsertion cancelled by user.")
            
    except Exception as e:
        logger.error(f"Script execution failed: {e}")

if __name__ == "__main__":
    main()