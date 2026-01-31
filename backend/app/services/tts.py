import os
import logging
import numpy as np
from cartesia import Cartesia
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class CartesiaTTS:
    # Voice personas - can be switched at runtime
    VOICE_PERSONAS = {
        "male": "a0e99841-438c-4a64-b679-ae501e7d6091",    # Default male voice
        "female": "faf0731e-dfb9-4cfc-8119-259a79b27e12",  # Female voice (update with your preferred ID)
    }
    
    def __init__(self):
        # Ensure CARTESIA_API_KEY is in your .env file
        self.client = Cartesia(api_key=settings.CARTESIA_API_KEY)
        
        # Default to female voice (Urja is a female assistant)
        self.current_persona = "female"
        self.voice_id = self.VOICE_PERSONAS[self.current_persona]
        
        self.model_id = "sonic-3"  # Multilingual (Handles English + Hindi)
        
        # Audio Format Config - 24kHz for FastRTC compatibility
        self.sample_rate = 24000
        self.encoding = "pcm_f32le"  # Maps to numpy float32
        
        logger.info(f"✅ Cartesia TTS Initialized (Persona: {self.current_persona}, Rate: {self.sample_rate}Hz)")

    def set_voice_persona(self, persona: str) -> bool:
        """
        Switch between voice personas.
        Args:
            persona: "male" or "female"
        Returns:
            True if switched successfully, False if invalid persona
        """
        if persona not in self.VOICE_PERSONAS:
            logger.warning(f"⚠️ Invalid persona: {persona}. Available: {list(self.VOICE_PERSONAS.keys())}")
            return False
        
        self.current_persona = persona
        self.voice_id = self.VOICE_PERSONAS[persona]
        logger.info(f"🔄 Voice persona switched to: {persona} (ID: {self.voice_id})")
        return True

    def get_current_persona(self) -> dict:
        """Get current voice persona info."""
        return {
            "persona": self.current_persona,
            "voice_id": self.voice_id,
            "available_personas": list(self.VOICE_PERSONAS.keys())
        }

    def set_custom_voice_id(self, voice_id: str):
        """
        Set a custom Cartesia voice ID directly.
        Use this if you want to use a voice not in VOICE_PERSONAS.
        """
        self.voice_id = voice_id
        self.current_persona = "custom"
        logger.info(f"🔄 Custom voice ID set: {voice_id}")

    def generate_audio(self, text: str):
        """
        Stream audio chunks via WebSocket.
        Yields: (sample_rate, numpy_audio_array) in FastRTC format
        """
        if not text:
            return

        try:
            # 1. Open WebSocket
            ws = self.client.tts.websocket()
            
            # 2. Configure Output Format (Raw for Streaming)
            output_format = {
                "container": "raw",
                "encoding": self.encoding,
                "sample_rate": self.sample_rate
            }
            
            # 3. Configure Voice (new Cartesia SDK format)
            voice = {
                "mode": "id",
                "id": self.voice_id
            }

            # 4. Send Text
            # We don't set 'language' explicitly; Sonic-3 auto-detects English/Hindi mix.
            output = ws.send(
                model_id=self.model_id,
                transcript=text,
                voice=voice,  # Use voice dict, not voice_id
                stream=True,
                output_format=output_format
            )

            # 5. Stream & Yield
            for chunk in output:
                if chunk.audio:
                    # chunk.audio is already bytes from the SDK
                    audio_data = np.frombuffer(chunk.audio, dtype=np.float32)
                    
                    # FastRTC expects: (sample_rate, 1D numpy array) for mono audio
                    yield (self.sample_rate, audio_data)

            ws.close()

        except Exception as e:
            logger.error(f"⚠️ Cartesia TTS Error: {e}")
            # Yield silent chunk to prevent crash
            yield (self.sample_rate, np.zeros(self.sample_rate, dtype=np.float32))


# Singleton instance
tts_service = CartesiaTTS()