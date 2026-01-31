"""
Enhanced OCR Service - Main Orchestrator

This service consolidates and enhances the existing OCR and document processing functionality
into a unified interface, providing improved processing capabilities while maintaining
compatibility with the existing API.
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import uuid
from lib.logger import logger
from configs.config import DocumentSettings

from .pdf_processor import PDFProcessor
from .image_processor import ImageProcessor
from .chunking_service import ChunkingService


class EnhancedOCRService:
    """
    Enhanced OCR Service that orchestrates document processing for both PDF and image files.

    This service replaces the existing OCRService and DocumentProcessor classes while
    maintaining API compatibility and providing enhanced functionality.
    """

    def __init__(self):
        """Initialize the enhanced OCR service with all processors"""
        self.settings = DocumentSettings()

        # Initialize specialized processors
        self.pdf_processor = PDFProcessor()
        self.image_processor = ImageProcessor()
        self.chunking_service = ChunkingService()

        logger.info("Enhanced OCR Service initialized with all processors")

    def process_document(
        self,
        file_content: bytes,
        document_id: str,
        filename: str,
        file_type: str
    ) -> Tuple[List[Dict], int, str]:
        """
        Main document processing method that handles both PDF and image files.

        Args:
            file_content: Raw file content as bytes
            document_id: UUID for the document
            filename: Original filename
            file_type: File type ('pdf' or 'image')

        Returns:
            tuple: (chunks_with_metadata, total_pages, processing_type)
        """
        try:
            if file_type.lower() == 'pdf':
                return self._process_pdf_document(file_content, document_id, filename)
            else:
                return self._process_image_document(file_content, document_id, filename)

        except Exception as e:
            logger.error(f"Document processing failed for {filename}: {e}", exc_info=True)
            raise

    def _process_pdf_document(
        self,
        file_content: bytes,
        document_id: str,
        filename: str
    ) -> Tuple[List[Dict], int, str]:
        """
        Process PDF documents with enhanced text extraction.

        Args:
            file_content: PDF file content as bytes
            document_id: UUID for the document
            filename: Original filename

        Returns:
            tuple: (chunks_with_metadata, total_pages, 'pdf')
        """
        try:
            logger.info(f"Processing PDF document: {filename}")

            # Extract text and metadata using specialized PDF processor
            extraction_result = self.pdf_processor.extract_text_with_metadata(
                file_content, filename
            )

            total_pages = extraction_result['total_pages']
            extracted_text = extraction_result['text']
            page_metadata = extraction_result['pages']

            # Enhanced chunking with context preservation
            chunks_with_metadata = self.chunking_service.create_chunks_with_metadata(
                text=extracted_text,
                document_id=document_id,
                filename=filename,
                processing_type='pdf',
                total_pages=total_pages,
                page_metadata=page_metadata
            )

            logger.info(
                f"PDF processing complete: {filename}, "
                f"pages={total_pages}, chunks={len(chunks_with_metadata)}"
            )

            return chunks_with_metadata, total_pages, 'pdf'

        except Exception as e:
            logger.error(f"PDF processing failed for {filename}: {e}", exc_info=True)
            raise

    def _process_image_document(
        self,
        file_content: bytes,
        document_id: str,
        filename: str
    ) -> Tuple[List[Dict], int, str]:
        """
        Process image documents with enhanced OCR.

        Args:
            file_content: Image file content as bytes
            document_id: UUID for the document
            filename: Original filename

        Returns:
            tuple: (chunks_with_metadata, 1, 'ocr')
        """
        try:
            logger.info(f"Processing image document: {filename}")

            # Extract text using enhanced image processor
            extraction_result = self.image_processor.extract_text_with_metadata(
                file_content, filename
            )

            extracted_text = extraction_result['text']
            confidence = extraction_result['confidence']
            image_metadata = extraction_result['metadata']

            # Enhanced chunking with OCR-specific metadata
            chunks_with_metadata = self.chunking_service.create_chunks_with_metadata(
                text=extracted_text,
                document_id=document_id,
                filename=filename,
                processing_type='ocr',
                total_pages=1,
                ocr_confidence=confidence,
                image_metadata=image_metadata
            )

            logger.info(
                f"Image OCR processing complete: {filename}, "
                f"confidence={confidence:.2f}%, chunks={len(chunks_with_metadata)}"
            )

            return chunks_with_metadata, 1, 'ocr'

        except Exception as e:
            logger.error(f"Image OCR processing failed for {filename}: {e}", exc_info=True)
            raise

    # Legacy compatibility methods to maintain existing API

    def extract_text_from_image(self, image_content: bytes) -> str:
        """
        Legacy method for backward compatibility with existing OCRService.

        Args:
            image_content: Raw image bytes

        Returns:
            str: Extracted text
        """
        try:
            result = self.image_processor.extract_text_with_metadata(image_content, "legacy_image")
            return result['text']
        except Exception as e:
            logger.error(f"Legacy image text extraction failed: {e}")
            return ""

    def extract_text_with_confidence(self, image_content: bytes) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility with existing OCRService.

        Args:
            image_content: Raw image bytes

        Returns:
            dict: Contains 'text', 'confidence', 'word_count', etc.
        """
        try:
            result = self.image_processor.extract_text_with_metadata(image_content, "legacy_image")

            # Convert to legacy format
            return {
                "text": result['text'],
                "confidence": result['confidence'],
                "word_count": result.get('word_count', 0),
                "image_size": result['metadata'].get('image_size'),
                "languages_used": result['metadata'].get('languages_used', self.settings.OCR_LANGUAGES)
            }
        except Exception as e:
            logger.error(f"Legacy confidence extraction failed: {e}")
            return {"text": "", "confidence": 0, "word_count": 0, "error": str(e)}

    def process_pdf(
        self,
        blob_content: bytes,
        document_id: str,
        filename: str
    ) -> Tuple[List[Dict], int]:
        """
        Legacy method for backward compatibility with existing DocumentProcessor.

        Args:
            blob_content: PDF file content as bytes
            document_id: UUID for the document
            filename: Original filename

        Returns:
            tuple: (List of chunk dictionaries with metadata, total_pages)
        """
        try:
            chunks, total_pages, _ = self._process_pdf_document(blob_content, document_id, filename)
            return chunks, total_pages
        except Exception as e:
            logger.error(f"Legacy PDF processing failed for {filename}: {e}")
            raise

    def process_ocr_text(
        self,
        extracted_text: str,
        document_id: str,
        filename: str
    ) -> List[Dict]:
        """
        Legacy method for backward compatibility with existing DocumentProcessor.

        Args:
            extracted_text: Text extracted from image via OCR
            document_id: UUID for the document
            filename: Original filename

        Returns:
            List[Dict]: List of chunk dictionaries with metadata
        """
        try:
            # Use chunking service with legacy text format
            chunks_with_metadata = self.chunking_service.create_chunks_with_metadata(
                text=extracted_text,
                document_id=document_id,
                filename=filename,
                processing_type='ocr',
                total_pages=1,
                legacy_format=True
            )

            return chunks_with_metadata
        except Exception as e:
            logger.error(f"Legacy OCR text processing failed for {filename}: {e}")
            raise

    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Get processing statistics and service health information.

        Returns:
            dict: Service statistics and health info
        """
        return {
            "service_name": "Enhanced OCR Service",
            "pdf_processor_available": self.pdf_processor.is_available(),
            "image_processor_available": self.image_processor.is_available(),
            "supported_languages": self.image_processor.get_supported_languages(),
            "chunk_size": self.settings.CHUNK_SIZE,
            "chunk_overlap": self.settings.CHUNK_OVERLAP,
            "ocr_languages": self.settings.OCR_LANGUAGES
        }

    def is_available(self) -> bool:
        """
        Check if the enhanced OCR service is available.

        Returns:
            bool: True if all processors are available
        """
        return (
            self.pdf_processor.is_available() and
            self.image_processor.is_available()
        )

    def validate_processing_quality(
        self,
        chunks_with_metadata: List[Dict],
        processing_type: str
    ) -> Dict[str, Any]:
        """
        Validate the quality of processed chunks.

        Args:
            chunks_with_metadata: List of processed chunks
            processing_type: Type of processing ('pdf' or 'ocr')

        Returns:
            dict: Quality metrics and validation results
        """
        try:
            total_chunks = len(chunks_with_metadata)

            if total_chunks == 0:
                return {
                    "valid": False,
                    "error": "No chunks generated",
                    "total_chunks": 0
                }

            # Calculate quality metrics
            total_text_length = sum(len(chunk['text']) for chunk in chunks_with_metadata)
            avg_chunk_size = total_text_length / total_chunks if total_chunks > 0 else 0

            # OCR-specific quality checks
            if processing_type == 'ocr':
                avg_confidence = sum(
                    chunk.get('ocr_confidence', 0)
                    for chunk in chunks_with_metadata
                ) / total_chunks

                quality_threshold = getattr(self.settings, 'OCR_CONFIDENCE_THRESHOLD', 50.0)
                high_quality = avg_confidence >= quality_threshold
            else:
                avg_confidence = None
                high_quality = True  # PDF text extraction is typically reliable

            return {
                "valid": True,
                "total_chunks": total_chunks,
                "total_text_length": total_text_length,
                "avg_chunk_size": avg_chunk_size,
                "processing_type": processing_type,
                "avg_confidence": avg_confidence,
                "high_quality": high_quality
            }

        except Exception as e:
            logger.error(f"Quality validation failed: {e}")
            return {
                "valid": False,
                "error": str(e),
                "total_chunks": len(chunks_with_metadata) if chunks_with_metadata else 0
            }