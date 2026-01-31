"""
Enhanced Chunking Service

This service provides improved text chunking with better context preservation,
intelligent boundary detection, and enhanced metadata for the banking application.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re
from lib.logger import logger
from configs.config import DocumentSettings


class ChunkingService:
    """
    Enhanced chunking service with intelligent text splitting and context preservation.

    Features:
    - Context-aware chunk boundaries (preserves sentences and paragraphs)
    - Enhanced metadata with page tracking and content analysis
    - Quality assessment for each chunk
    - Support for different document types (PDF vs OCR)
    - Smart overlap calculation to maintain context
    """

    def __init__(self):
        """Initialize the enhanced chunking service"""
        self.settings = DocumentSettings()

        # Initialize multiple splitters for different content types
        self.document_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.CHUNK_SIZE,
            chunk_overlap=self.settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]
        )

        # Specialized splitter for tables and structured content
        self.structured_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.CHUNK_SIZE,
            chunk_overlap=self.settings.CHUNK_OVERLAP // 2,  # Less overlap for structured content
            length_function=len,
            separators=["\n\n", "\n", "\t", " ", ""]
        )

        logger.info(
            f"Enhanced Chunking Service initialized: "
            f"chunk_size={self.settings.CHUNK_SIZE}, "
            f"chunk_overlap={self.settings.CHUNK_OVERLAP}"
        )

    def create_chunks_with_metadata(
        self,
        text: str,
        document_id: str,
        filename: str,
        processing_type: str,
        total_pages: int = 1,
        page_metadata: Optional[List[Dict[str, Any]]] = None,
        ocr_confidence: Optional[float] = None,
        image_metadata: Optional[Dict[str, Any]] = None,
        legacy_format: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Create enhanced chunks with comprehensive metadata.

        Args:
            text: Text content to chunk
            document_id: Document UUID
            filename: Original filename
            processing_type: 'pdf' or 'ocr'
            total_pages: Total number of pages
            page_metadata: Per-page metadata for PDFs
            ocr_confidence: OCR confidence score for images
            image_metadata: Image processing metadata
            legacy_format: Whether to use legacy format for compatibility

        Returns:
            List[Dict]: List of chunks with enhanced metadata
        """
        try:
            if not text or not text.strip():
                logger.warning(f"Empty text content provided for chunking: {filename}")
                return []

            # Apply legacy format if requested (for backward compatibility)
            if legacy_format:
                return self._create_legacy_format_chunks(text, document_id, filename, processing_type)

            logger.info(f"Creating enhanced chunks: {filename}, type={processing_type}")

            # Analyze text structure
            text_analysis = self._analyze_text_structure(text)

            # Select appropriate splitter based on content
            splitter = self._select_splitter(text_analysis)

            # Pre-process text for better chunking
            processed_text = self._preprocess_for_chunking(text, text_analysis)

            # Create base chunks
            base_chunks = splitter.split_text(processed_text)

            # Enhance chunks with intelligent boundaries
            enhanced_chunks = self._enhance_chunk_boundaries(base_chunks, text_analysis)

            # Create comprehensive metadata for each chunk
            chunks_with_metadata = []
            timestamp = datetime.utcnow().isoformat()

            for idx, chunk in enumerate(enhanced_chunks):
                # Extract page information for this chunk
                page_info = self._extract_chunk_page_info(
                    chunk, page_metadata, processing_type, total_pages
                )

                # Analyze chunk content
                chunk_analysis = self._analyze_chunk_content(chunk)

                # Calculate chunk quality metrics
                quality_metrics = self._calculate_chunk_quality(
                    chunk, text_analysis, ocr_confidence
                )

                # Build comprehensive metadata
                chunk_metadata = {
                    'text': chunk,
                    'document_id': document_id,
                    'chunk_index': idx,
                    'total_chunks': len(enhanced_chunks),
                    'filename': filename,
                    'processing_type': processing_type,
                    'timestamp': timestamp,

                    # Page information
                    'page_number': page_info['page_number'],
                    'page_span': page_info['page_span'],
                    'starts_page': page_info['starts_page'],
                    'ends_page': page_info['ends_page'],

                    # Content analysis
                    'content_type': chunk_analysis['content_type'],
                    'has_numbers': chunk_analysis['has_numbers'],
                    'has_dates': chunk_analysis['has_dates'],
                    'language_detected': chunk_analysis['language_detected'],
                    'sentence_count': chunk_analysis['sentence_count'],
                    'word_count': chunk_analysis['word_count'],
                    'char_count': len(chunk),

                    # Quality metrics
                    'quality_score': quality_metrics['quality_score'],
                    'completeness_score': quality_metrics['completeness_score'],
                    'coherence_score': quality_metrics['coherence_score'],

                    # Processing-specific metadata
                    **(
                        {
                            'ocr_confidence': ocr_confidence,
                            'image_metadata': image_metadata
                        }
                        if processing_type == 'ocr' and ocr_confidence is not None
                        else {}
                    )
                }

                chunks_with_metadata.append(chunk_metadata)

            logger.info(f"Enhanced chunking complete: {len(chunks_with_metadata)} chunks created")

            return chunks_with_metadata

        except Exception as e:
            logger.error(f"Enhanced chunking failed for {filename}: {e}", exc_info=True)
            raise

    def _analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """
        Analyze text structure to optimize chunking strategy.

        Args:
            text: Input text

        Returns:
            dict: Text structure analysis
        """
        try:
            # Basic statistics
            total_length = len(text)
            line_count = text.count('\n') + 1
            paragraph_count = len(re.split(r'\n\s*\n', text))

            # Detect structured content
            has_page_markers = bool(re.search(r'--- PAGE \d+ (STARTS|ENDS) ---', text))
            has_image_markers = bool(re.search(r'--- IMAGE .+ (STARTS|ENDS) ---', text))

            # Detect table-like content
            has_tables = self._detect_table_content(text)

            # Detect list-like content
            has_lists = self._detect_list_content(text)

            # Calculate average line length
            lines = [line for line in text.split('\n') if line.strip()]
            avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0

            # Detect content density
            words = text.split()
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0

            analysis = {
                'total_length': total_length,
                'line_count': line_count,
                'paragraph_count': paragraph_count,
                'avg_line_length': avg_line_length,
                'avg_word_length': avg_word_length,
                'has_page_markers': has_page_markers,
                'has_image_markers': has_image_markers,
                'has_tables': has_tables,
                'has_lists': has_lists,
                'is_structured': has_tables or has_lists,
                'content_density': self._calculate_content_density(text)
            }

            logger.debug(f"Text structure analysis: {analysis}")
            return analysis

        except Exception as e:
            logger.warning(f"Text structure analysis failed: {e}")
            return {
                'total_length': len(text),
                'line_count': text.count('\n') + 1,
                'paragraph_count': 1,
                'avg_line_length': 50,
                'avg_word_length': 5,
                'has_page_markers': False,
                'has_image_markers': False,
                'has_tables': False,
                'has_lists': False,
                'is_structured': False,
                'content_density': 'medium'
            }

    def _detect_table_content(self, text: str) -> bool:
        """Detect if text contains table-like structures"""
        lines = text.split('\n')

        # Look for patterns indicating tables
        tab_lines = sum(1 for line in lines if '\t' in line or re.search(r'  {2,}', line))
        numeric_lines = sum(1 for line in lines if len(re.findall(r'\b\d+(?:\.\d+)?\b', line)) >= 3)

        total_lines = len([l for l in lines if l.strip()])
        return (tab_lines > total_lines * 0.2) or (numeric_lines > total_lines * 0.15)

    def _detect_list_content(self, text: str) -> bool:
        """Detect if text contains list-like structures"""
        lines = text.split('\n')

        # Look for bullet points, numbers, or other list indicators
        list_patterns = [
            r'^\s*[•·▪▫-]\s+',  # Bullet points
            r'^\s*\d+[\.\)]\s+',  # Numbered lists
            r'^\s*[a-z][\.\)]\s+',  # Lettered lists
            r'^\s*[ivxlc]+[\.\)]\s+',  # Roman numerals
        ]

        list_lines = 0
        for line in lines:
            if any(re.match(pattern, line, re.IGNORECASE) for pattern in list_patterns):
                list_lines += 1

        total_lines = len([l for l in lines if l.strip()])
        return list_lines > total_lines * 0.3

    def _calculate_content_density(self, text: str) -> str:
        """Calculate content density category"""
        words = text.split()
        if not words:
            return 'empty'

        # Calculate various density metrics
        avg_word_length = sum(len(word) for word in words) / len(words)
        punctuation_ratio = len(re.findall(r'[.!?;,:]', text)) / len(text)
        numeric_ratio = len(re.findall(r'\d', text)) / len(text)

        # Categorize density
        if avg_word_length > 6 and punctuation_ratio < 0.02:
            return 'high'  # Dense technical text
        elif avg_word_length < 4 and punctuation_ratio > 0.05:
            return 'low'   # Simple, punctuated text
        else:
            return 'medium'

    def _select_splitter(self, analysis: Dict[str, Any]) -> RecursiveCharacterTextSplitter:
        """Select appropriate splitter based on text analysis"""
        if analysis['is_structured']:
            logger.debug("Using structured content splitter")
            return self.structured_splitter
        else:
            logger.debug("Using standard document splitter")
            return self.document_splitter

    def _preprocess_for_chunking(self, text: str, analysis: Dict[str, Any]) -> str:
        """Preprocess text for optimal chunking"""
        processed = text

        # Preserve page markers by adding extra spacing
        if analysis['has_page_markers']:
            processed = re.sub(r'(--- PAGE \d+ STARTS ---)', r'\n\1\n', processed)
            processed = re.sub(r'(--- PAGE \d+ ENDS ---)', r'\n\1\n', processed)

        # Preserve image markers
        if analysis['has_image_markers']:
            processed = re.sub(r'(--- IMAGE .+ STARTS ---)', r'\n\1\n', processed)
            processed = re.sub(r'(--- IMAGE .+ ENDS ---)', r'\n\1\n', processed)

        # Improve sentence boundary detection
        processed = re.sub(r'([.!?])\s*([A-Z])', r'\1\n\n\2', processed)

        # Clean up excessive whitespace
        processed = re.sub(r'\n\s*\n\s*\n', '\n\n', processed)

        return processed

    def _enhance_chunk_boundaries(
        self,
        chunks: List[str],
        analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Enhance chunk boundaries to preserve context and improve readability.

        Args:
            chunks: Base chunks from splitter
            analysis: Text structure analysis

        Returns:
            List[str]: Enhanced chunks with better boundaries
        """
        if not chunks:
            return chunks

        enhanced_chunks = []

        for chunk in chunks:
            # Clean up chunk boundaries
            enhanced_chunk = self._clean_chunk_boundaries(chunk)

            # Ensure minimum viable content
            if len(enhanced_chunk.strip()) >= 10:  # Minimum 10 characters
                enhanced_chunks.append(enhanced_chunk)
            else:
                # Merge very small chunks with previous chunk
                if enhanced_chunks:
                    enhanced_chunks[-1] += "\n" + enhanced_chunk
                else:
                    enhanced_chunks.append(enhanced_chunk)

        return enhanced_chunks

    def _clean_chunk_boundaries(self, chunk: str) -> str:
        """Clean up individual chunk boundaries"""
        cleaned = chunk.strip()

        # Remove incomplete sentences at the end if they're very short
        sentences = re.split(r'[.!?]+', cleaned)
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            # Remove the incomplete sentence
            cleaned = '.'.join(sentences[:-1]) + '.'
            cleaned = re.sub(r'\.+$', '.', cleaned)

        return cleaned

    def _extract_chunk_page_info(
        self,
        chunk: str,
        page_metadata: Optional[List[Dict[str, Any]]],
        processing_type: str,
        total_pages: int
    ) -> Dict[str, Any]:
        """Extract page information for a chunk"""
        if processing_type == 'ocr':
            return {
                'page_number': 1,
                'page_span': [1],
                'starts_page': 1,
                'ends_page': 1
            }

        # Extract page numbers from page markers
        page_numbers = self._extract_page_numbers_from_chunk(chunk)

        if page_numbers:
            return {
                'page_number': min(page_numbers),  # Primary page (for legacy compatibility)
                'page_span': sorted(list(set(page_numbers))),
                'starts_page': min(page_numbers),
                'ends_page': max(page_numbers)
            }
        else:
            # Default to page 1 if no markers found
            return {
                'page_number': 1,
                'page_span': [1],
                'starts_page': 1,
                'ends_page': 1
            }

    def _extract_page_numbers_from_chunk(self, chunk: str) -> List[int]:
        """Extract page numbers from page markers in chunk"""
        page_numbers = []
        matches = re.findall(r'PAGE (\d+) STARTS', chunk)
        for match in matches:
            page_numbers.append(int(match))
        return page_numbers

    def _analyze_chunk_content(self, chunk: str) -> Dict[str, Any]:
        """Analyze chunk content characteristics"""
        # Detect content type
        content_type = self._detect_content_type(chunk)

        # Detect numbers, dates, and other patterns
        has_numbers = bool(re.search(r'\b\d+\b', chunk))
        has_dates = bool(re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', chunk))

        # Simple language detection (basic heuristic)
        language_detected = self._detect_chunk_language(chunk)

        # Count sentences and words
        sentences = re.split(r'[.!?]+', chunk)
        sentence_count = len([s for s in sentences if s.strip()])
        word_count = len(chunk.split())

        return {
            'content_type': content_type,
            'has_numbers': has_numbers,
            'has_dates': has_dates,
            'language_detected': language_detected,
            'sentence_count': sentence_count,
            'word_count': word_count
        }

    def _detect_content_type(self, chunk: str) -> str:
        """Detect the type of content in the chunk"""
        chunk_lower = chunk.lower()

        # Banking-specific content types
        if any(term in chunk_lower for term in ['account', 'balance', 'transaction', 'bank']):
            return 'banking'
        elif any(term in chunk_lower for term in ['table', '---', '\t']):
            return 'table'
        elif re.search(r'^\s*[•·▪▫-]', chunk, re.MULTILINE):
            return 'list'
        elif re.search(r'^\s*\d+[\.\)]', chunk, re.MULTILINE):
            return 'numbered_list'
        elif chunk.count('\n') < 2 and len(chunk) < 100:
            return 'header'
        else:
            return 'paragraph'

    def _detect_chunk_language(self, chunk: str) -> str:
        """Simple language detection for chunk"""
        # Count characters in different scripts
        devanagari_chars = len(re.findall(r'[\u0900-\u097F]', chunk))
        bengali_chars = len(re.findall(r'[\u0980-\u09FF]', chunk))
        tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', chunk))

        total_chars = len(re.findall(r'[a-zA-Z\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF]', chunk))

        if total_chars == 0:
            return 'unknown'

        # Simple heuristic based on character distribution
        if devanagari_chars / total_chars > 0.3:
            return 'hindi'
        elif bengali_chars / total_chars > 0.3:
            return 'bengali'
        elif tamil_chars / total_chars > 0.3:
            return 'tamil'
        else:
            return 'english'

    def _calculate_chunk_quality(
        self,
        chunk: str,
        text_analysis: Dict[str, Any],
        ocr_confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """Calculate quality metrics for the chunk"""
        # Base quality score
        quality_score = 80.0  # Start with good base score

        # Completeness score (based on sentence boundaries)
        completeness_score = self._calculate_completeness_score(chunk)

        # Coherence score (based on content flow)
        coherence_score = self._calculate_coherence_score(chunk)

        # Adjust quality based on OCR confidence
        if ocr_confidence is not None:
            quality_score = (quality_score + ocr_confidence) / 2

        # Penalize very short or very long chunks
        chunk_length = len(chunk)
        if chunk_length < 50:
            quality_score *= 0.8
        elif chunk_length > self.settings.CHUNK_SIZE * 1.5:
            quality_score *= 0.9

        return {
            'quality_score': round(min(quality_score, 100.0), 2),
            'completeness_score': round(completeness_score, 2),
            'coherence_score': round(coherence_score, 2)
        }

    def _calculate_completeness_score(self, chunk: str) -> float:
        """Calculate how complete the chunk is (sentence boundaries, etc.)"""
        if not chunk.strip():
            return 0.0

        # Check if chunk starts and ends with complete sentences
        starts_complete = bool(re.match(r'^[A-Z\d]', chunk.strip()))
        ends_complete = bool(re.search(r'[.!?]\s*$', chunk.strip()))

        score = 50.0  # Base score

        if starts_complete:
            score += 25.0
        if ends_complete:
            score += 25.0

        return score

    def _calculate_coherence_score(self, chunk: str) -> float:
        """Calculate how coherent the chunk content is"""
        if not chunk.strip():
            return 0.0

        score = 70.0  # Base coherence score

        # Bonus for proper paragraph structure
        if '\n\n' in chunk:
            score += 10.0

        # Penalty for broken words or incomplete thoughts
        if re.search(r'\b\w{1,2}\b', chunk):  # Very short words (might be artifacts)
            score -= 5.0

        # Bonus for consistent formatting
        lines = chunk.split('\n')
        if len(set(len(line) for line in lines if line.strip())) == 1:
            score += 5.0  # Consistent line lengths

        return min(score, 100.0)

    def _create_legacy_format_chunks(
        self,
        text: str,
        document_id: str,
        filename: str,
        processing_type: str
    ) -> List[Dict[str, Any]]:
        """Create chunks in legacy format for backward compatibility"""
        # Add appropriate markers
        if processing_type == 'ocr':
            marked_text = (
                f"\n--- IMAGE {filename} STARTS ---\n"
                f"{text.strip()}"
                f"\n--- IMAGE {filename} ENDS ---\n"
            )
        else:
            marked_text = text

        # Use simple splitter
        chunks = self.document_splitter.split_text(marked_text)
        timestamp = datetime.utcnow().isoformat()

        chunks_with_metadata = []
        for idx, chunk in enumerate(chunks):
            chunk_data = {
                'text': chunk,
                'document_id': document_id,
                'chunk_index': idx,
                'total_chunks': len(chunks),
                'filename': filename,
                'page_number': self._extract_page_number_legacy(chunk),
                'timestamp': timestamp
            }
            chunks_with_metadata.append(chunk_data)

        return chunks_with_metadata

    def _extract_page_number_legacy(self, chunk: str) -> int:
        """Extract page number using legacy method"""
        match = re.search(r'PAGE (\d+) STARTS', chunk)
        if match:
            return int(match.group(1))
        return 1  # Default for images

    def get_chunking_statistics(self) -> Dict[str, Any]:
        """Get chunking service statistics"""
        return {
            'service_name': 'Enhanced Chunking Service',
            'chunk_size': self.settings.CHUNK_SIZE,
            'chunk_overlap': self.settings.CHUNK_OVERLAP,
            'document_splitter_separators': self.document_splitter._separators,
            'structured_splitter_separators': self.structured_splitter._separators,
            'features': [
                'Context-aware boundaries',
                'Enhanced metadata',
                'Quality scoring',
                'Multi-language support',
                'Content type detection'
            ]
        }