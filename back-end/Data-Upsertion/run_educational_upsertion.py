"""
Simple runner script for educational Q&A data upsertion to Pinecone.

This script provides an easy way to run the educational data upsertion
with different options and configurations.

Usage:
    python run_educational_upsertion.py [options]
"""

import os
import sys
import argparse
from upsert_educational_data import EducationalDataUpserter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function with command line argument parsing."""
    
    parser = argparse.ArgumentParser(description='Upsert educational Q&A data to Pinecone')
    parser.add_argument('--test-only', action='store_true', 
                       help='Run test processing only without upserting')
    parser.add_argument('--sample-size', type=int, default=3,
                       help='Number of samples to test (default: 3)')
    parser.add_argument('--start-index', type=int, default=0,
                       help='Index to start processing from (default: 0)')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of Q&A pairs to process')
    parser.add_argument('--json-path', type=str, default='mutual_funds_qa_dataset.json',
                       help='Path to the Q&A JSON file')
    parser.add_argument('--auto-confirm', action='store_true',
                       help='Skip user confirmation and proceed with upsertion')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.json_path):
        logger.error(f"Q&A dataset file not found: {args.json_path}")
        logger.info("Available files in current directory:")
        for file in os.listdir('.'):
            if file.endswith('.json'):
                logger.info(f"  - {file}")
        return 1
    
    try:
        # Initialize upserter
        logger.info(f"🚀 Initializing Educational Data Upserter...")
        logger.info(f"📄 Using JSON file: {args.json_path}")
        
        upserter = EducationalDataUpserter(args.json_path)
        
        # Test processing
        logger.info(f"🧪 Running test processing with {args.sample_size} samples...")
        upserter.test_data_processing(sample_size=args.sample_size)
        
        if args.test_only:
            logger.info("✅ Test completed. Exiting (--test-only flag used).")
            return 0
        
        # Get confirmation
        proceed = args.auto_confirm
        if not proceed:
            user_input = input(f"\n🤔 Do you want to proceed with upserting to Pinecone? (y/n): ").strip().lower()
            proceed = user_input == 'y'
        
        if proceed:
            logger.info("🚀 Starting full upsertion...")
            upserter.upsert_data(start_index=args.start_index, limit=args.limit)
            
            # Get final stats
            logger.info("📊 Getting final index statistics...")
            stats = upserter.get_index_stats()
            
            logger.info("✅ Educational data upsertion completed successfully!")
            return 0
        else:
            logger.info("❌ Upsertion cancelled by user.")
            return 0
            
    except Exception as e:
        logger.error(f"💥 Script execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)