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

if __name__ == "__main__":
    print("Embedding Model Demonstration")
    
    # 1. Get the embedding model
    print("\n1. Loading embedding model")
    model = get_embedding_model()
    print("Model loaded successfully")
    
    # 2. Create embeddings for single texts
    print("\n2. Creating embeddings for single texts")
    texts = [
        "This is a sample text about artificial intelligence.",
        "This text is about machine learning and neural networks.",
        "This one is completely different, talking about cooking recipes."
    ]
    
    for i, text in enumerate(texts, 1):
        embedding = model.embed_query(text)
        print(f"\nText {i}: {text}")
        print(f"Embedding shape: {len(embedding)} dimensions")
        print(f"First 5 values: {embedding[:5]}")
    
