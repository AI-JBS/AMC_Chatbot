# Educational Data Upsertion to Pinecone

This folder contains scripts for upserting educational Q&A data from the mutual funds dataset to Pinecone vector database.

## Files

- `upsert_educational_data.py` - Main upsertion class and logic
- `run_educational_upsertion.py` - Simple runner script with CLI options
- `mutual_funds_qa_dataset.json` - The Q&A dataset (1502 question-answer pairs)
- `requirements_educational.txt` - Python dependencies
- `README_Educational.md` - This file

## Setup

1. **Activate Virtual Environment:**
   ```bash
   .venv\Scripts\Activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements_educational.txt
   ```

3. **Environment Variables:**
   Ensure your `.env` file contains:
   ```
   EDUCATIONAL_DATA_INDEX_NAME=hkp-amceducationdata
   AZURE_OPENAI_EMBEDDING_API_KEY=your_key
   AZURE_OPENAI_EMBEDDING_ENDPOINT=your_endpoint
   AZURE_OPENAI_EMBEDDINGS_MODEL=text-embedding-3-small
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_ENVIRONMENT=us-east-1
   ```

## Usage

### 1. Test Only (Recommended First Run)
```bash
cd Data-Upsertion
python run_educational_upsertion.py --test-only --sample-size 5
```

### 2. Full Upsertion with Confirmation
```bash
python run_educational_upsertion.py
```

### 3. Auto-Confirm Upsertion (No Prompt)
```bash
python run_educational_upsertion.py --auto-confirm
```

### 4. Partial Upsertion (First 100 Q&A pairs)
```bash
python run_educational_upsertion.py --limit 100
```

### 5. Resume from Specific Index
```bash
python run_educational_upsertion.py --start-index 500 --limit 200
```

## Data Structure

Each Q&A pair is embedded as a single vector with the following structure:

### Combined Text (for embedding):
```
Question: What is passive income?

Answer: Passive income is regular income that requires little or no maintenance...
```

### Metadata (stored with each vector):
```json
{
  "vector_id": "edu_qa_0001_0000",
  "question": "What is passive income?",
  "answer": "Passive income is regular income...",
  "chunk_number": 1,
  "source": "Mutual Funds Educational Info.pdf",
  "data_type": "educational_qa",
  "topic": "mutual_funds",
  "upload_timestamp": "2025-01-17T10:30:00",
  "question_length": 25,
  "answer_length": 150,
  "combined_length": 175,
  "question_words": 4,
  "answer_words": 25,
  "keywords": ["passive", "income", "regular", "maintenance"]
}
```

## Features

- ✅ **Azure OpenAI Integration**: Uses Azure OpenAI embeddings (text-embedding-3-small)
- ✅ **Comprehensive Metadata**: Question, answer, and analytics stored as metadata
- ✅ **Batch Processing**: Efficient batch upsertion (100 vectors per batch)
- ✅ **Error Handling**: Robust error handling and logging
- ✅ **Resume Capability**: Start from any index, process any number of records
- ✅ **Test Mode**: Test processing without uploading
- ✅ **Progress Tracking**: Detailed logging and progress updates
- ✅ **Keyword Extraction**: Automatic keyword extraction for better searchability

## Index Configuration

- **Index Name**: From `EDUCATIONAL_DATA_INDEX_NAME` environment variable
- **Namespace**: `educational_qa`
- **Dimension**: 1536 (text-embedding-3-small)
- **Metric**: Cosine similarity
- **Cloud**: AWS (us-east-1)

## Troubleshooting

1. **Index Not Found**: The script will automatically create the index if it doesn't exist
2. **API Rate Limits**: Built-in rate limiting with 1-second delays between batches
3. **Memory Issues**: Process in smaller batches using `--limit` parameter
4. **Network Issues**: The script will retry failed operations

## Monitoring

Check index statistics after upsertion:
```python
from upsert_educational_data import EducationalDataUpserter
upserter = EducationalDataUpserter('mutual_funds_qa_dataset.json')
stats = upserter.get_index_stats()
print(stats)
```

## Next Steps

After successful upsertion, you can:
1. Query the vectors using the Pinecone index
2. Integrate with your chatbot for Q&A retrieval
3. Use the metadata for filtering and analytics
4. Monitor performance and optimize as needed