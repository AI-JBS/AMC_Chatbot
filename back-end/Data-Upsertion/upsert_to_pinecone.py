"""
Pinecone Data Upsertion Script - Column-wise Fund Data Processing

This script reads mutual fund data from a CSV file and upserts it to Pinecone
using column-wise chunking strategy. Each column value becomes a separate
vector in Pinecone with comprehensive metadata.

Author: Asset Management Chatbot System
Phase: 1 - Data Preparation
"""

import os
import pandas as pd
import re
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import AzureOpenAI
import time
from slugify import slugify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FundDataUpserter:
    """
    Handles the upsertion of mutual fund data to Pinecone with column-wise processing.
    """
    
    def __init__(self, csv_path: str, index_name: Optional[str] = None):
        """
        Initialize the upserter with configuration from environment variables.
        
        Args:
            csv_path: Path to the CSV file containing fund data
            index_name: Optional custom index name (defaults to env variable)
        """
        # Load environment variables
        load_dotenv()
        
        self.csv_path = csv_path
        self.index_name = index_name or os.getenv('PINECONE_INDEX_NAME', 'hkp-amcdata')
        
        # Initialize clients
        self._initialize_openai_client()
        self._initialize_pinecone_client()
        
        # Configuration
        self.batch_size = 100  # Pinecone batch size limit
        self.embedding_dimension = 1536  # text-embedding-3-small dimension
        
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
                time.sleep(10)
            
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client: {e}")
            raise
    
    def _clean_value(self, value: Any) -> str:
        """
        Clean and normalize column values.
        
        Args:
            value: Raw value from CSV
            
        Returns:
            Cleaned string value
        """
        if pd.isna(value) or value == '' or value is None:
            return None
        
        # Convert to string and clean
        str_value = str(value).strip()
        
        # Handle dash as missing value (common in financial data)
        if str_value == '-':
            return None
        
        # Remove commas from numbers (like "8,950,000,000")
        if re.match(r'^[\d,]+$', str_value):
            str_value = str_value.replace(',', '')
        
        # Clean percentage signs but keep the value
        if str_value.endswith('%'):
            str_value = str_value[:-1].strip()
            
        return str_value
    
    def _to_snake_case(self, text: str) -> str:
        """
        Convert text to snake_case format.
        
        Args:
            text: Input text
            
        Returns:
            Snake_case formatted text
        """
        # Replace spaces and special characters with underscores
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', '_', text)
        return text.lower()
    
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
    
    def test_data_processing(self, sample_size: int = 2) -> None:
        """
        Test data processing without uploading to Pinecone.
        
        Args:
            sample_size: Number of fund rows to process for testing
        """
        logger.info("🧪 Testing data processing...")
        
        # Load data
        df = self.load_and_process_data()
        
        # Process a sample
        sample_df = df.head(sample_size)
        
        for idx, fund_row in sample_df.iterrows():
            fund_name = fund_row['Fund Name']
            logger.info(f"\n📊 Testing fund: {fund_name}")
            
            # Show original data sample
            logger.info("Original data sample:")
            for col in ['Fund Name', 'Risk Profile', 'Pricing Mechanism', 'Total Expense Ratio', 'Net Asset Value']:
                if col in fund_row:
                    logger.info(f"  {col}: {fund_row[col]}")
            
            # Test data cleaning
            logger.info("\nCleaned values:")
            for col in fund_row.index[:5]:  # Test first 5 columns
                raw_value = fund_row[col]
                cleaned_value = self._clean_value(raw_value)
                logger.info(f"  {col}: '{raw_value}' → '{cleaned_value}'")
            
            # Test metadata creation for one column
            test_column = 'Risk Profile'
            if test_column in fund_row:
                cleaned_value = self._clean_value(fund_row[test_column])
                if cleaned_value:
                    metadata = self._create_metadata(fund_row, test_column, cleaned_value)
                    logger.info(f"\nSample metadata for '{test_column}':")
                    for key, value in list(metadata.items())[:8]:  # Show first 8 metadata fields
                        logger.info(f"  {key}: {value}")
                    
                    # Test chunk ID generation
                    chunk_id = self._create_chunk_id(fund_name, test_column)
                    logger.info(f"\nChunk ID: {chunk_id}")
        
        logger.info("\n✅ Data processing test completed!")
        
        # Summary stats
        total_columns = len(df.columns)
        total_funds = len(df)
        estimated_chunks = total_funds * total_columns
        logger.info(f"\n📈 Summary:")
        logger.info(f"  Total funds: {total_funds}")
        logger.info(f"  Total columns per fund: {total_columns}")
        logger.info(f"  Estimated total chunks: {estimated_chunks}")
        logger.info(f"  Column names: {list(df.columns)}")
    
    def _create_metadata(self, fund_row: pd.Series, column_name: str, column_value: str) -> Dict[str, Any]:
        """
        Create comprehensive metadata for a chunk.
        
        Args:
            fund_row: Complete fund data row
            column_name: Name of the current column
            column_value: Raw value of the current column
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'fund_name': fund_row['Fund Name'],
            'column': column_name,
            'value': column_value
        }
        
        # Add all other fund attributes in snake_case
        for col in fund_row.index:
            if col != column_name:  # Don't duplicate the current column
                snake_key = self._to_snake_case(col)
                cleaned_value = self._clean_value(fund_row[col])
                if cleaned_value is not None:
                    metadata[snake_key] = cleaned_value
        
        return metadata
    
    def _create_chunk_id(self, fund_name: str, column_name: str) -> str:
        """
        Create unique chunk ID in the specified format.
        
        Args:
            fund_name: Name of the fund
            column_name: Name of the column
            
        Returns:
            Formatted chunk ID
        """
        fund_slug = slugify(fund_name)
        column_slug = slugify(column_name)
        return f"{fund_slug}_{column_slug}"
    
    def _process_fund_row(self, fund_row: pd.Series) -> List[Dict[str, Any]]:
        """
        Process a single fund row into multiple chunks (one per column).
        
        Args:
            fund_row: Single row of fund data
            
        Returns:
            List of chunks ready for upsertion
        """
        chunks = []
        fund_name = fund_row['Fund Name']
        
        for column_name in fund_row.index:
            raw_value = fund_row[column_name]
            cleaned_value = self._clean_value(raw_value)
            
            # Skip empty or null values
            if cleaned_value is None:
                logger.debug(f"Skipping empty value for {fund_name} - {column_name}")
                continue
            
            # Generate embedding
            try:
                embedding = self._generate_embedding(cleaned_value)
            except Exception as e:
                logger.warning(f"Failed to generate embedding for {fund_name} - {column_name}: {e}")
                continue
            
            # Create metadata
            metadata = self._create_metadata(fund_row, column_name, cleaned_value)
            
            # Create chunk
            chunk = {
                'id': self._create_chunk_id(fund_name, column_name),
                'values': embedding,
                'metadata': metadata
            }
            
            chunks.append(chunk)
            logger.debug(f"Created chunk for {fund_name} - {column_name}")
        
        return chunks
    
    def _upsert_batch(self, vectors: List[Dict[str, Any]]) -> None:
        """
        Upsert a batch of vectors to Pinecone.
        
        Args:
            vectors: List of vector dictionaries
        """
        try:
            self.index.upsert(vectors=vectors)
            logger.info(f"Successfully upserted batch of {len(vectors)} vectors")
        except Exception as e:
            logger.error(f"Failed to upsert batch: {e}")
            raise
    
    def load_and_process_data(self) -> pd.DataFrame:
        """
        Load and validate the CSV data.
        
        Returns:
            Loaded DataFrame
        """
        try:
            df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(df)} fund records from {self.csv_path}")
            logger.info(f"Columns: {list(df.columns)}")
            return df
        except Exception as e:
            logger.error(f"Failed to load CSV file: {e}")
            raise
    
    def upsert_all_data(self) -> None:
        """
        Main method to process and upsert all fund data to Pinecone.
        """
        logger.info("Starting fund data upsertion process...")
        
        # Load data
        df = self.load_and_process_data()
        
        # Process all funds
        all_chunks = []
        total_chunks_created = 0
        
        for idx, fund_row in df.iterrows():
            fund_name = fund_row['Fund Name']
            logger.info(f"Processing fund {idx + 1}/{len(df)}: {fund_name}")
            
            # Process this fund's data
            fund_chunks = self._process_fund_row(fund_row)
            all_chunks.extend(fund_chunks)
            total_chunks_created += len(fund_chunks)
            
            # Upsert in batches
            if len(all_chunks) >= self.batch_size:
                self._upsert_batch(all_chunks[:self.batch_size])
                all_chunks = all_chunks[self.batch_size:]
                time.sleep(0.1)  # Rate limiting
        
        # Upsert remaining chunks
        if all_chunks:
            self._upsert_batch(all_chunks)
        
        logger.info(f"Upsertion complete! Total chunks created: {total_chunks_created}")
        
        # Get index stats
        stats = self.index.describe_index_stats()
        logger.info(f"Pinecone index stats: {stats}")


def main(test_mode: bool = False):
    """
    Main execution function.
    
    Args:
        test_mode: If True, only test data processing without uploading to Pinecone
    """
    # Configuration
    csv_path = r"..\..\Data\jbs_funds_data.csv"
    
    try:
        # Initialize upserter
        upserter = FundDataUpserter(csv_path=csv_path)
        
        if test_mode:
            # Test data processing only
            upserter.test_data_processing(sample_size=3)
        else:
            # Start upsertion process
            upserter.upsert_all_data()
            logger.info("✅ Fund data upsertion completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    # Check if test mode is requested
    test_mode = len(sys.argv) > 1 and sys.argv[1] == "--test"
    
    if test_mode:
        logger.info("🧪 Running in TEST MODE - no data will be uploaded to Pinecone")
    else:
        logger.info("🚀 Running in PRODUCTION MODE - data will be uploaded to Pinecone")
    
    main(test_mode=test_mode)