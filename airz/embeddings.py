from functools import lru_cache
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

@lru_cache
def get_embedding_model():
    """Get a cached instance of the Google Generative AI embedding model.
    
    Returns:
        GoogleGenerativeAIEmbeddings: An instance of the embedding model.
        
    Raises:
        ValueError: If GOOGLE_API_KEY is not set in environment variables.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found in environment variables. "
            "Please set it in your .env file."
        )
    
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key,
    )
