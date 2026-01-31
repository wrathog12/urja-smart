import os
from typing import List
from pydantic_settings import BaseSettings

from services.credential_manager import get_secret

ENVIRONMENT = (os.getenv('ENVIRONMENT') or 'LOCAL').upper()

secret_keys_list = get_secret(ENVIRONMENT)

class AppInfo(BaseSettings):
    PROJECT_NAME: str = "Document Handling API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for vectorisation of given documents and chatting with them"
    API_STR: str = "/api"
    ALLOWED_ORIGINS: List[str] = ["*", "http://localhost:3000"]

class QdrantSettings(BaseSettings):
    QDRANT_HOST_URL:str=secret_keys_list['QDRANT_HOST_URL']
    QDRANT_API_KEY:str=secret_keys_list.get('QDRANT_API_KEY', '')
    QDRANT_COLLECTION_NAME:str='BANKING_RAG_DOCUMENTS'

class OllamaSettings(BaseSettings):
    OLLAMA_ENDPOINT_URL:str=secret_keys_list['OLLAMA_ENDPOINT_URL']

class DocumentDB(BaseSettings):
    DOCUMENT_DB_CONNECTION_STRING:str=secret_keys_list['DOCUMENT_DB_CONNECTION_STRING']
    DATABASE_NAME:str='banking_rag'
    COLLECTION_NAME:str='documents'

class AzureOpenAISettings(BaseSettings):
    # Embeddings endpoint
    AZURE_OPENAI_ENDPOINT:str=secret_keys_list['AZURE_OPENAI_ENDPOINT']
    AZURE_OPENAI_API_KEY:str=secret_keys_list['AZURE_OPENAI_API_KEY']
    AZURE_OPENAI_API_VERSION:str=secret_keys_list.get('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT:str="text-embedding-3-large"

    # Chat endpoint (can be different from embeddings)
    AZURE_OPENAI_CHAT_ENDPOINT:str=secret_keys_list.get('AZURE_OPENAI_CHAT_ENDPOINT', secret_keys_list['AZURE_OPENAI_ENDPOINT'])
    AZURE_OPENAI_CHAT_API_KEY:str=secret_keys_list.get('AZURE_OPENAI_CHAT_API_KEY', secret_keys_list['AZURE_OPENAI_API_KEY'])
    AZURE_OPENAI_CHAT_API_VERSION:str=secret_keys_list.get('AZURE_OPENAI_CHAT_API_VERSION', '2024-12-01-preview')
    AZURE_OPENAI_CHAT_DEPLOYMENT:str=secret_keys_list.get('AZURE_OPENAI_CHAT_DEPLOYMENT', 'gpt-4o-2')

    EMBEDDING_DIMENSION:int=3072

class AzureStorageSettings(BaseSettings):
    AZURE_STORAGE_CONNECTION_STRING:str=secret_keys_list['AZURE_STORAGE_CONNECTION_STRING']
    AZURE_STORAGE_CONTAINER_NAME:str=secret_keys_list.get('AZURE_CONTAINER_NAME', 'banking-documents')

class DocumentSettings(BaseSettings):
    MAX_FILE_SIZE:int=10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS:List[str]=[".pdf", ".jpg", ".jpeg", ".png"]
    IMAGE_EXTENSIONS:List[str]=[".jpg", ".jpeg", ".png"]
    OCR_LANGUAGES:str="eng+hin+ben+tam+tel"
    CHUNK_SIZE:int=512
    CHUNK_OVERLAP:int=150

class EnhancedOCRSettings(BaseSettings):
    """Enhanced OCR Service Configuration Settings"""

    # OCR Processing Settings
    OCR_CONFIDENCE_THRESHOLD: float = secret_keys_list.get('OCR_CONFIDENCE_THRESHOLD', 50.0)
    OCR_MAX_PROCESSING_TIME: int = secret_keys_list.get('OCR_MAX_PROCESSING_TIME', 300)  # seconds
    OCR_ENABLE_PREPROCESSING: bool = secret_keys_list.get('OCR_ENABLE_PREPROCESSING', 'true').lower() == 'true'

    # Image Processing Settings
    OCR_MIN_IMAGE_SIZE: int = 50  # minimum width/height in pixels
    OCR_MAX_IMAGE_SIZE: int = 4000  # maximum dimension before downscaling
    OCR_UPSCALE_THRESHOLD: int = 800  # minimum dimension to trigger upscaling
    OCR_ENABLE_NOISE_REDUCTION: bool = True
    OCR_ENABLE_SHARPENING: bool = True
    OCR_ENABLE_CONTRAST_ENHANCEMENT: bool = True

    # Multi-method OCR Settings
    OCR_USE_MULTIPLE_METHODS: bool = True
    OCR_STANDARD_METHOD_WEIGHT: float = 1.0
    OCR_DOCUMENT_METHOD_WEIGHT: float = 1.2  # Prefer document-optimized OCR
    OCR_SINGLE_COLUMN_WEIGHT: float = 1.1

    # PDF Processing Settings
    PDF_ENABLE_METADATA_EXTRACTION: bool = True
    PDF_ENABLE_TABLE_DETECTION: bool = True
    PDF_ENABLE_STRUCTURE_ANALYSIS: bool = True
    PDF_MAX_PAGES_TO_SAMPLE: int = 3  # For text content validation

    # Enhanced Chunking Settings
    CHUNK_QUALITY_THRESHOLD: float = secret_keys_list.get('CHUNK_QUALITY_THRESHOLD', 70.0)
    CHUNK_ENABLE_SMART_BOUNDARIES: bool = True
    CHUNK_MIN_SIZE: int = 10  # Minimum characters per chunk
    CHUNK_PRESERVE_SENTENCES: bool = True
    CHUNK_PRESERVE_PARAGRAPHS: bool = True

    # Content Analysis Settings
    ENABLE_CONTENT_TYPE_DETECTION: bool = True
    ENABLE_LANGUAGE_DETECTION: bool = True
    ENABLE_TABLE_CONTENT_DETECTION: bool = True
    ENABLE_LIST_CONTENT_DETECTION: bool = True

    # Performance Settings
    OCR_BATCH_SIZE: int = 1  # Number of images to process simultaneously
    OCR_ENABLE_CACHING: bool = False  # Disable by default for banking security
    OCR_MEMORY_OPTIMIZATION: bool = True

    # Quality Assessment Settings
    ENABLE_QUALITY_SCORING: bool = True
    ENABLE_CONFIDENCE_WEIGHTING: bool = True
    ENABLE_COMPLETENESS_CHECK: bool = True
    ENABLE_COHERENCE_CHECK: bool = True

    # Banking-Specific Settings
    ENABLE_BANKING_CONTENT_DETECTION: bool = True
    BANKING_KEYWORDS: List[str] = [
        "account", "balance", "transaction", "bank", "payment",
        "deposit", "withdrawal", "statement", "credit", "debit",
        "ifsc", "micr", "upi", "neft", "rtgs", "swift"
    ]

    # Error Handling Settings
    OCR_RETRY_COUNT: int = 2
    OCR_RETRY_DELAY: float = 1.0  # seconds
    OCR_FALLBACK_TO_LEGACY: bool = True  # Fallback to legacy OCR if enhanced fails

    # Logging and Monitoring Settings
    OCR_ENABLE_DETAILED_LOGGING: bool = secret_keys_list.get('OCR_ENABLE_DETAILED_LOGGING', 'false').lower() == 'true'
    OCR_LOG_PROCESSING_STATS: bool = True
    OCR_LOG_CONFIDENCE_SCORES: bool = True

    # Feature Flags
    ENABLE_ENHANCED_OCR: bool = secret_keys_list.get('ENABLE_ENHANCED_OCR', 'true').lower() == 'true'
    ENABLE_LEGACY_COMPATIBILITY: bool = True
    ENABLE_EXPERIMENTAL_FEATURES: bool = secret_keys_list.get('ENABLE_EXPERIMENTAL_FEATURES', 'false').lower() == 'true'

class BhashiniSettings(BaseSettings):
    # Bhashini API Configuration (for translation only)
    BHASHINI_USER_ID:str=secret_keys_list.get('BHASHINI_USER_ID', '')
    BHASHINI_API_KEY:str=secret_keys_list.get('BHASHINI_API_KEY', '')
    BHASHINI_PIPELINE_ID:str="64392f96daac500b55c543cd"
    BHASHINI_CONFIG_URL:str="https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"

class ElevenLabsSettings(BaseSettings):
    # ElevenLabs TTS Configuration
    ELEVENLABS_API_KEY:str=secret_keys_list.get('ELEVENLABS_API_KEY', '')
    ELEVENLABS_VOICE_ID:str=secret_keys_list.get('ELEVENLABS_VOICE_ID', 'TX3LPaxmHKxFdv7VOQHJ')
    ELEVENLABS_API_URL:str="https://api.elevenlabs.io/v1"
    ELEVENLABS_MODEL_ID:str="eleven_multilingual_v2"

mongo_db_settings=DocumentDB()
enhanced_ocr_settings=EnhancedOCRSettings()