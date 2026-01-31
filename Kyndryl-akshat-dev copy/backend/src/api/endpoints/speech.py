from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.speech_recognition_service import SpeechRecognitionService
from services.rag_service import RAGService
from services.elevenlabs_service import ElevenLabsService
from services.azure_storage_service import AzureStorageService
from utils.file_handler import FileHandler
from utils.language_detector import LanguageDetector
from schema.speech import TranscribeResponse, VoiceChatResponse
from lib.logger import logger
import uuid
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/speech", tags=["Speech"])


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    language: Optional[str] = Form("en-US", description="Language code for transcription")
):
    """
    Transcribe audio file to text using Speech-to-Text

    **Supported Audio Formats:**
    - WAV, MP3, OGG, WebM, M4A, FLAC

    **Supported Languages:**
    - en-US (English - US)
    - hi-IN (Hindi)
    - bn-IN (Bengali)
    - ta-IN (Tamil)
    - te-IN (Telugu)
    - mr-IN (Marathi)
    - And more...

    **Flow:**
    1. Validate audio file format and size
    2. Convert to WAV if needed
    3. Transcribe using Google Speech Recognition with fallback to Sphinx
    4. Return transcribed text with confidence score

    Args:
        file: Audio file upload
        language: Target language for transcription (default: en-US)

    Returns:
        TranscribeResponse with transcribed text and metadata
    """
    try:
        # Initialize services
        file_handler = FileHandler()
        stt_service = SpeechRecognitionService()

        logger.info(f"STT request: {file.filename}, language={language}")

        # Step 1: Validate audio file
        audio_content, audio_format = await file_handler.validate_audio_file(file)

        # Step 2: Transcribe audio
        if language and language != "en-US":
            # Use language-specific transcription
            result = stt_service.transcribe_with_language(audio_content, language, audio_format)
        else:
            # Use default transcription
            result = stt_service.transcribe_audio(audio_content, audio_format)

        logger.info(f"STT completed: {len(result.get('text', ''))} characters transcribed")

        return TranscribeResponse(
            text=result.get('text', ''),
            confidence=result.get('confidence', 0.0),
            language=result.get('language', language or 'en-US'),
            engine=result.get('engine', 'unknown'),
            error=result.get('error')
        )

    except ValueError as e:
        # File validation error
        logger.error(f"Audio validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Processing error
        logger.error(f"Speech transcription failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Speech transcription failed: {str(e)}"
        )


@router.post("/voice-chat", response_model=VoiceChatResponse)
async def voice_chat(
    file: UploadFile = File(..., description="Audio file with user's voice message"),
    document_id: Optional[str] = Form(None, description="Document ID for RAG mode"),
    language: Optional[str] = Form("en-US", description="Language for speech recognition"),
    include_audio_response: Optional[bool] = Form(True, description="Include TTS audio response")
):
    """
    Complete voice chat pipeline: STT → Chat → TTS

    **Voice Chat Flow:**
    1. **Speech-to-Text**: Transcribe user's audio to text
    2. **Chat Processing**: Process transcribed text with AI (RAG or general mode)
    3. **Text-to-Speech**: Convert AI response back to audio (optional)

    **Features:**
    - Multi-language speech recognition
    - RAG mode with document context
    - Multi-language AI responses
    - Audio response generation
    - Error resilience with partial results

    Args:
        file: Audio file with user's voice message
        document_id: Optional document ID for RAG context
        language: Language for speech recognition
        include_audio_response: Whether to generate audio response

    Returns:
        VoiceChatResponse with transcription, chat response, and optional audio
    """
    errors = []
    transcribed_text = ""
    audio_url = None

    try:
        # Initialize services
        file_handler = FileHandler()
        stt_service = SpeechRecognitionService()
        rag_service = RAGService()
        language_detector = LanguageDetector()

        logger.info(f"Voice chat request: {file.filename}, document_id={document_id}, language={language}")

        # Step 1: Speech-to-Text
        try:
            audio_content, audio_format = await file_handler.validate_audio_file(file)

            if language and language != "en-US":
                stt_result = stt_service.transcribe_with_language(audio_content, language, audio_format)
            else:
                stt_result = stt_service.transcribe_audio(audio_content, audio_format)

            transcribed_text = stt_result.get('text', '')
            transcription_confidence = stt_result.get('confidence', 0.0)

            if not transcribed_text.strip():
                raise ValueError("No speech could be transcribed from the audio")

            logger.info(f"STT successful: '{transcribed_text[:50]}...', confidence={transcription_confidence}")

        except Exception as e:
            logger.error(f"STT failed: {e}")
            raise HTTPException(status_code=400, detail=f"Speech transcription failed: {str(e)}")

        # Step 2: Chat Processing
        try:
            if document_id:
                # RAG mode
                logger.info(f"Using RAG mode with document_id={document_id}")
                chat_response, detected_language, sentiment_data = rag_service.query_with_rag(
                    user_query=transcribed_text,
                    document_id=document_id
                )
                mode = "rag"
                chunks_used = 30
            else:
                # General mode
                logger.info("Using general mode (no document context)")
                chat_response, detected_language, sentiment_data = rag_service.query_without_rag(transcribed_text)
                mode = "general"
                chunks_used = None

            language_name = language_detector.get_language_name(detected_language)

            logger.info(f"Chat successful: {len(chat_response)} characters, language={detected_language}, sentiment={sentiment_data.get('sentiment', 'unknown')}")

        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            errors.append(f"Chat processing failed: {str(e)}")
            chat_response = "I apologize, but I encountered an error processing your request."
            detected_language = "en"
            language_name = "English"
            mode = "error"
            chunks_used = None

        # Step 3: Text-to-Speech (optional)
        if include_audio_response and chat_response:
            try:
                tts_service = ElevenLabsService()
                logger.info(f"TTS requested for {len(chat_response)} character response")

                if tts_service.is_available():
                    logger.info(f"TTS service available - API Key configured: {bool(tts_service.settings.ELEVENLABS_API_KEY)}, Voice ID: {tts_service.settings.ELEVENLABS_VOICE_ID}")

                    audio_content = tts_service.text_to_speech(chat_response)
                    if audio_content:
                        logger.info(f"TTS generation successful: {len(audio_content)} bytes generated")

                        # Store audio in Azure Blob Storage
                        azure_storage = AzureStorageService()
                        audio_filename = f"voice_chat_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}.mp3"
                        logger.info(f"Uploading audio to Azure storage: {audio_filename}")

                        audio_url = await azure_storage.upload_audio_blob(audio_content, audio_filename)
                        logger.info(f"TTS successful - Audio URL: {audio_url}")
                    else:
                        logger.error("TTS generation returned empty audio content")
                        errors.append("TTS conversion failed: empty audio returned")
                else:
                    logger.warning(f"TTS service not available - API Key: {bool(tts_service.settings.ELEVENLABS_API_KEY)}, Voice ID: {tts_service.settings.ELEVENLABS_VOICE_ID}")
                    errors.append("TTS service not available: API key not configured")

            except Exception as e:
                logger.error(f"TTS failed with exception: {e}", exc_info=True)
                errors.append(f"TTS failed: {str(e)}")

        logger.info(f"Voice chat completed: STT→Chat→TTS pipeline finished")

        return VoiceChatResponse(
            # STT results
            transcribed_text=transcribed_text,
            transcription_confidence=transcription_confidence,

            # Chat results
            chat_response=chat_response,
            mode=mode,
            detected_language=detected_language,
            language_name=language_name,
            document_id=document_id,
            chunks_used=chunks_used,

            # TTS results
            audio_url=audio_url,

            # Errors
            errors=errors if errors else None
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Catastrophic error
        logger.error(f"Voice chat failed catastrophically: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Voice chat processing failed: {str(e)}"
        )


@router.get("/supported-languages")
async def get_supported_languages():
    """
    Get list of supported languages for speech recognition

    Returns:
        dict: List of supported language codes and names
    """
    try:
        stt_service = SpeechRecognitionService()
        languages = stt_service.get_supported_languages()

        language_map = {
            "en-US": "English (US)",
            "en-GB": "English (UK)",
            "hi-IN": "Hindi (India)",
            "bn-IN": "Bengali (India)",
            "ta-IN": "Tamil (India)",
            "te-IN": "Telugu (India)",
            "mr-IN": "Marathi (India)",
            "gu-IN": "Gujarati (India)",
            "kn-IN": "Kannada (India)",
            "ml-IN": "Malayalam (India)",
            "pa-IN": "Punjabi (India)",
            "or-IN": "Odia (India)",
            "as-IN": "Assamese (India)",
            "en-IN": "English (India)"
        }

        supported = [
            {"code": lang, "name": language_map.get(lang, lang)}
            for lang in languages
        ]

        return {
            "supported_languages": supported,
            "total_count": len(supported)
        }

    except Exception as e:
        logger.error(f"Failed to get supported languages: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve supported languages")


@router.get("/tts-status")
async def check_tts_status():
    """
    Check TTS service availability and configuration status

    Returns diagnostic information about the ElevenLabs TTS service:
    - Is service available
    - API key configured status
    - Voice ID being used

    Use this endpoint to troubleshoot TTS issues.
    """
    try:
        tts_service = ElevenLabsService()
        is_available = tts_service.is_available()

        # Get configuration details
        api_key = tts_service.settings.ELEVENLABS_API_KEY
        api_key_configured = bool(api_key)
        voice_id = tts_service.settings.ELEVENLABS_VOICE_ID

        # Check for whitespace issues
        api_key_has_whitespace = api_key != api_key.strip() if api_key else False

        # Log the status with API key preview (first/last 4 chars)
        api_key_preview = f"{api_key[:4]}...{api_key[-4:]}" if api_key and len(api_key) > 8 else "N/A"
        logger.info(f"TTS Status Check - Available: {is_available}, API Key: {api_key_preview}, Voice ID: {voice_id}")

        # Test the API key by getting voice info
        test_result = None
        try:
            voice_info = tts_service.get_voice_info()
            test_result = "success" if voice_info else "failed"
        except Exception as test_error:
            test_result = f"error: {str(test_error)}"

        # Get subscription and quota information
        quota_info = None
        if is_available:
            try:
                subscription_info = tts_service.get_subscription_info()
                if subscription_info:
                    # Extract quota information from subscription
                    character_count = subscription_info.get("character_count", 0)
                    character_limit = subscription_info.get("character_limit", 0)
                    remaining = character_limit - character_count

                    quota_info = {
                        "character_count": character_count,
                        "character_limit": character_limit,
                        "remaining": remaining,
                        "tier": subscription_info.get("tier", "unknown"),
                        "usage_percentage": round((character_count / character_limit * 100) if character_limit > 0 else 0, 2)
                    }
                    logger.info(f"Quota Info - Used: {character_count}/{character_limit}, Remaining: {remaining}")
            except Exception as quota_error:
                logger.error(f"Failed to get quota info: {quota_error}")
                quota_info = {"error": "Failed to retrieve quota information"}

        status_response = {
            "available": is_available,
            "api_key_configured": api_key_configured,
            "api_key_length": len(api_key) if api_key else 0,
            "api_key_preview": api_key_preview,
            "api_key_has_whitespace": api_key_has_whitespace,
            "voice_id": voice_id,
            "api_test_result": test_result,
            "status": "ready" if is_available else "not_configured"
        }

        # Add quota info if available
        if quota_info:
            status_response["quota"] = quota_info

        return status_response

    except Exception as e:
        logger.error(f"TTS status check failed: {e}")
        return {
            "available": False,
            "api_key_configured": False,
            "voice_id": None,
            "status": "error",
            "error": str(e)
        }


@router.post("/synthesize")
async def synthesize_text(
    text: str = Form(..., description="Text to convert to speech"),
    language: Optional[str] = Form("en", description="Language code (default: en)")
):
    """
    Convert text to speech and return audio URL

    **Text-to-Speech Synthesis:**
    - Converts provided text to natural-sounding speech
    - Supports multiple languages via ElevenLabs multilingual model
    - Returns Azure Blob Storage URL for generated audio

    **Use Case:**
    - Generate TTS for typed text messages (not voice messages)
    - Allow users to hear bot responses without using voice input

    Args:
        text: Text content to synthesize
        language: Language code (default: en)

    Returns:
        JSON with audio_url field containing the audio file URL
    """
    try:
        logger.info(f"Text synthesis requested: {len(text)} characters, language={language}")

        # Initialize TTS service
        tts_service = ElevenLabsService()

        if not tts_service.is_available():
            logger.error("TTS service not available for text synthesis")
            raise HTTPException(
                status_code=503,
                detail="TTS service not available. Please check API key configuration."
            )

        # Truncate text if too long (ElevenLabs has character limits)
        max_chars = 2500
        if len(text) > max_chars:
            logger.warning(f"Text too long ({len(text)} chars), truncating to {max_chars}")
            text = text[:max_chars] + "..."

        # Generate audio
        audio_content = tts_service.text_to_speech(text)
        if not audio_content:
            logger.error("TTS generation returned empty audio content")
            raise HTTPException(
                status_code=500,
                detail="TTS generation failed: empty audio returned"
            )

        logger.info(f"TTS generation successful: {len(audio_content)} bytes")

        # Upload to Azure Blob Storage
        azure_storage = AzureStorageService()
        audio_filename = f"synthesized_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}.mp3"
        logger.info(f"Uploading synthesized audio to Azure: {audio_filename}")

        audio_url = await azure_storage.upload_audio_blob(audio_content, audio_filename)
        logger.info(f"Text synthesis successful: {audio_url}")

        return {
            "audio_url": audio_url,
            "text_length": len(text),
            "audio_size": len(audio_content)
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"Text synthesis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Text synthesis failed: {str(e)}"
        )