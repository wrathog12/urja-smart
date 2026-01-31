"""
PDF Processor - Enhanced PDF Text Extraction

This module provides enhanced PDF text extraction with improved metadata,
better text cleaning, and structure preservation for the banking application.
"""

import fitz  # PyMuPDF
from typing import Dict, Any, List, Tuple
from datetime import datetime
from lib.logger import logger
import re


class PDFProcessor:
    """
    Enhanced PDF processor with improved text extraction and metadata handling.

    Features:
    - Better text cleaning and normalization
    - Enhanced metadata extraction
    - Structure-aware text processing
    - Improved error handling and logging
    """

    def __init__(self):
        """Initialize the PDF processor"""
        try:
            # Test PyMuPDF availability
            fitz.version
            self.available = True
            logger.info("PDF Processor initialized successfully")
        except Exception as e:
            logger.error(f"PDF Processor initialization failed: {e}")
            self.available = False

    def extract_text_with_metadata(
        self,
        pdf_content: bytes,
        filename: str
    ) -> Dict[str, Any]:
        """
        Extract text from PDF with comprehensive metadata.

        Args:
            pdf_content: PDF file content as bytes
            filename: Original filename

        Returns:
            dict: Contains extracted text, metadata, and page information
        """
        if not self.available:
            raise RuntimeError("PDF Processor is not available - PyMuPDF not properly configured")

        try:
            # Open PDF from memory
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            total_pages = len(pdf_document)

            logger.info(f"Processing PDF: {filename}, Pages={total_pages}")

            # Extract document metadata
            metadata = pdf_document.metadata

            # Process each page
            pages_data = []
            full_text_parts = []

            for page_num in range(total_pages):
                page = pdf_document[page_num]

                # Extract text with enhanced cleaning
                raw_page_text = page.get_text()
                cleaned_page_text = self._clean_text(raw_page_text)

                # Get page-specific metadata
                page_info = {
                    'page_number': page_num + 1,
                    'text_length': len(cleaned_page_text),
                    'has_images': len(page.get_images()) > 0,
                    'has_tables': self._detect_tables(cleaned_page_text),
                    'rect': page.rect,  # Page dimensions
                    'rotation': page.rotation
                }

                pages_data.append(page_info)

                # Add enhanced page markers for better context
                if cleaned_page_text.strip():
                    marked_text = self._format_page_content(
                        page_text=cleaned_page_text,
                        page_num=page_num + 1,
                        page_info=page_info
                    )
                    full_text_parts.append(marked_text)

            pdf_document.close()

            # Combine all text
            combined_text = "\n\n".join(full_text_parts)

            # Perform document-level text enhancement
            enhanced_text = self._enhance_document_text(combined_text)

            # Calculate document statistics
            document_stats = self._calculate_document_stats(enhanced_text, pages_data)

            result = {
                'text': enhanced_text,
                'total_pages': total_pages,
                'pages': pages_data,
                'metadata': {
                    'title': metadata.get('title', '').strip(),
                    'author': metadata.get('author', '').strip(),
                    'subject': metadata.get('subject', '').strip(),
                    'creator': metadata.get('creator', '').strip(),
                    'producer': metadata.get('producer', '').strip(),
                    'creation_date': metadata.get('creationDate', ''),
                    'modification_date': metadata.get('modDate', ''),
                    'filename': filename,
                    'processing_timestamp': datetime.utcnow().isoformat()
                },
                'statistics': document_stats
            }

            logger.info(
                f"PDF extraction complete: {filename}, "
                f"pages={total_pages}, chars={document_stats['total_characters']}, "
                f"words={document_stats['total_words']}"
            )

            return result

        except Exception as e:
            logger.error(f"PDF text extraction failed for {filename}: {e}", exc_info=True)
            raise

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.

        Args:
            text: Raw text from PDF

        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""

        # Remove excessive whitespace while preserving structure
        lines = [line.rstrip() for line in text.split('\n')]

        # Remove completely empty lines but preserve paragraph breaks
        cleaned_lines = []
        previous_empty = False

        for line in lines:
            if line.strip():
                cleaned_lines.append(line)
                previous_empty = False
            elif not previous_empty:  # Only add one empty line for paragraph breaks
                cleaned_lines.append("")
                previous_empty = True

        # Join and normalize spacing
        cleaned_text = '\n'.join(cleaned_lines)

        # Fix common PDF extraction issues
        cleaned_text = self._fix_pdf_artifacts(cleaned_text)

        return cleaned_text.strip()

    def _fix_pdf_artifacts(self, text: str) -> str:
        """
        Fix common PDF extraction artifacts.

        Args:
            text: Text with potential artifacts

        Returns:
            str: Text with artifacts corrected
        """
        # Fix hyphenated line breaks (common in justified text)
        text = re.sub(r'-\s*\n\s*', '', text)

        # Fix broken words across lines
        text = re.sub(r'(\w)\n(\w)', r'\1 \2', text)

        # Normalize multiple spaces (but preserve indentation)
        text = re.sub(r'[ \t]{2,}', ' ', text)

        # Fix bullet points and numbering artifacts
        text = re.sub(r'^\s*[•·▪▫]\s*', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*(\d+[\.\)])\s*', r'\1 ', text, flags=re.MULTILINE)

        # Remove form feed and other control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

        return text

    def _detect_tables(self, text: str) -> bool:
        """
        Detect if page contains table-like structures.

        Args:
            text: Page text

        Returns:
            bool: True if tables are detected
        """
        # Simple heuristic: look for patterns that suggest tabular data
        lines = text.split('\n')

        # Look for multiple lines with similar patterns of spaces/tabs
        tab_pattern_count = 0
        aligned_number_count = 0

        for line in lines:
            if line.strip():
                # Count tabs or multiple spaces (table separators)
                if re.search(r'\t|  {2,}', line):
                    tab_pattern_count += 1

                # Look for lines with multiple numbers (often indicates tables)
                numbers = re.findall(r'\b\d+(?:\.\d+)?\b', line)
                if len(numbers) >= 3:
                    aligned_number_count += 1

        # If significant portion of content looks tabular
        total_content_lines = len([l for l in lines if l.strip()])
        return (
            (tab_pattern_count > total_content_lines * 0.3) or
            (aligned_number_count > total_content_lines * 0.2)
        )

    def _format_page_content(
        self,
        page_text: str,
        page_num: int,
        page_info: Dict[str, Any]
    ) -> str:
        """
        Format page content with enhanced metadata markers.

        Args:
            page_text: Cleaned page text
            page_num: Page number (1-indexed)
            page_info: Page metadata

        Returns:
            str: Formatted page content with markers
        """
        # Create enhanced page header
        page_header_parts = [f"PAGE {page_num}"]

        if page_info['has_images']:
            page_header_parts.append("IMAGES")

        if page_info['has_tables']:
            page_header_parts.append("TABLES")

        page_header = " + ".join(page_header_parts)

        # Format the content
        formatted_content = (
            f"\n--- {page_header} STARTS ---\n"
            f"{page_text}"
            f"\n--- {page_header} ENDS ---\n"
        )

        return formatted_content

    def _enhance_document_text(self, text: str) -> str:
        """
        Perform document-level text enhancement.

        Args:
            text: Combined document text

        Returns:
            str: Enhanced document text
        """
        # Additional document-level cleaning
        enhanced = text

        # Normalize section headers and improve structure
        enhanced = re.sub(r'\n--- PAGE \d+.*?STARTS ---\n\s*\n', '\n--- PAGE \\g<0> ---\n\n', enhanced)

        # Ensure proper spacing around page markers
        enhanced = re.sub(r'\n--- PAGE.*?ENDS ---\n', '\\g<0>\n', enhanced)

        # Fix any remaining multiple blank lines
        enhanced = re.sub(r'\n\s*\n\s*\n', '\n\n', enhanced)

        return enhanced.strip()

    def _calculate_document_stats(
        self,
        text: str,
        pages_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive document statistics.

        Args:
            text: Full document text
            pages_data: Per-page metadata

        Returns:
            dict: Document statistics
        """
        # Basic text statistics
        total_characters = len(text)
        total_words = len(text.split()) if text else 0
        total_lines = text.count('\n') + 1 if text else 0

        # Page statistics
        pages_with_content = len([p for p in pages_data if p['text_length'] > 0])
        pages_with_images = len([p for p in pages_data if p['has_images']])
        pages_with_tables = len([p for p in pages_data if p['has_tables']])

        # Content analysis
        avg_words_per_page = total_words / len(pages_data) if pages_data else 0

        return {
            'total_characters': total_characters,
            'total_words': total_words,
            'total_lines': total_lines,
            'total_pages': len(pages_data),
            'pages_with_content': pages_with_content,
            'pages_with_images': pages_with_images,
            'pages_with_tables': pages_with_tables,
            'avg_words_per_page': round(avg_words_per_page, 2),
            'content_density': round(total_characters / len(pages_data), 2) if pages_data else 0
        }

    def extract_text_only(self, pdf_content: bytes) -> str:
        """
        Extract plain text from PDF without metadata (legacy compatibility).

        Args:
            pdf_content: PDF file content as bytes

        Returns:
            str: Extracted plain text
        """
        try:
            result = self.extract_text_with_metadata(pdf_content, "plain_extraction")
            return result['text']
        except Exception as e:
            logger.error(f"Plain text extraction failed: {e}")
            raise

    def get_document_info(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Get document information without full text extraction.

        Args:
            pdf_content: PDF file content as bytes

        Returns:
            dict: Document information and metadata
        """
        if not self.available:
            raise RuntimeError("PDF Processor is not available")

        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")

            info = {
                'total_pages': len(pdf_document),
                'metadata': pdf_document.metadata,
                'encrypted': pdf_document.is_encrypted,
                'pdf_version': pdf_document.pdf_version(),
                'page_count': pdf_document.page_count
            }

            pdf_document.close()
            return info

        except Exception as e:
            logger.error(f"Document info extraction failed: {e}")
            raise

    def is_available(self) -> bool:
        """
        Check if PDF processor is available.

        Returns:
            bool: True if PyMuPDF is properly configured
        """
        return self.available

    def validate_pdf(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Validate PDF file and check for processing issues.

        Args:
            pdf_content: PDF file content as bytes

        Returns:
            dict: Validation results
        """
        if not self.available:
            return {
                'valid': False,
                'error': 'PDF processor not available',
                'can_process': False
            }

        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")

            validation = {
                'valid': True,
                'can_process': True,
                'total_pages': len(pdf_document),
                'encrypted': pdf_document.is_encrypted,
                'password_required': pdf_document.needs_pass,
                'pdf_version': pdf_document.pdf_version(),
                'has_text_content': False
            }

            # Check if document has extractable text
            sample_pages = min(3, len(pdf_document))  # Check first 3 pages
            for page_num in range(sample_pages):
                page = pdf_document[page_num]
                if len(page.get_text().strip()) > 50:  # Reasonable text content
                    validation['has_text_content'] = True
                    break

            pdf_document.close()

            return validation

        except Exception as e:
            logger.error(f"PDF validation failed: {e}")
            return {
                'valid': False,
                'error': str(e),
                'can_process': False
            }