"""
Image Processor - Enhanced OCR for Image Files

This module provides enhanced OCR capabilities for image files with improved
preprocessing, confidence scoring, and multi-language support for the banking application.
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import io
import numpy as np
from lib.logger import logger
from configs.config import DocumentSettings
import re


class ImageProcessor:
    """
    Enhanced image processor with advanced OCR capabilities.

    Features:
    - Advanced image preprocessing for better OCR accuracy
    - Confidence scoring and quality assessment
    - Multi-language OCR support
    - Enhanced text cleaning and validation
    - Comprehensive metadata extraction
    """

    def __init__(self):
        """Initialize the image processor"""
        self.settings = DocumentSettings()

        try:
            # Test if Tesseract is available
            pytesseract.get_tesseract_version()
            self.available = True
            logger.info(f"Image Processor initialized with languages: {self.settings.OCR_LANGUAGES}")
        except Exception as e:
            logger.error(f"Tesseract not found or not properly configured: {e}")
            self.available = False

    def extract_text_with_metadata(
        self,
        image_content: bytes,
        filename: str
    ) -> Dict[str, Any]:
        """
        Extract text from image with comprehensive metadata and quality assessment.

        Args:
            image_content: Raw image bytes
            filename: Original filename

        Returns:
            dict: Contains extracted text, confidence, and detailed metadata
        """
        if not self.available:
            raise RuntimeError("Image Processor is not available - Tesseract not properly configured")

        if not image_content:
            raise ValueError("Empty image content provided for OCR")

        try:
            # Convert bytes to PIL Image
            original_image = Image.open(io.BytesIO(image_content))

            logger.info(f"Processing image for OCR: {filename}, {original_image.size[0]}x{original_image.size[1]} pixels, mode: {original_image.mode}")

            # Convert to RGB if necessary (handles transparency, etc.)
            if original_image.mode not in ('RGB', 'L'):
                original_image = original_image.convert('RGB')

            # Analyze image quality and characteristics
            image_analysis = self._analyze_image(original_image)

            # Apply advanced preprocessing
            processed_image = self._advanced_preprocess_image(original_image, image_analysis)

            # Extract text with multiple methods for best results
            extraction_results = self._extract_with_multiple_methods(processed_image, filename)

            # Select best extraction result
            best_result = self._select_best_extraction(extraction_results)

            # Enhanced text cleaning
            cleaned_text = self._enhanced_clean_text(best_result['text'])

            # Calculate comprehensive confidence metrics
            confidence_metrics = self._calculate_confidence_metrics(extraction_results, cleaned_text)

            # Generate comprehensive metadata
            metadata = self._generate_image_metadata(
                original_image=original_image,
                processed_image=processed_image,
                image_analysis=image_analysis,
                filename=filename
            )

            result = {
                'text': cleaned_text,
                'confidence': confidence_metrics['overall_confidence'],
                'metadata': metadata,
                'confidence_metrics': confidence_metrics,
                'extraction_methods': {
                    method: {
                        'text_length': len(result['text']),
                        'confidence': result['confidence'],
                        'word_count': result['word_count']
                    }
                    for method, result in extraction_results.items()
                }
            }

            logger.info(
                f"Image OCR complete: {filename}, "
                f"confidence={confidence_metrics['overall_confidence']:.2f}%, "
                f"chars={len(cleaned_text)}, words={confidence_metrics['word_count']}"
            )

            return result

        except Exception as e:
            logger.error(f"Image OCR processing failed for {filename}: {e}", exc_info=True)
            raise

    def _analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        """
        Analyze image characteristics to optimize preprocessing.

        Args:
            image: PIL Image object

        Returns:
            dict: Image analysis results
        """
        try:
            # Convert to numpy array for analysis
            img_array = np.array(image)

            # Basic characteristics
            width, height = image.size
            is_grayscale = len(img_array.shape) == 2 or (len(img_array.shape) == 3 and img_array.shape[2] == 1)

            # Calculate image statistics
            if is_grayscale:
                mean_brightness = np.mean(img_array)
                contrast = np.std(img_array)
            else:
                # Convert to grayscale for analysis
                gray_array = np.mean(img_array, axis=2) if len(img_array.shape) == 3 else img_array
                mean_brightness = np.mean(gray_array)
                contrast = np.std(gray_array)

            # Determine image quality characteristics
            is_low_contrast = contrast < 30
            is_dark = mean_brightness < 100
            is_bright = mean_brightness > 200
            is_small = width < 500 or height < 500
            is_large = width > 3000 or height > 3000

            analysis = {
                'width': width,
                'height': height,
                'is_grayscale': is_grayscale,
                'mean_brightness': float(mean_brightness),
                'contrast': float(contrast),
                'is_low_contrast': is_low_contrast,
                'is_dark': is_dark,
                'is_bright': is_bright,
                'is_small': is_small,
                'is_large': is_large,
                'aspect_ratio': width / height,
                'resolution_category': self._categorize_resolution(width, height)
            }

            logger.debug(f"Image analysis: {analysis}")
            return analysis

        except Exception as e:
            logger.warning(f"Image analysis failed: {e}")
            return {
                'width': image.size[0],
                'height': image.size[1],
                'is_grayscale': False,
                'mean_brightness': 128,
                'contrast': 50,
                'is_low_contrast': False,
                'is_dark': False,
                'is_bright': False,
                'is_small': False,
                'is_large': False,
                'aspect_ratio': image.size[0] / image.size[1],
                'resolution_category': 'medium'
            }

    def _categorize_resolution(self, width: int, height: int) -> str:
        """Categorize image resolution for processing optimization"""
        total_pixels = width * height

        if total_pixels < 250000:  # < 500x500
            return 'low'
        elif total_pixels < 2000000:  # < ~1400x1400
            return 'medium'
        elif total_pixels < 8000000:  # < ~2800x2800
            return 'high'
        else:
            return 'very_high'

    def _advanced_preprocess_image(
        self,
        image: Image.Image,
        analysis: Dict[str, Any]
    ) -> Image.Image:
        """
        Apply advanced preprocessing based on image analysis.

        Args:
            image: Original PIL Image
            analysis: Image analysis results

        Returns:
            PIL Image: Preprocessed image optimized for OCR
        """
        try:
            processed = image.copy()

            # Convert to grayscale if not already
            if not analysis['is_grayscale']:
                processed = processed.convert('L')

            # Apply adaptive resizing
            processed = self._adaptive_resize(processed, analysis)

            # Apply contrast and brightness adjustments
            processed = self._enhance_contrast_brightness(processed, analysis)

            # Apply noise reduction if needed
            if analysis['is_low_contrast'] or analysis['resolution_category'] == 'low':
                processed = self._reduce_noise(processed)

            # Apply sharpening for better text definition
            processed = self._sharpen_image(processed, analysis)

            logger.debug(f"Applied preprocessing: final size {processed.size}")
            return processed

        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original: {e}")
            return image.convert('L') if image.mode != 'L' else image

    def _adaptive_resize(self, image: Image.Image, analysis: Dict[str, Any]) -> Image.Image:
        """Apply adaptive resizing based on image characteristics"""
        width, height = image.size

        # Define target size based on resolution category
        if analysis['resolution_category'] == 'low':
            # Upscale small images for better OCR
            min_dimension = 800
            if width < min_dimension or height < min_dimension:
                scale_factor = max(min_dimension / width, min_dimension / height)
                new_size = (int(width * scale_factor), int(height * scale_factor))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                logger.debug(f"Upscaled image to {new_size}")

        elif analysis['resolution_category'] == 'very_high':
            # Downscale very large images to improve processing speed
            max_dimension = 4000
            if width > max_dimension or height > max_dimension:
                scale_factor = min(max_dimension / width, max_dimension / height)
                new_size = (int(width * scale_factor), int(height * scale_factor))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                logger.debug(f"Downscaled image to {new_size}")

        return image

    def _enhance_contrast_brightness(
        self,
        image: Image.Image,
        analysis: Dict[str, Any]
    ) -> Image.Image:
        """Apply adaptive contrast and brightness enhancement"""
        try:
            # Apply contrast enhancement if low contrast
            if analysis['is_low_contrast']:
                enhancer = ImageEnhance.Contrast(image)
                contrast_factor = 1.5 if analysis['contrast'] < 20 else 1.2
                image = enhancer.enhance(contrast_factor)
                logger.debug(f"Applied contrast enhancement: factor {contrast_factor}")

            # Apply brightness adjustment if too dark or bright
            if analysis['is_dark']:
                enhancer = ImageEnhance.Brightness(image)
                brightness_factor = 1.3
                image = enhancer.enhance(brightness_factor)
                logger.debug(f"Applied brightness enhancement: factor {brightness_factor}")

            elif analysis['is_bright']:
                enhancer = ImageEnhance.Brightness(image)
                brightness_factor = 0.8
                image = enhancer.enhance(brightness_factor)
                logger.debug(f"Applied brightness reduction: factor {brightness_factor}")

            return image

        except Exception as e:
            logger.warning(f"Contrast/brightness enhancement failed: {e}")
            return image

    def _reduce_noise(self, image: Image.Image) -> Image.Image:
        """Apply noise reduction filters"""
        try:
            # Apply median filter to reduce salt-and-pepper noise
            filtered = image.filter(ImageFilter.MedianFilter(size=3))
            logger.debug("Applied noise reduction filter")
            return filtered
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return image

    def _sharpen_image(self, image: Image.Image, analysis: Dict[str, Any]) -> Image.Image:
        """Apply adaptive sharpening"""
        try:
            # Apply moderate sharpening for better text edges
            sharpening_factor = 1.0

            if analysis['is_low_contrast']:
                sharpening_factor = 1.5
            elif analysis['resolution_category'] == 'low':
                sharpening_factor = 1.2

            if sharpening_factor > 1.0:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(sharpening_factor)
                logger.debug(f"Applied sharpening: factor {sharpening_factor}")

            return image

        except Exception as e:
            logger.warning(f"Image sharpening failed: {e}")
            return image

    def _extract_with_multiple_methods(
        self,
        image: Image.Image,
        filename: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract text using multiple OCR configurations for best results.

        Args:
            image: Preprocessed PIL Image
            filename: Original filename

        Returns:
            dict: Results from different extraction methods
        """
        methods = {}

        # Method 1: Standard configuration (current implementation)
        try:
            standard_config = self._get_tesseract_config('standard')
            standard_result = self._extract_with_config(image, standard_config)
            methods['standard'] = standard_result
        except Exception as e:
            logger.warning(f"Standard OCR extraction failed: {e}")

        # Method 2: Enhanced configuration for documents
        try:
            document_config = self._get_tesseract_config('document')
            document_result = self._extract_with_config(image, document_config)
            methods['document'] = document_result
        except Exception as e:
            logger.warning(f"Document OCR extraction failed: {e}")

        # Method 3: Single-column configuration
        try:
            column_config = self._get_tesseract_config('single_column')
            column_result = self._extract_with_config(image, column_config)
            methods['single_column'] = column_result
        except Exception as e:
            logger.warning(f"Single column OCR extraction failed: {e}")

        if not methods:
            raise RuntimeError("All OCR extraction methods failed")

        return methods

    def _get_tesseract_config(self, method: str) -> str:
        """
        Get Tesseract configuration for different extraction methods.

        Args:
            method: Extraction method ('standard', 'document', 'single_column')

        Returns:
            str: Tesseract configuration string
        """
        base_config = r'--oem 3'

        if method == 'standard':
            # Current implementation: uniform block of text
            config = base_config + r' --psm 6'
        elif method == 'document':
            # Automatic page segmentation with orientation and script detection
            config = base_config + r' --psm 1'
        elif method == 'single_column':
            # Single uniform block of vertically aligned text
            config = base_config + r' --psm 4'
        else:
            config = base_config + r' --psm 6'  # default

        # Add character whitelist and spacing preservation
        config += r' -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
        config += r'-c preserve_interword_spaces=1'

        return config

    def _extract_with_config(self, image: Image.Image, config: str) -> Dict[str, Any]:
        """Extract text with specific Tesseract configuration"""
        # Extract text
        text = pytesseract.image_to_string(
            image,
            lang=self.settings.OCR_LANGUAGES,
            config=config
        )

        # Get confidence data
        data = pytesseract.image_to_data(
            image,
            lang=self.settings.OCR_LANGUAGES,
            config=config,
            output_type=pytesseract.Output.DICT
        )

        # Calculate metrics
        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        word_count = len([word for word in data['text'] if word.strip()])

        return {
            'text': text,
            'confidence': round(avg_confidence, 2),
            'word_count': word_count,
            'raw_data': data
        }

    def _select_best_extraction(
        self,
        extraction_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Select the best extraction result based on confidence and content quality.

        Args:
            extraction_results: Results from different methods

        Returns:
            dict: Best extraction result
        """
        if not extraction_results:
            raise ValueError("No extraction results to select from")

        # Score each result
        scored_results = []

        for method, result in extraction_results.items():
            score = self._calculate_extraction_score(result, method)
            scored_results.append((score, method, result))

        # Sort by score (descending) and select best
        scored_results.sort(reverse=True, key=lambda x: x[0])
        best_score, best_method, best_result = scored_results[0]

        logger.debug(f"Selected best extraction method: {best_method} (score: {best_score:.2f})")

        return best_result

    def _calculate_extraction_score(self, result: Dict[str, Any], method: str) -> float:
        """Calculate quality score for extraction result"""
        score = 0.0

        # Base score from confidence
        score += result['confidence'] * 0.4

        # Score from word count (more words generally better)
        word_count = result['word_count']
        if word_count > 0:
            score += min(word_count * 2, 40)  # Cap at 40 points

        # Score from text length
        text_length = len(result['text'].strip())
        if text_length > 0:
            score += min(text_length * 0.1, 20)  # Cap at 20 points

        # Method-specific bonuses
        method_bonuses = {
            'document': 5,  # Prefer document-optimized OCR
            'standard': 0,
            'single_column': 2
        }
        score += method_bonuses.get(method, 0)

        return score

    def _enhanced_clean_text(self, text: str) -> str:
        """
        Enhanced text cleaning specifically for OCR results.

        Args:
            text: Raw OCR text

        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""

        # Start with basic cleaning
        cleaned = text.strip()

        # Remove OCR artifacts and fix common issues
        cleaned = self._fix_ocr_artifacts(cleaned)

        # Normalize whitespace and line breaks
        lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
        cleaned = '\n'.join(lines)

        # Remove excessive spacing
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)

        return cleaned.strip()

    def _fix_ocr_artifacts(self, text: str) -> str:
        """Fix common OCR artifacts and misrecognitions"""
        # Fix common character misrecognitions
        corrections = {
            r'\b0\b': 'O',  # Zero to letter O in words
            r'\bO\b(?=\d)': '0',  # Letter O to zero before numbers
            r'\bl\b(?=\d)': '1',  # Letter l to number 1 before numbers
            r'rn\b': 'm',  # Common rn -> m misrecognition
            r'\bvv': 'w',  # Double v to w
            r'(?<=[a-z])l(?=[a-z])': 'I',  # Lowercase l to uppercase I in words
        }

        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text)

        # Remove isolated single characters that are likely artifacts
        text = re.sub(r'\b[^\w\s]\b', '', text)

        # Fix spacing issues around punctuation
        text = re.sub(r'\s+([.,:;!?])', r'\1', text)
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)

        return text

    def _calculate_confidence_metrics(
        self,
        extraction_results: Dict[str, Dict[str, Any]],
        final_text: str
    ) -> Dict[str, Any]:
        """Calculate comprehensive confidence metrics"""
        # Get best result confidence
        best_confidence = max(result['confidence'] for result in extraction_results.values())

        # Calculate consistency across methods
        all_confidences = [result['confidence'] for result in extraction_results.values()]
        confidence_std = np.std(all_confidences) if len(all_confidences) > 1 else 0

        # Calculate text quality indicators
        word_count = len(final_text.split()) if final_text else 0
        char_count = len(final_text)

        # Overall confidence based on multiple factors
        overall_confidence = best_confidence

        # Penalize if methods are inconsistent
        if confidence_std > 20:
            overall_confidence *= 0.9

        # Bonus for reasonable content length
        if word_count >= 5:
            overall_confidence = min(overall_confidence * 1.1, 100)

        return {
            'overall_confidence': round(overall_confidence, 2),
            'best_method_confidence': best_confidence,
            'confidence_std': round(confidence_std, 2),
            'word_count': word_count,
            'char_count': char_count,
            'methods_used': list(extraction_results.keys())
        }

    def _generate_image_metadata(
        self,
        original_image: Image.Image,
        processed_image: Image.Image,
        image_analysis: Dict[str, Any],
        filename: str
    ) -> Dict[str, Any]:
        """Generate comprehensive image metadata"""
        return {
            'filename': filename,
            'processing_timestamp': datetime.utcnow().isoformat(),
            'original_size': original_image.size,
            'processed_size': processed_image.size,
            'original_mode': original_image.mode,
            'processed_mode': processed_image.mode,
            'languages_used': self.settings.OCR_LANGUAGES,
            'image_analysis': image_analysis,
            'preprocessing_applied': {
                'resizing': original_image.size != processed_image.size,
                'contrast_enhancement': image_analysis['is_low_contrast'],
                'brightness_adjustment': image_analysis['is_dark'] or image_analysis['is_bright'],
                'noise_reduction': image_analysis['is_low_contrast'] or image_analysis['resolution_category'] == 'low',
                'sharpening': image_analysis['is_low_contrast'] or image_analysis['resolution_category'] == 'low'
            }
        }

    # Legacy compatibility methods

    def extract_text_from_image(self, image_content: bytes) -> str:
        """Legacy method for backward compatibility"""
        try:
            result = self.extract_text_with_metadata(image_content, "legacy_extraction")
            return result['text']
        except Exception as e:
            logger.error(f"Legacy image text extraction failed: {e}")
            return ""

    def get_supported_languages(self) -> List[str]:
        """Get list of supported OCR languages"""
        if not self.available:
            return []

        try:
            langs = pytesseract.get_languages(config='')
            logger.info(f"Available OCR languages: {langs}")
            return langs
        except Exception as e:
            logger.error(f"Failed to get supported languages: {e}")
            return []

    def is_available(self) -> bool:
        """Check if image processor is available"""
        return self.available

    def validate_image(self, image_content: bytes) -> Dict[str, Any]:
        """Validate image for OCR processing"""
        try:
            image = Image.open(io.BytesIO(image_content))
            analysis = self._analyze_image(image)

            # Determine if image is suitable for OCR
            is_suitable = (
                analysis['width'] >= 50 and
                analysis['height'] >= 50 and
                not (analysis['is_low_contrast'] and analysis['is_dark'])
            )

            return {
                'valid': True,
                'suitable_for_ocr': is_suitable,
                'image_analysis': analysis,
                'recommendations': self._get_processing_recommendations(analysis)
            }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'suitable_for_ocr': False
            }

    def _get_processing_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Get processing recommendations based on image analysis"""
        recommendations = []

        if analysis['is_small']:
            recommendations.append("Image resolution is low - consider using a higher resolution scan")

        if analysis['is_low_contrast']:
            recommendations.append("Low contrast detected - preprocessing will be applied")

        if analysis['is_dark']:
            recommendations.append("Dark image detected - brightness enhancement will be applied")

        if analysis['is_bright']:
            recommendations.append("Bright image detected - brightness reduction will be applied")

        if not recommendations:
            recommendations.append("Image appears suitable for OCR processing")

        return recommendations