import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
from typing import Optional, Dict, Any
import io
import tempfile
import os
from lib.logger import logger


class SpeechRecognitionService:
    """Service for Speech-to-Text conversion using Google Speech Recognition"""

    def __init__(self):
        self.recognizer = sr.Recognizer()

        # Check if ffmpeg is available for audio conversion
        if which("ffmpeg") is None:
            logger.warning("ffmpeg not found. Audio format conversion may be limited.")
            self.ffmpeg_available = False
        else:
            self.ffmpeg_available = True

        logger.info("Speech Recognition Service initialized")

    def transcribe_audio(self, audio_content: bytes, audio_format: str = "wav") -> Dict[str, Any]:
        """
        Transcribe audio to text using Google Speech Recognition

        Args:
            audio_content: Raw audio bytes
            audio_format: Audio format ('wav', 'mp3', 'ogg', 'webm', etc.)

        Returns:
            dict: Contains 'text', 'confidence', 'language', etc.
        """
        if not audio_content:
            logger.warning("Empty audio content provided for transcription")
            return {"text": "", "error": "Empty audio content", "confidence": 0.0}

        try:
            logger.info(f"Processing audio for transcription: {len(audio_content)} bytes, format: {audio_format}")

            # Convert audio to WAV format if needed
            audio_data = self._convert_to_wav(audio_content, audio_format)

            if not audio_data:
                return {"text": "", "error": "Audio conversion failed", "confidence": 0.0}

            # Create AudioData object for speech recognition
            with io.BytesIO(audio_data) as audio_file:
                with sr.AudioFile(audio_file) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                    # Record the audio data
                    audio = self.recognizer.record(source)

            # Perform speech recognition with multiple engines for fallback
            transcription_result = self._transcribe_with_fallback(audio)

            logger.info(f"Transcription completed: {len(transcription_result.get('text', ''))} characters")

            return transcription_result

        except Exception as e:
            logger.error(f"Speech transcription failed: {e}", exc_info=True)
            return {"text": "", "error": str(e), "confidence": 0.0}

    def _convert_to_wav(self, audio_content: bytes, source_format: str) -> Optional[bytes]:
        """
        Convert audio to WAV format for speech recognition

        Args:
            audio_content: Raw audio bytes
            source_format: Source audio format

        Returns:
            bytes: WAV audio data or None if conversion failed
        """
        try:
            # If already WAV, return as-is
            if source_format.lower() == "wav":
                return audio_content

            # Convert using pydub
            if self.ffmpeg_available:
                # Use pydub with ffmpeg for broader format support
                audio = AudioSegment.from_file(
                    io.BytesIO(audio_content),
                    format=source_format.lower()
                )

                # Convert to WAV format with proper settings for speech recognition
                audio = audio.set_frame_rate(16000)  # 16kHz is good for speech
                audio = audio.set_channels(1)        # Mono
                audio = audio.set_sample_width(2)    # 16-bit

                # Export to WAV
                wav_buffer = io.BytesIO()
                audio.export(wav_buffer, format="wav")
                return wav_buffer.getvalue()
            else:
                # Fallback: assume input is already in compatible format
                logger.warning("ffmpeg not available, assuming audio is WAV compatible")
                return audio_content

        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            return None

    def _transcribe_with_fallback(self, audio_data: sr.AudioData) -> Dict[str, Any]:
        """
        Transcribe audio with multiple recognition engines for fallback

        Args:
            audio_data: AudioData object from speech_recognition

        Returns:
            dict: Transcription result with text, confidence, and engine used
        """
        # Try Google Speech Recognition (free, good quality)
        try:
            text = self.recognizer.recognize_google(audio_data, language="en-US")
            return {
                "text": text,
                "confidence": 0.85,  # Google doesn't provide confidence, estimate
                "language": "en-US",
                "engine": "google",
                "error": None
            }
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.warning(f"Google Speech Recognition service error: {e}")
        except Exception as e:
            logger.warning(f"Google Speech Recognition error: {e}")

        # Fallback to Sphinx (offline, lower quality but always available)
        try:
            text = self.recognizer.recognize_sphinx(audio_data)
            return {
                "text": text,
                "confidence": 0.6,  # Sphinx typically has lower accuracy
                "language": "en-US",
                "engine": "sphinx",
                "error": None
            }
        except sr.UnknownValueError:
            logger.warning("Sphinx could not understand audio")
        except sr.RequestError as e:
            logger.warning(f"Sphinx recognition error: {e}")
        except Exception as e:
            logger.warning(f"Sphinx recognition error: {e}")

        # If all engines fail
        return {
            "text": "",
            "confidence": 0.0,
            "language": "unknown",
            "engine": "none",
            "error": "No speech recognition engine could process the audio"
        }

    def transcribe_with_language(self, audio_content: bytes, language: str = "en-US", audio_format: str = "wav") -> Dict[str, Any]:
        """
        Transcribe audio with specific language

        Args:
            audio_content: Raw audio bytes
            language: Language code (e.g., 'en-US', 'hi-IN', 'bn-IN')
            audio_format: Audio format

        Returns:
            dict: Transcription result
        """
        try:
            logger.info(f"Transcribing audio with language: {language}")

            # Convert audio to WAV
            audio_data = self._convert_to_wav(audio_content, audio_format)
            if not audio_data:
                return {"text": "", "error": "Audio conversion failed", "confidence": 0.0}

            # Create AudioData object
            with io.BytesIO(audio_data) as audio_file:
                with sr.AudioFile(audio_file) as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.record(source)

            # Try Google with specific language
            try:
                text = self.recognizer.recognize_google(audio, language=language)
                return {
                    "text": text,
                    "confidence": 0.85,
                    "language": language,
                    "engine": "google",
                    "error": None
                }
            except Exception as e:
                logger.warning(f"Language-specific recognition failed for {language}: {e}")
                # Fallback to default language
                return self.transcribe_audio(audio_content, audio_format)

        except Exception as e:
            logger.error(f"Language-specific transcription failed: {e}", exc_info=True)
            return {"text": "", "error": str(e), "confidence": 0.0}

    def get_supported_languages(self) -> list:
        """
        Get list of supported languages for speech recognition

        Returns:
            list: Language codes supported by the service
        """
        return [
            "en-US",    # English (US)
            "en-GB",    # English (UK)
            "hi-IN",    # Hindi (India)
            "bn-IN",    # Bengali (India)
            "ta-IN",    # Tamil (India)
            "te-IN",    # Telugu (India)
            "mr-IN",    # Marathi (India)
            "gu-IN",    # Gujarati (India)
            "kn-IN",    # Kannada (India)
            "ml-IN",    # Malayalam (India)
            "pa-IN",    # Punjabi (India)
            "or-IN",    # Odia (India)
            "as-IN",    # Assamese (India)
            "en-IN",    # English (India)
        ]

    def is_available(self) -> bool:
        """
        Check if speech recognition service is available

        Returns:
            bool: True if service can process audio
        """
        try:
            # Test if we can create a recognizer
            test_recognizer = sr.Recognizer()
            return True
        except Exception as e:
            logger.error(f"Speech recognition not available: {e}")
            return False