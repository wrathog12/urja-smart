from configs.config import QdrantSettings
from qdrant_client import QdrantClient


def initialize_qdrant_client() -> QdrantClient:
    """
    Initialize and verify the Qdrant client connection.
    Supports both local Qdrant (without API key) and Qdrant Cloud (with API key).

    Returns:
        QdrantClient: Configured Qdrant client instance with timeout settings

    Raises:
        Exception: If connection to Qdrant server fails
    """
    qdrant_settings = QdrantSettings()

    # Support both local and cloud Qdrant
    if qdrant_settings.QDRANT_API_KEY:
        # Qdrant Cloud with API key
        client = QdrantClient(
            url=qdrant_settings.QDRANT_HOST_URL,
            api_key=qdrant_settings.QDRANT_API_KEY,
            timeout=300
        )
    else:
        # Local Qdrant without API key
        client = QdrantClient(qdrant_settings.QDRANT_HOST_URL, timeout=300)
    
    try:
        print('Sending heartbeat to Qdrant Client...')
        client.get_collections()
        print('Qdrant Client is up and running!')
        return client
    except Exception as e:
        print(f'''
      
##################################

               __
              /._)
     _.----._/ /
    /         /
 __/ (  | (  |
/__.-'|_|--|_|

      
Could not connect to Qdrant Client. Make sure that the corresponding container is up and running. (Error: {e})
      
      
##################################''')
        raise

# Initialize the global client instance
qdrant_settings = QdrantSettings()
current_qdrant_client = initialize_qdrant_client()