import numpy as np
import logging
from deepgram import DeepgramClient, PrerecordedOptions
from fastrtc.utils import audio_to_bytes  # Converts NumPy -> WAV Bytes

# Import settings to get the API Key safely
from backend.app.core.config import settings

# Setup Logger
logger = logging.getLogger(__name__)

class DeepgramSTT:
    """
    Implements the FastRTC STTModel Protocol.
    Converts audio chunks (Turn-based) to text using Deepgram Nova-3.
    """
    def __init__(self):
        # Initialize the Client once
        try:
            self.client = DeepgramClient(settings.DEEPGRAM_API_KEY)
            logger.info("✅ Deepgram STT Service Initialized (Nova-3)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Deepgram: {e}")
            raise e

    def stt(self, audio: tuple[int, np.ndarray]) -> tuple[str, float]:
        """
        The required method for FastRTC.
        Args:
            audio: Tuple of (sample_rate, audio_array)
        Returns:
            tuple: (transcribed_text, confidence_score)
        """
        sample_rate, audio_array = audio

        # 1. Quick validation: If audio is empty or silent, return empty
        if audio_array.size == 0:
            return "", 0.0

        try:
            # 2. Convert Numpy Array -> WAV Bytes
            # FastRTC provides this utility to handle headers/encoding automatically.
            audio_bytes = audio_to_bytes(audio)

            # 3. Configure Deepgram Options
            # We use 'multi' for best Hinglish support (e.g., "Mera paisa kat gaya")
            options = PrerecordedOptions(
                model="nova-3",
                language="multi", 
                smart_format=True,
                punctuate=True,
                utterances=True 
            )

            # 4. Send to Deepgram (REST API)
            # We treat this 'turn' as a file upload. 
            response = self.client.listen.rest.v("1").transcribe_file(
                {"buffer": audio_bytes, "mimetype": "audio/wav"}, 
                options
            )

            # 5. Extract Text and Confidence
            # Safety check to ensure we actually got a transcript
            if (response and 
                response.results and 
                response.results.channels and 
                response.results.channels[0].alternatives):
                
                alt = response.results.channels[0].alternatives[0]
                transcript = alt.transcript.strip()
                confidence = getattr(alt, 'confidence', 0.0) or 0.0
                return transcript, confidence
            
            return "", 0.0

        except Exception as e:
            logger.error(f"⚠️ STT Error: {e}")
            # Return empty so the bot doesn't crash on one bad audio packet
            return "", 0.0

# --- Singleton Instance ---
# You import THIS instance in your pipeline, not the class.
# This ensures we don't reconnect to Deepgram 100 times.
stt_service = DeepgramSTT()