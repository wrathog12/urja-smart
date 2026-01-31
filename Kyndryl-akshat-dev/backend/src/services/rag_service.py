from services.embedding_service import EmbeddingService
from services.qdrant_service import QdrantService
from services.llm_service import LLMService
from services.bhashini_service import BhashiniTranslationService
from services.sentiment_service import SentimentService
from utils.language_detector import LanguageDetector
from typing import List, Dict, Optional, Tuple
from lib.logger import logger


class RAGService:
    """RAG pipeline orchestration service with multi-language support and sentiment awareness"""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
        self.llm_service = LLMService()
        self.translation_service = BhashiniTranslationService()
        self.language_detector = LanguageDetector()
        self.sentiment_service = SentimentService()
        logger.info("RAG Service initialized with multi-language support and sentiment analysis")

    def store_document_embeddings(self, chunks_with_metadata: List[Dict]):
        """
        Generate embeddings for document chunks and store in Qdrant

        Args:
            chunks_with_metadata: List of chunk dictionaries with metadata
        """
        try:
            logger.info(f"Generating embeddings for {len(chunks_with_metadata)} chunks")

            # Extract text from chunks
            texts = [chunk['text'] for chunk in chunks_with_metadata]

            # Generate embeddings in batches
            embeddings = self.embedding_service.generate_embeddings(texts)

            # Store in Qdrant
            self.qdrant_service.store_chunks(chunks_with_metadata, embeddings)

            logger.info(f"Successfully stored {len(embeddings)} embeddings in Qdrant")

        except Exception as e:
            logger.error(f"Failed to store document embeddings: {e}", exc_info=True)
            raise

    def query_with_rag(self, user_query: str, document_id: Optional[str] = None) -> Tuple[str, str, Dict]:
        """
        RAG pipeline for queries with document context, multi-language support, and sentiment awareness

        Steps:
        1. Analyze sentiment of user query
        2. Detect user query language
        3. Translate query to English if needed
        4. Generate query embedding
        5. Search Qdrant (with optional document filter)
        6. Format context from retrieved chunks
        7. Send to LLM with sentiment-aware context
        8. Translate response back to user's language
        9. Return response

        Args:
            user_query: User's question
            document_id: Optional document ID to filter by

        Returns:
            Tuple[str, str, Dict]: (AI-generated response, detected language code, sentiment data)
        """
        try:
            logger.info(f"Processing RAG query: '{user_query[:50]}...'")

            # Step 1: Analyze sentiment
            sentiment_data = self.sentiment_service.analyze_sentiment(user_query)
            logger.info(f"Sentiment: {sentiment_data['sentiment']} (confidence: {sentiment_data['confidence']:.2f})")

            # Step 2: Detect language
            detected_language = self.language_detector.detect_language(user_query)
            language_name = self.language_detector.get_language_name(detected_language)
            logger.info(f"Detected language: {language_name} ({detected_language})")

            # Step 2: Translate to English if needed
            english_query = user_query
            if detected_language != 'en':
                logger.info(f"Translating query from {detected_language} to English")
                translated = self.translation_service.translate(user_query, detected_language, 'en')
                if translated:
                    english_query = translated
                    logger.info(f"Translated query: '{english_query[:50]}...'")

            # Step 3: Generate query embedding
            query_embedding = self.embedding_service.generate_single_embedding(english_query)

            # Step 4: Retrieve relevant chunks
            retrieved_chunks = self.qdrant_service.search_similar_chunks(
                query_embedding=query_embedding,
                document_id=document_id,
                limit=30,
                score_threshold=0.1
            )

            if not retrieved_chunks:
                logger.warning("No relevant information found in documents")
                no_info_message = "I couldn't find relevant information in the documents to answer your question. Please try rephrasing or ask a different question."

                # Translate "no info" message if needed
                if detected_language != 'en':
                    translated_message = self.translation_service.translate(no_info_message, 'en', detected_language)
                    if translated_message:
                        no_info_message = translated_message

                return no_info_message, detected_language, sentiment_data

            # Step 5: Format context
            context = self._format_context(retrieved_chunks)

            # Step 6: Generate sentiment-aware response in English
            english_response = self.llm_service.generate_response_with_context(
                query=english_query,
                context=context,
                sentiment_data=sentiment_data
            )

            # Step 7: Translate response back to user's language
            final_response = english_response
            if detected_language != 'en':
                logger.info(f"Translating response from English to {detected_language}")
                translated_response = self.translation_service.translate(english_response, 'en', detected_language)
                if translated_response:
                    final_response = translated_response
                    logger.info(f"Translated response: '{final_response[:50]}...'")

            logger.info(f"RAG query completed successfully. Used {len(retrieved_chunks)} chunks, Language: {detected_language}, Sentiment: {sentiment_data['sentiment']}")
            return final_response, detected_language, sentiment_data

        except Exception as e:
            logger.error(f"Failed to process RAG query: {e}", exc_info=True)
            raise

    def query_without_rag(self, user_query: str) -> Tuple[str, str, Dict]:
        """
        Direct LLM query for general banking questions with multi-language support and sentiment awareness

        Steps:
        1. Analyze sentiment of user query
        2. Detect user query language
        3. Translate query to English if needed
        4. Send to LLM with sentiment-aware prompt
        5. Translate response back to user's language
        6. Return response

        Args:
            user_query: User's banking question

        Returns:
            Tuple[str, str, Dict]: (AI-generated response, detected language code, sentiment data)
        """
        try:
            logger.info(f"Processing general banking query: '{user_query[:50]}...'")

            # Step 1: Analyze sentiment
            sentiment_data = self.sentiment_service.analyze_sentiment(user_query)
            logger.info(f"Sentiment: {sentiment_data['sentiment']} (confidence: {sentiment_data['confidence']:.2f})")

            # Step 2: Detect language
            detected_language = self.language_detector.detect_language(user_query)
            language_name = self.language_detector.get_language_name(detected_language)
            logger.info(f"Detected language: {language_name} ({detected_language})")

            # Step 2: Translate to English if needed
            english_query = user_query
            if detected_language != 'en':
                logger.info(f"Translating query from {detected_language} to English")
                translated = self.translation_service.translate(user_query, detected_language, 'en')
                if translated:
                    english_query = translated
                    logger.info(f"Translated query: '{english_query[:50]}...'")

            # Step 3: Generate sentiment-aware response in English
            english_response = self.llm_service.generate_banking_response(
                english_query,
                sentiment_data=sentiment_data
            )

            # Step 4: Translate response back to user's language
            final_response = english_response
            if detected_language != 'en':
                logger.info(f"Translating response from English to {detected_language}")
                translated_response = self.translation_service.translate(english_response, 'en', detected_language)
                if translated_response:
                    final_response = translated_response
                    logger.info(f"Translated response: '{final_response[:50]}...'")

            logger.info(f"General banking query completed successfully. Language: {detected_language}, Sentiment: {sentiment_data['sentiment']}")
            return final_response, detected_language, sentiment_data

        except Exception as e:
            logger.error(f"Failed to process general query: {e}", exc_info=True)
            raise

    def _format_context(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into context string

        Args:
            chunks: List of chunk dictionaries with metadata

        Returns:
            str: Formatted context string
        """
        context_parts = []

        for idx, chunk in enumerate(chunks, 1):
            context_part = (
                f"[Document: {chunk['filename']}, "
                f"Page: {chunk['page_number']}, "
                f"Relevance Score: {chunk['score']:.3f}]\n"
                f"{chunk['text']}\n"
            )
            context_parts.append(context_part)

        formatted_context = "\n---\n".join(context_parts)
        logger.info(f"Formatted context from {len(chunks)} chunks")

        return formatted_context
