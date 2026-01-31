from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Distance,
    VectorParams
)
from services.qdrant_host import current_qdrant_client
from configs.config import QdrantSettings, AzureOpenAISettings
from typing import List, Dict, Optional
from lib.logger import logger
import uuid


class QdrantService:
    """Service for Qdrant vector database operations"""

    def __init__(self):
        self.client = current_qdrant_client
        self.qdrant_settings = QdrantSettings()
        self.azure_settings = AzureOpenAISettings()
        self.collection_name = self.qdrant_settings.QDRANT_COLLECTION_NAME
        self._ensure_collection_exists()
        logger.info(f"Qdrant Service initialized: Collection={self.collection_name}")

    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_exists = any(col.name == self.collection_name for col in collections)

            if not collection_exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.azure_settings.EMBEDDING_DIMENSION,  # 3072
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")

                # Create payload index for efficient filtering by document_id
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="document_id",
                    field_schema="keyword"
                )
                logger.info(f"Created payload index on document_id")

            else:
                logger.info(f"Qdrant collection already exists: {self.collection_name}")

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}", exc_info=True)
            raise

    def store_chunks(self, chunks_with_metadata: List[Dict], embeddings: List[List[float]]):
        """
        Store document chunks with embeddings in Qdrant.
        Uploads in batches of 100 points.

        Args:
            chunks_with_metadata: List of chunk dictionaries with metadata
            embeddings: List of 3072-dimensional embeddings
        """
        if len(chunks_with_metadata) != len(embeddings):
            raise ValueError(
                f"Mismatch between chunks ({len(chunks_with_metadata)}) "
                f"and embeddings ({len(embeddings)})"
            )

        points = []

        for chunk_data, embedding in zip(chunks_with_metadata, embeddings):
            point = PointStruct(
                id=str(uuid.uuid4()),
                payload={
                    "text": chunk_data['text'],
                    "document_id": chunk_data['document_id'],
                    "chunk_index": chunk_data['chunk_index'],
                    "total_chunks": chunk_data['total_chunks'],
                    "filename": chunk_data['filename'],
                    "page_number": chunk_data.get('page_number', 0),
                    "timestamp": chunk_data['timestamp']
                },
                vector=embedding
            )
            points.append(point)

        # Upload in batches of 100
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            logger.info(f"Uploaded batch {i//batch_size + 1}: {len(batch)} points")

        logger.info(f"Total points stored in Qdrant: {len(points)}")

    def search_similar_chunks(
        self,
        query_embedding: List[float],
        document_id: Optional[str] = None,
        limit: int = 30,
        score_threshold: float = 0.1
    ) -> List[Dict]:
        """
        Semantic search in Qdrant

        Args:
            query_embedding: Query vector (3072-dimensional)
            document_id: Optional filter by specific document
            limit: Top K results to return
            score_threshold: Minimum similarity score

        Returns:
            List[Dict]: List of matching chunks with metadata
        """
        try:
            # Build filter for document_id if provided
            query_filter = None
            if document_id:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
                logger.info(f"Searching with filter: document_id={document_id}")

            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold
            )

            # Format results
            results = []
            for hit in search_result:
                results.append({
                    "text": hit.payload["text"],
                    "document_id": hit.payload["document_id"],
                    "filename": hit.payload["filename"],
                    "chunk_index": hit.payload["chunk_index"],
                    "page_number": hit.payload.get("page_number", 0),
                    "score": hit.score
                })

            logger.info(
                f"Search completed: Found {len(results)} results "
                f"(limit={limit}, threshold={score_threshold})"
            )
            return results

        except Exception as e:
            logger.error(f"Failed to search Qdrant: {e}", exc_info=True)
            raise

    def delete_by_document_id(self, document_id: str) -> bool:
        """
        Delete all chunks for a specific document

        Args:
            document_id: UUID of the document

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
            )
            logger.info(f"Deleted all chunks for document_id={document_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete chunks for document_id={document_id}: {e}", exc_info=True)
            return False

    def get_collection_info(self) -> Dict:
        """
        Get collection information

        Returns:
            Dict: Collection info including point count
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "points_count": info.points_count,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance
            }

        except Exception as e:
            logger.error(f"Failed to get collection info: {e}", exc_info=True)
            return {}
