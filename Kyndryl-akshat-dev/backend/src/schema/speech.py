from pydantic import BaseModel, Field
from typing import Optional


class TranscribeRequest(BaseModel):
    """Request schema for audio transcription endpoint"""
    language: Optional[str] = Field("en-US", description="Language code for transcription (e.g., 'en-US', 'hi-IN')")


class TranscribeResponse(BaseModel):
    """Response schema for audio transcription endpoint"""
    text: str = Field(..., description="Transcribed text from audio")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    language: str = Field(..., description="Language used for transcription")
    engine: str = Field(..., description="Speech recognition engine used")
    error: Optional[str] = Field(None, description="Error message if transcription failed")


class VoiceChatRequest(BaseModel):
    """Request schema for voice chat endpoint (STT + Chat + TTS)"""
    document_id: Optional[str] = Field(None, description="Optional document ID for RAG mode")
    language: Optional[str] = Field("en-US", description="Language for speech recognition")
    include_audio_response: Optional[bool] = Field(True, description="Whether to return TTS audio response")


class VoiceChatResponse(BaseModel):
    """Response schema for voice chat endpoint"""
    # STT results
    transcribed_text: str = Field(..., description="Transcribed text from input audio")
    transcription_confidence: float = Field(..., description="STT confidence score")

    # Chat results
    chat_response: str = Field(..., description="AI-generated response text")
    mode: str = Field(..., description="Chat mode: 'rag' or 'general'")
    detected_language: str = Field(..., description="Detected language code")
    language_name: str = Field(..., description="Full language name")
    document_id: Optional[str] = Field(None, description="Document ID used (if RAG mode)")
    chunks_used: Optional[int] = Field(None, description="Number of chunks retrieved (if RAG mode)")

    # TTS results
    audio_url: Optional[str] = Field(None, description="URL to audio response (if TTS enabled)")

    # Error handling
    errors: Optional[list] = Field(None, description="List of non-critical errors during processing")