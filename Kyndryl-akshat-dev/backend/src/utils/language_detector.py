import re
from lib.logger import logger


class LanguageDetector:
    """Detect language based on Unicode character scripts"""

    # Unicode ranges for different scripts
    SCRIPT_RANGES = {
        'hi': [(0x0900, 0x097F)],  # Devanagari (Hindi, Marathi)
        'bn': [(0x0980, 0x09FF)],  # Bengali
        'pa': [(0x0A00, 0x0A7F)],  # Gurmukhi (Punjabi)
        'gu': [(0x0A80, 0x0AFF)],  # Gujarati
        'or': [(0x0B00, 0x0B7F)],  # Odia
        'ta': [(0x0B80, 0x0BFF)],  # Tamil
        'te': [(0x0C00, 0x0C7F)],  # Telugu
        'kn': [(0x0C80, 0x0CFF)],  # Kannada
        'ml': [(0x0D00, 0x0D7F)],  # Malayalam
        'as': [(0x0980, 0x09FF)],  # Assamese (uses Bengali script)
        'ur': [(0x0600, 0x06FF)],  # Arabic script (Urdu)
    }

    LANGUAGE_NAMES = {
        'en': 'English',
        'hi': 'Hindi (हिन्दी)',
        'bn': 'Bengali (বাংলা)',
        'ta': 'Tamil (தமிழ்)',
        'te': 'Telugu (తెలుగు)',
        'mr': 'Marathi (मराठी)',
        'gu': 'Gujarati (ગુજરાતી)',
        'kn': 'Kannada (ಕನ್ನಡ)',
        'ml': 'Malayalam (മലയാളം)',
        'pa': 'Punjabi (ਪੰਜਾਬੀ)',
        'or': 'Odia (ଓଡ଼ିଆ)',
        'as': 'Assamese (অসমীয়া)',
        'ur': 'Urdu (اردو)',
    }

    @staticmethod
    def _is_in_range(char: str, ranges: list) -> bool:
        """Check if character is in given Unicode ranges"""
        if not char:
            return False
        code_point = ord(char)
        return any(start <= code_point <= end for start, end in ranges)

    @staticmethod
    def _detect_script(text: str) -> str:
        """
        Detect language based on Unicode script

        Args:
            text: Input text

        Returns:
            str: Language code based on script detection
        """
        if not text:
            return 'en'

        # Count characters from each script
        script_counts = {lang: 0 for lang in LanguageDetector.SCRIPT_RANGES.keys()}

        for char in text:
            for lang, ranges in LanguageDetector.SCRIPT_RANGES.items():
                if LanguageDetector._is_in_range(char, ranges):
                    script_counts[lang] += 1
                    break

        # Find script with most characters
        max_count = max(script_counts.values())

        if max_count > 0:
            # Return language with highest character count
            for lang, count in script_counts.items():
                if count == max_count:
                    return lang

        # Default to English if no Indic script detected
        return 'en'

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect language of the input text using script detection

        Args:
            text: Input text to detect language

        Returns:
            str: Language code (e.g., 'hi', 'en', 'bn')
        """
        try:
            if not text or len(text.strip()) < 3:
                logger.warning("Text too short for language detection, defaulting to English")
                return 'en'

            # Remove punctuation and numbers for better detection
            clean_text = re.sub(r'[0-9\s\.\,\!\?\-\:\;]', '', text)

            if not clean_text:
                logger.warning("No characters to analyze, defaulting to English")
                return 'en'

            detected = LanguageDetector._detect_script(clean_text)
            logger.info(f"Detected language: {detected} for text: '{text[:50]}...'")

            return detected

        except Exception as e:
            logger.error(f"Language detection failed: {e}", exc_info=True)
            return 'en'  # Default to English on error

    @staticmethod
    def get_language_name(language_code: str) -> str:
        """
        Get full language name from code

        Args:
            language_code: Language code (e.g., 'hi', 'en')

        Returns:
            str: Full language name
        """
        return LanguageDetector.LANGUAGE_NAMES.get(language_code, 'English')

    @staticmethod
    def is_translation_needed(source_lang: str, target_lang: str = 'en') -> bool:
        """
        Check if translation is needed

        Args:
            source_lang: Source language code
            target_lang: Target language code (default: 'en')

        Returns:
            bool: True if translation needed, False otherwise
        """
        return source_lang != target_lang

    @staticmethod
    def is_indian_language(language_code: str) -> bool:
        """
        Check if language is an Indian language

        Args:
            language_code: Language code

        Returns:
            bool: True if Indian language, False otherwise
        """
        indian_languages = ['hi', 'bn', 'ta', 'te', 'mr', 'gu', 'kn', 'ml', 'pa', 'or', 'as', 'ur']
        return language_code in indian_languages
