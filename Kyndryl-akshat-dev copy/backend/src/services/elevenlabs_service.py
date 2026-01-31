import requests
from typing import Optional
from configs.config import ElevenLabsSettings
from lib.logger import logger


class ElevenLabsService:
    """Service for ElevenLabs Text-to-Speech conversion"""

    def __init__(self):
        self.settings = ElevenLabsSettings()

        # Check if ElevenLabs is configured
        if not self.settings.ELEVENLABS_API_KEY:
            logger.warning("ElevenLabs API key not configured, TTS will be disabled")
            self.enabled = False
        else:
            # Strip whitespace from API key (common issue)
            self.api_key = self.settings.ELEVENLABS_API_KEY.strip()

            self.enabled = True
            api_key_preview = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "****"
            logger.info(f"ElevenLabs TTS Service initialized: Voice ID={self.settings.ELEVENLABS_VOICE_ID}, API Key={api_key_preview}")

    def text_to_speech(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech using ElevenLabs API

        Args:
            text: The text to convert to speech

        Returns:
            bytes: Audio content in MP3 format, or None if failed
        """
        if not self.enabled:
            logger.warning("ElevenLabs TTS is disabled - API key not configured")
            return None

        if not text or not text.strip():
            logger.warning("Empty text provided for TTS conversion")
            return None

        # Truncate text if too long (ElevenLabs has limits)
        max_length = 2500
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + "..."
            logger.info(f"Text truncated to {len(text)} characters for TTS")

        try:
            # Prepare the API request
            url = f"{self.settings.ELEVENLABS_API_URL}/text-to-speech/{self.settings.ELEVENLABS_VOICE_ID}"

            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }

            payload = {
                "text": text,
                "model_id": self.settings.ELEVENLABS_MODEL_ID,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }

            logger.info(f"Converting text to speech: {len(text)} characters")
            logger.info(f"Sending request to: {url}")
            logger.info(f"Using API key: {self.api_key[:8]}...{self.api_key[-4:]}")
            logger.info(f"Voice ID: {self.settings.ELEVENLABS_VOICE_ID}")
            logger.info(f"Model: {self.settings.ELEVENLABS_MODEL_ID}")

            # Make the API request
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=60  # TTS can take longer than normal API calls
            )

            logger.info(f"ElevenLabs API Response Status: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")

            response.raise_for_status()

            # Return the audio content
            audio_content = response.content
            logger.info(f"TTS conversion successful: {len(audio_content)} bytes")

            return audio_content

        except requests.exceptions.Timeout as e:
            logger.error(f"ElevenLabs API Timeout: Request took longer than 60 seconds")
            logger.error(f"This might indicate: slow network, large text, or ElevenLabs service issues")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"ElevenLabs API Connection Error: Cannot reach {url}")
            logger.error(f"Check your internet connection and ElevenLabs service status")
            return None
        except requests.exceptions.HTTPError as e:
            # Log detailed error information
            status_code = e.response.status_code if e.response else "unknown"
            error_body = e.response.text if e.response else "no response body"

            logger.error(f"ElevenLabs API HTTP Error {status_code}")
            logger.error(f"Request URL: {url}")
            logger.error(f"Voice ID: {self.settings.ELEVENLABS_VOICE_ID}")
            logger.error(f"API Key (first 8): {self.api_key[:8]}...")

            # Parse error details if available
            if e.response and error_body:
                try:
                    import json
                    error_json = json.loads(error_body)

                    # Check for quota exceeded error
                    if isinstance(error_json.get('detail'), dict):
                        detail = error_json['detail']
                        if detail.get('status') == 'quota_exceeded':
                            logger.error("=" * 80)
                            logger.error("ELEVENLABS QUOTA EXCEEDED!")
                            logger.error(f"Message: {detail.get('message', 'No message')}")
                            logger.error("=" * 80)
                            logger.error("To fix this:")
                            logger.error("1. Purchase more credits at https://elevenlabs.io/")
                            logger.error("2. Or create a new account and update ELEVENLABS_API_KEY in .env")
                            logger.error("3. Or wait for your quota to reset (check your ElevenLabs dashboard)")
                            logger.error("=" * 80)
                        else:
                            logger.error(f"ElevenLabs Error Details: {error_json}")
                    else:
                        logger.error(f"ElevenLabs Error Details: {error_json}")
                except json.JSONDecodeError:
                    logger.error(f"ElevenLabs Error (raw): {error_body}")
                except Exception as parse_error:
                    logger.error(f"ElevenLabs Error (raw): {error_body}")
                    logger.error(f"Failed to parse error details: {parse_error}")

            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"ElevenLabs API request failed: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"TTS conversion failed: {e}", exc_info=True)
            return None

    def get_voice_info(self) -> Optional[dict]:
        """
        Get information about the configured voice

        Returns:
            dict: Voice information or None if failed
        """
        if not self.enabled:
            return None

        try:
            url = f"{self.settings.ELEVENLABS_API_URL}/voices/{self.settings.ELEVENLABS_VOICE_ID}"

            headers = {
                "Accept": "application/json",
                "xi-api-key": self.api_key
            }

            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            voice_info = response.json()
            logger.info(f"Voice info retrieved: {voice_info.get('name', 'Unknown')}")

            return voice_info

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "unknown"
            error_body = e.response.text if e.response else "no response body"
            logger.error(f"ElevenLabs Voice Info HTTP Error {status_code}: {error_body}")
            logger.error(f"Voice ID: {self.settings.ELEVENLABS_VOICE_ID}")
            logger.error(f"API Key (first 8): {self.api_key[:8]}...")
            return None
        except Exception as e:
            logger.error(f"Failed to get voice info: {e}", exc_info=True)
            return None

    def get_subscription_info(self) -> Optional[dict]:
        """
        Get current subscription and quota information from ElevenLabs

        Returns:
            dict: Subscription information including character count, limits, and remaining quota
                  Returns None if failed or service is disabled
        """
        if not self.enabled:
            return None

        try:
            url = f"{self.settings.ELEVENLABS_API_URL}/user/subscription"

            headers = {
                "Accept": "application/json",
                "xi-api-key": self.api_key
            }

            logger.info("Fetching ElevenLabs subscription info...")

            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            subscription_info = response.json()
            logger.info(f"Subscription info retrieved: {subscription_info.get('tier', 'Unknown')} tier")

            return subscription_info

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "unknown"
            error_body = e.response.text if e.response else "no response body"
            logger.error(f"Failed to get subscription info - HTTP Error {status_code}: {error_body}")
            return None
        except Exception as e:
            logger.error(f"Failed to get subscription info: {e}", exc_info=True)
            return None

    def is_available(self) -> bool:
        """
        Check if ElevenLabs service is available

        Returns:
            bool: True if service is configured and available
        """
        return self.enabled