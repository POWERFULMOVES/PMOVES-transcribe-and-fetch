import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get the app directory path
APP_DIR = Path(__file__).parent.absolute()
ENV_PATH = APP_DIR / '.env'

# Load environment variables from the specific .env file location
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    print(f"Loaded environment variables from {ENV_PATH}")
else:
    print(f"Warning: .env file not found at {ENV_PATH}")
    # Fallback to default load_dotenv behavior
load_dotenv()

def test_openai_embedding():
    """Test that embedding generation works with OpenAI client."""
    try:
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY environment variable is not set")
            return False
            
        openai_client = OpenAI(api_key=api_key)
        
        # Test direct embedding generation with OpenAI client
        print("Testing direct embedding generation with OpenAI client...")
        test_query = "test query for embedding generation"
        
        embedding = openai_client.embeddings.create(
            input=test_query,
            model="text-embedding-3-small",
            dimensions=1536
        ).data[0].embedding
        
        # Check if embedding was generated successfully
        if embedding and len(embedding) == 1536:
            print(f"✅ Successfully generated embedding with OpenAI client. Embedding length: {len(embedding)}")
            return True
        else:
            print(f"❌ Failed to generate proper embedding. Length: {len(embedding) if embedding else 'None'}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing OpenAI embedding generation...")
    success = test_openai_embedding()
    
    if success:
        print("\n✅ Test passed! The OpenAI client can generate embeddings correctly.")
        print("The fix in compsearchfix.py should work as it uses the same approach.")
        sys.exit(0)
    else:
        print("\n❌ Test failed. The OpenAI client cannot generate embeddings correctly.")
        print("Check your API key and OpenAI configuration.")
        sys.exit(1)
