from fastapi import APIRouter, HTTPException
from services.rag_service import RAGService
from utils.language_detector import LanguageDetector
from schema.chat import ChatRequest, ChatResponse
from lib.logger import logger

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint supporting both RAG and general queries with multi-language support

    **Features:**
    - Automatic language detection
    - Response in the same language as the query
    - Supports Hindi, English, Bengali, Tamil, Telugu, Marathi, Gujarati, and more

    **Logic:**
    - If document_id provided: Use RAG pipeline (semantic search + context-aware LLM)
    - If document_id is None: Direct LLM query (general banking knowledge)
    - Language is automatically detected and response is translated

    **Supported Languages:**
    - Hindi (हिन्दी)
    - English
    - Bengali (বাংলা)
    - Tamil (தமிழ்)
    - Telugu (తెలుగు)
    - Marathi (मराठी)
    - Gujarati (ગુજરાતી)
    - Kannada (ಕನ್ನಡ)
    - Malayalam (മലയാളം)
    - Punjabi (ਪੰਜਾਬੀ)
    - Odia (ଓଡ଼ିଆ)
    - Assamese (অসমীয়া)

    Args:
        request: ChatRequest with query and optional document_id

    Returns:
        ChatResponse with AI-generated response in user's language
    """
    try:
        rag_service = RAGService()
        language_detector = LanguageDetector()

        logger.info(f"Chat request: query='{request.query[:50]}...', document_id={request.document_id}")

        if request.document_id:
            # RAG mode - query with document context and sentiment analysis
            logger.info(f"Using RAG mode with document_id={request.document_id}")

            response_text, detected_language, sentiment_data = rag_service.query_with_rag(
                user_query=request.query,
                document_id=request.document_id
            )

            language_name = language_detector.get_language_name(detected_language)

            return ChatResponse(
                response=response_text,
                mode="rag",
                detected_language=detected_language,
                language_name=language_name,
                document_id=request.document_id,
                chunks_used=30,  # We retrieve top 30 chunks
                sentiment=sentiment_data.get('sentiment'),
                sentiment_confidence=sentiment_data.get('confidence')
            )

        else:
            # General mode - no RAG, with sentiment analysis
            logger.info("Using general mode (no document context)")

            response_text, detected_language, sentiment_data = rag_service.query_without_rag(request.query)

            language_name = language_detector.get_language_name(detected_language)

            return ChatResponse(
                response=response_text,
                mode="general",
                detected_language=detected_language,
                language_name=language_name,
                document_id=None,
                chunks_used=None,
                sentiment=sentiment_data.get('sentiment'),
                sentiment_confidence=sentiment_data.get('confidence')
            )

    except ValueError as e:
        # Validation or query error
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Processing error
        logger.error(f"Chat failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )
