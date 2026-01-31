import requests
from typing import Optional
from configs.config import BhashiniSettings
from lib.logger import logger


class BhashiniTranslationService:
    """Service for Bhashini Neural Machine Translation (NMT)"""

    def __init__(self):
        self.settings = BhashiniSettings()

        # Check if Bhashini is configured
        if not self.settings.BHASHINI_USER_ID or not self.settings.BHASHINI_API_KEY:
            logger.warning("Bhashini credentials not configured, translation will be disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"Bhashini Translation Service initialized: User ID={self.settings.BHASHINI_USER_ID}")

    def _make_config_call(self, source_language: str, target_language: str) -> Optional[dict]:
        """
        Step 1: Pipeline config call for translation

        Args:
            source_language: Source language code (e.g., "hi", "en")
            target_language: Target language code (e.g., "en", "hi")

        Returns:
            dict with serviceId, callback_url, and auth_token
        """
        if not self.enabled:
            return None

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_language,
                            "targetLanguage": target_language
                        }
                    }
                }
            ],
            "pipelineRequestConfig": {
                "pipelineId": self.settings.BHASHINI_PIPELINE_ID
            }
        }

        headers = {
            "userID": self.settings.BHASHINI_USER_ID,
            "ulcaApiKey": self.settings.BHASHINI_API_KEY,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.settings.BHASHINI_CONFIG_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            config_data = response.json()

            # Extract serviceId, callback URL, and auth token
            service_id = config_data['pipelineResponseConfig'][0]['config'][0]['serviceId']
            callback_url = config_data['pipelineInferenceAPIEndPoint']['callbackUrl']
            auth_token = config_data['pipelineInferenceAPIEndPoint']['inferenceApiKey']['value']

            logger.info(f"Translation config successful: {source_language} → {target_language}, serviceId={service_id}")

            return {
                "service_id": service_id,
                "callback_url": callback_url,
                "auth_token": auth_token
            }

        except Exception as e:
            logger.error(f"Translation config call failed: {e}", exc_info=True)
            return None

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> Optional[str]:
        """
        Translate text from source language to target language

        Args:
            text: Text to translate
            source_language: Source language code (e.g., "hi", "en")
            target_language: Target language code (e.g., "en", "hi")

        Returns:
            str: Translated text, or None if translation fails
        """
        if not self.enabled:
            logger.warning("Bhashini translation is disabled, returning original text")
            return text

        # No translation needed if same language
        if source_language == target_language:
            logger.info(f"Source and target language are same ({source_language}), skipping translation")
            return text

        try:
            logger.info(f"Translation request: '{text[:50]}...' from {source_language} to {target_language}")

            # Step 1: Get config
            config = self._make_config_call(source_language, target_language)
            if not config:
                logger.warning("Translation config failed, returning original text")
                return text

            # Step 2: Compute call
            compute_payload = {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {
                            "language": {
                                "sourceLanguage": source_language,
                                "targetLanguage": target_language
                            },
                            "serviceId": config["service_id"]
                        }
                    }
                ],
                "inputData": {
                    "input": [
                        {
                            "source": text
                        }
                    ]
                }
            }

            compute_headers = {
                "Authorization": config["auth_token"],
                "Content-Type": "application/json"
            }

            response = requests.post(
                config["callback_url"],
                json=compute_payload,
                headers=compute_headers,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            # Extract translated text
            translated_text = result['pipelineResponse'][0]['output'][0]['target']

            logger.info(f"Translation successful: '{translated_text[:50]}...'")
            return translated_text

        except Exception as e:
            logger.error(f"Translation failed: {e}", exc_info=True)
            # Return original text if translation fails
            return text
