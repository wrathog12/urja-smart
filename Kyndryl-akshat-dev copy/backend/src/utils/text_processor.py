from langchain_text_splitters import RecursiveCharacterTextSplitter
from configs.config import DocumentSettings
from typing import List, Dict, Any, Optional
from lib.logger import logger
import re


class TextChunker:
    """
    Enhanced utility for splitting text into chunks with improved algorithms.

    Maintains backward compatibility while providing enhanced chunking capabilities
    through integration with the Enhanced OCR Service's chunking logic.
    """

    def __init__(self):
        self.settings = DocumentSettings()

        # Legacy splitter (maintains backward compatibility)
        self.legacy_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.CHUNK_SIZE,  # 512
            chunk_overlap=self.settings.CHUNK_OVERLAP,  # 150
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        # Enhanced splitter with better separators for improved context preservation
        self.enhanced_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.CHUNK_SIZE,
            chunk_overlap=self.settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]
        )

        # Structured content splitter
        self.structured_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.CHUNK_SIZE,
            chunk_overlap=self.settings.CHUNK_OVERLAP // 2,  # Less overlap for structured content
            length_function=len,
            separators=["\n\n", "\n", "\t", " ", ""]
        )

        logger.info(
            f"Enhanced TextChunker initialized: "
            f"chunk_size={self.settings.CHUNK_SIZE}, "
            f"chunk_overlap={self.settings.CHUNK_OVERLAP}"
        )

    def chunk_text(self, text: str, enhanced: bool = False) -> List[str]:
        """
        Split text into chunks using recursive character splitter.

        Args:
            text: Input text to be chunked
            enhanced: Whether to use enhanced chunking algorithm (default: False for compatibility)

        Returns:
            List[str]: List of text chunks
        """
        if not text or not text.strip():
            logger.warning("Empty or whitespace-only text provided for chunking")
            return []

        if enhanced:
            # Use enhanced chunking with intelligent content analysis
            return self._enhanced_chunk_text(text)
        else:
            # Use legacy chunking for backward compatibility
            chunks = self.legacy_splitter.split_text(text)
            logger.info(f"Text split into {len(chunks)} chunks (legacy mode)")
            return chunks

    def _enhanced_chunk_text(self, text: str) -> List[str]:
        """
        Enhanced text chunking with intelligent content analysis.

        Args:
            text: Input text to be chunked

        Returns:
            List[str]: Enhanced text chunks with better boundaries
        """
        # Analyze text structure
        structure_analysis = self._analyze_text_structure(text)

        # Select appropriate splitter
        splitter = self._select_splitter(structure_analysis)

        # Pre-process text for better chunking
        processed_text = self._preprocess_text(text, structure_analysis)

        # Create chunks
        chunks = splitter.split_text(processed_text)

        # Post-process chunks for better boundaries
        enhanced_chunks = self._enhance_chunk_boundaries(chunks)

        logger.info(f"Enhanced text splitting complete: {len(enhanced_chunks)} chunks")
        logger.debug(f"Structure analysis: {structure_analysis}")

        return enhanced_chunks

    def _analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """Analyze text structure to optimize chunking strategy."""
        total_length = len(text)
        line_count = text.count('\n') + 1
        paragraph_count = len(re.split(r'\n\s*\n', text))

        # Detect structured content
        has_page_markers = bool(re.search(r'--- PAGE \d+ (STARTS|ENDS) ---', text))
        has_image_markers = bool(re.search(r'--- IMAGE .+ (STARTS|ENDS) ---', text))
        has_tables = self._detect_table_content(text)
        has_lists = self._detect_list_content(text)

        # Calculate content metrics
        lines = [line for line in text.split('\n') if line.strip()]
        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0

        return {
            'total_length': total_length,
            'line_count': line_count,
            'paragraph_count': paragraph_count,
            'avg_line_length': avg_line_length,
            'has_page_markers': has_page_markers,
            'has_image_markers': has_image_markers,
            'has_tables': has_tables,
            'has_lists': has_lists,
            'is_structured': has_tables or has_lists
        }

    def _detect_table_content(self, text: str) -> bool:
        """Detect if text contains table-like structures."""
        lines = text.split('\n')
        tab_lines = sum(1 for line in lines if '\t' in line or re.search(r'  {2,}', line))
        numeric_lines = sum(1 for line in lines if len(re.findall(r'\b\d+(?:\.\d+)?\b', line)) >= 3)

        total_lines = len([l for l in lines if l.strip()])
        return (tab_lines > total_lines * 0.2) or (numeric_lines > total_lines * 0.15)

    def _detect_list_content(self, text: str) -> bool:
        """Detect if text contains list-like structures."""
        lines = text.split('\n')
        list_patterns = [
            r'^\s*[•·▪▫-]\s+',  # Bullet points
            r'^\s*\d+[\.\)]\s+',  # Numbered lists
            r'^\s*[a-z][\.\)]\s+',  # Lettered lists
        ]

        list_lines = sum(1 for line in lines
                        if any(re.match(pattern, line, re.IGNORECASE)
                              for pattern in list_patterns))

        total_lines = len([l for l in lines if l.strip()])
        return list_lines > total_lines * 0.3

    def _select_splitter(self, analysis: Dict[str, Any]) -> RecursiveCharacterTextSplitter:
        """Select appropriate splitter based on text analysis."""
        if analysis['is_structured']:
            return self.structured_splitter
        else:
            return self.enhanced_splitter

    def _preprocess_text(self, text: str, analysis: Dict[str, Any]) -> str:
        """Preprocess text for optimal chunking."""
        processed = text

        # Preserve page markers with better spacing
        if analysis['has_page_markers']:
            processed = re.sub(r'(--- PAGE \d+ STARTS ---)', r'\n\1\n', processed)
            processed = re.sub(r'(--- PAGE \d+ ENDS ---)', r'\n\1\n', processed)

        # Preserve image markers
        if analysis['has_image_markers']:
            processed = re.sub(r'(--- IMAGE .+ STARTS ---)', r'\n\1\n', processed)
            processed = re.sub(r'(--- IMAGE .+ ENDS ---)', r'\n\1\n', processed)

        # Improve sentence boundary detection for better chunking
        processed = re.sub(r'([.!?])\s*([A-Z])', r'\1\n\n\2', processed)

        # Clean up excessive whitespace while preserving structure
        processed = re.sub(r'\n\s*\n\s*\n', '\n\n', processed)

        return processed

    def _enhance_chunk_boundaries(self, chunks: List[str]) -> List[str]:
        """Enhance chunk boundaries to preserve context and improve readability."""
        if not chunks:
            return chunks

        enhanced_chunks = []

        for chunk in chunks:
            # Clean up chunk boundaries
            enhanced_chunk = self._clean_chunk_boundaries(chunk)

            # Ensure minimum viable content
            if len(enhanced_chunk.strip()) >= 10:
                enhanced_chunks.append(enhanced_chunk)
            elif enhanced_chunks:
                # Merge very small chunks with previous chunk
                enhanced_chunks[-1] += "\n" + enhanced_chunk
            else:
                enhanced_chunks.append(enhanced_chunk)

        return enhanced_chunks

    def _clean_chunk_boundaries(self, chunk: str) -> str:
        """Clean up individual chunk boundaries."""
        cleaned = chunk.strip()

        # Remove incomplete sentences at the end if they're very short
        sentences = re.split(r'[.!?]+', cleaned)
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            # Remove the incomplete sentence
            cleaned = '.'.join(sentences[:-1]) + '.'
            cleaned = re.sub(r'\.+$', '.', cleaned)

        return cleaned

    # Enhanced methods for advanced use cases

    def chunk_with_metadata(self, text: str, **metadata) -> List[Dict[str, Any]]:
        """
        Chunk text and return chunks with metadata.

        Args:
            text: Input text to be chunked
            **metadata: Additional metadata to include with each chunk

        Returns:
            List[Dict[str, Any]]: List of chunks with metadata
        """
        chunks = self.chunk_text(text, enhanced=True)

        chunks_with_metadata = []
        for idx, chunk in enumerate(chunks):
            chunk_data = {
                'text': chunk,
                'chunk_index': idx,
                'total_chunks': len(chunks),
                'char_count': len(chunk),
                'word_count': len(chunk.split()),
                **metadata
            }
            chunks_with_metadata.append(chunk_data)

        return chunks_with_metadata

    def get_chunking_stats(self) -> Dict[str, Any]:
        """Get chunking configuration and statistics."""
        return {
            'chunk_size': self.settings.CHUNK_SIZE,
            'chunk_overlap': self.settings.CHUNK_OVERLAP,
            'legacy_separators': self.legacy_splitter._separators,
            'enhanced_separators': self.enhanced_splitter._separators,
            'structured_separators': self.structured_splitter._separators,
            'features': [
                'Backward compatibility with legacy chunking',
                'Enhanced chunking with better sentence boundaries',
                'Structured content detection and handling',
                'Context-aware boundary enhancement',
                'Metadata enrichment capabilities'
            ]
        }

    def validate_chunks(self, chunks: List[str]) -> Dict[str, Any]:
        """
        Validate chunk quality and provide metrics.

        Args:
            chunks: List of text chunks to validate

        Returns:
            Dict[str, Any]: Validation metrics and quality assessment
        """
        if not chunks:
            return {'valid': False, 'error': 'No chunks provided'}

        total_chunks = len(chunks)
        total_length = sum(len(chunk) for chunk in chunks)
        avg_chunk_size = total_length / total_chunks

        # Check for very small or very large chunks
        small_chunks = len([c for c in chunks if len(c) < 50])
        large_chunks = len([c for c in chunks if len(c) > self.settings.CHUNK_SIZE * 1.5])

        # Check for empty chunks
        empty_chunks = len([c for c in chunks if not c.strip()])

        quality_score = 100.0
        if small_chunks > total_chunks * 0.2:  # More than 20% small chunks
            quality_score -= 20
        if large_chunks > total_chunks * 0.1:  # More than 10% large chunks
            quality_score -= 15
        if empty_chunks > 0:
            quality_score -= 30

        return {
            'valid': True,
            'total_chunks': total_chunks,
            'total_length': total_length,
            'avg_chunk_size': round(avg_chunk_size, 2),
            'small_chunks': small_chunks,
            'large_chunks': large_chunks,
            'empty_chunks': empty_chunks,
            'quality_score': max(quality_score, 0),
            'quality_assessment': (
                'excellent' if quality_score >= 90 else
                'good' if quality_score >= 70 else
                'fair' if quality_score >= 50 else
                'poor'
            )
        }
