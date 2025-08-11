"""Utility & helper functions."""

from __future__ import annotations

import os
import typing
from functools import lru_cache

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_openai import AzureChatOpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from openai import AzureOpenAI

# Load environment variables
load_dotenv()


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


@lru_cache(maxsize=12)
def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    
    if provider == "azure_openai":
        # Use Azure OpenAI with custom configuration
        return AzureChatOpenAI(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', model),
            temperature=float(os.getenv('AZURE_OPENAI_TEMPERATURE', '0.1'))
        )
    else:
        return init_chat_model(model, model_provider=provider)


class State:
    """An object that can be used to store arbitrary state."""

    _state: dict[str, typing.Any]

    def __init__(self, state: dict[str, typing.Any] | None = None):
        if state is None:
            state = {}
        super().__setattr__("_state", state)

    def __setattr__(self, key: typing.Any, value: typing.Any) -> None:
        self._state[key] = value

    def __getattr__(self, key: typing.Any) -> typing.Any:
        try:
            return self._state[key]
        except KeyError:
            message = "'{}' object has no attribute '{}'"
            raise AttributeError(message.format(self.__class__.__name__, key))

    def __delattr__(self, key: typing.Any) -> None:
        del self._state[key]


# Pinecone utilities
class PineconeClient:
    """Singleton client for Pinecone operations."""
    
    _instance = None
    _client = None
    _index = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._client = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            index_name = os.getenv('PINECONE_INDEX_NAME', 'hkp-amcdata')
            self._index = self._client.Index(index_name)
    
    @property
    def index(self):
        return self._index


class EducationalPineconeClient:
    """Singleton client for Educational Pinecone operations."""
    
    _instance = None
    _client = None
    _index = None
    _openai_client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._client = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            index_name = os.getenv('EDUCATIONAL_DATA_INDEX_NAME', 'hkp-amceducationdata')
            self._index = self._client.Index(index_name)
            
            # Initialize Azure OpenAI client for embeddings
            embedding_endpoint = os.getenv('AZURE_OPENAI_EMBEDDING_ENDPOINT')
            base_endpoint = embedding_endpoint.split('/openai/')[0] if embedding_endpoint else None
            
            self._openai_client = AzureOpenAI(
                api_key=os.getenv('AZURE_OPENAI_EMBEDDING_API_KEY'),
                api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview'),
                azure_endpoint=base_endpoint or 'https://hkp-test.openai.azure.com/'
            )
    
    @property
    def index(self):
        return self._index
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for the given text."""
        try:
            response = self._openai_client.embeddings.create(
                input=text,
                model=os.getenv('AZURE_OPENAI_EMBEDDINGS_MODEL', 'text-embedding-3-small')
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 1536  # Return dummy vector on error


def query_funds_by_risk_profile(risk_profile: str) -> List[Dict[str, Any]]:
    """Query funds by risk profile from Pinecone.
    
    Args:
        risk_profile: Risk profile (Low, Medium, High)
        
    Returns:
        List of fund data matching the risk profile
    """
    pc_client = PineconeClient()
    
    try:
        # Query with a dummy vector to find all funds with matching risk profile
        dummy_vector = [0.0] * 1536  # text-embedding-3-small dimension
        
        results = pc_client.index.query(
            vector=dummy_vector,
            filter={"risk_profile": {"$eq": risk_profile.title()}},
            top_k=100,
            include_metadata=True
        )
        
        funds_data = []
        fund_names_seen = set()
        
        for match in getattr(results, 'matches', []):
            metadata = getattr(match, 'metadata', {})
            fund_name = metadata.get('fund_name')
            
            if fund_name and fund_name not in fund_names_seen:
                fund_names_seen.add(fund_name)
                funds_data.append({
                    'name': fund_name,
                    'risk_profile': metadata.get('risk_profile'),
                    'nav': metadata.get('net_asset_value'),
                    'return_365d': metadata.get('365d'),
                    'return_ytd': metadata.get('return_ytd'),
                    'expense_ratio': metadata.get('total_expense_ratio'),
                    'management_fee': metadata.get('management_fee'),
                    'pricing_mechanism': metadata.get('pricing_mechanism')
                })
        
        return funds_data
        
    except Exception as e:
        print(f"Error querying Pinecone: {e}")
        return []


def query_fund_comparison_data(fund_names: List[str], metric: str) -> List[Dict[str, Any]]:
    """Query specific metric data for fund comparison.
    
    Args:
        fund_names: List of fund names to compare
        metric: The metric column to compare (e.g., '365d', 'total_expense_ratio')
        
    Returns:
        List of fund data with the specified metric
    """
    pc_client = PineconeClient()
    
    try:
        # Convert metric to snake_case for querying
        metric_snake = metric.lower().replace(' ', '_').replace('%', '').replace('(', '').replace(')', '')
        
        comparison_data = []
        
        for fund_name in fund_names:
            # Query for the specific fund and metric
            dummy_vector = [0.0] * 1536
            
            results = pc_client.index.query(
                vector=dummy_vector,
                filter={
                    "fund_name": {"$eq": fund_name},
                    "column": {"$eq": metric}
                },
                top_k=1,
                include_metadata=True
            )
            
            matches = getattr(results, 'matches', [])
            if matches:
                metadata = getattr(matches[0], 'metadata', {})
                value = metadata.get('value')
                
                if value and value != '-':
                    try:
                        # Try to convert to float for numeric comparison
                        numeric_value = float(str(value).replace(',', '').replace('%', ''))
                        comparison_data.append({
                            'Fund Name': fund_name,
                            metric: numeric_value
                        })
                    except ValueError:
                        comparison_data.append({
                            'Fund Name': fund_name,
                            metric: value
                        })
        
        return comparison_data
        
    except Exception as e:
        print(f"Error querying fund comparison data: {e}")
        return []


def get_all_fund_names() -> List[str]:
    """Get all available fund names from Pinecone.
    
    Returns:
        List of unique fund names
    """
    pc_client = PineconeClient()
    
    try:
        dummy_vector = [0.0] * 1536
        
        results = pc_client.index.query(
            vector=dummy_vector,
            filter={"column": {"$eq": "Fund Name"}},
            top_k=100,
            include_metadata=True
        )
        
        fund_names = []
        matches = getattr(results, 'matches', [])
        
        for match in matches:
            metadata = getattr(match, 'metadata', {})
            fund_name = metadata.get('value')
            if fund_name and fund_name not in fund_names:
                fund_names.append(fund_name)
        
        return sorted(fund_names)
        
    except Exception as e:
        print(f"Error getting fund names: {e}")
        return []


def query_educational_content(term: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Query educational content from Pinecone based on user's term/question.
    
    Args:
        term: Financial term or question to explain
        top_k: Number of top results to return
        
    Returns:
        List of relevant Q&A pairs from educational index
    """
    edu_client = EducationalPineconeClient()
    
    try:
        # Generate embedding for the user's term/question
        query_embedding = edu_client.generate_embedding(term)
        
        # Query the educational index
        results = edu_client.index.query(
            vector=query_embedding,
            namespace="educational_qa",  # Use the correct namespace
            top_k=top_k,
            include_metadata=True
        )
        
        educational_content = []
        matches = getattr(results, 'matches', [])
        
        for match in matches:
            metadata = getattr(match, 'metadata', {})
            score = getattr(match, 'score', 0)
            
            # Only include results with reasonable similarity scores
            if score > 0.6:  # Threshold for relevance (lowered for better coverage)
                educational_content.append({
                    'question': metadata.get('question', ''),
                    'answer': metadata.get('answer', ''),
                    'score': round(score, 3),
                    'source': metadata.get('source', 'Educational Content'),
                    'chunk_number': metadata.get('chunk_number', 0)
                })
        
        return educational_content
        
    except Exception as e:
        print(f"Error querying educational content: {e}")
        return []
