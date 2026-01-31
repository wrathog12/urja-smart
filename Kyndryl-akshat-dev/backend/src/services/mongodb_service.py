from motor.motor_asyncio import AsyncIOMotorClient
from configs.config import DocumentDB
from models.db_models import DocumentMetadata
from typing import List, Optional
from lib.logger import logger


class MongoDBService:
    """Service for MongoDB operations on document metadata"""

    def __init__(self):
        self.settings = DocumentDB()
        self.client = AsyncIOMotorClient(self.settings.DOCUMENT_DB_CONNECTION_STRING)
        self.db = self.client[self.settings.DATABASE_NAME]
        self.collection = self.db[self.settings.COLLECTION_NAME]
        logger.info(f"MongoDB Service initialized: Database={self.settings.DATABASE_NAME}, Collection={self.settings.COLLECTION_NAME}")

    async def store_document_metadata(self, metadata: DocumentMetadata) -> bool:
        """
        Store document metadata in MongoDB

        Args:
            metadata: DocumentMetadata object

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            document_dict = metadata.model_dump()
            result = await self.collection.insert_one(document_dict)
            logger.info(f"Document metadata stored: document_id={metadata.document_id}, mongo_id={result.inserted_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store document metadata: {e}", exc_info=True)
            return False

    async def get_document_metadata(self, document_id: str) -> Optional[DocumentMetadata]:
        """
        Retrieve document metadata by document_id

        Args:
            document_id: UUID string

        Returns:
            DocumentMetadata object or None if not found
        """
        try:
            document = await self.collection.find_one({"document_id": document_id})
            if document:
                # Remove MongoDB's _id field before creating Pydantic model
                document.pop('_id', None)
                return DocumentMetadata(**document)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve document metadata: {e}", exc_info=True)
            return None

    async def list_all_documents(self, limit: int = 100, skip: int = 0) -> List[DocumentMetadata]:
        """
        List all documents with pagination

        Args:
            limit: Maximum number of documents to return
            skip: Number of documents to skip

        Returns:
            List of DocumentMetadata objects
        """
        try:
            cursor = self.collection.find().sort("upload_timestamp", -1).skip(skip).limit(limit)
            documents = []
            async for doc in cursor:
                doc.pop('_id', None)
                documents.append(DocumentMetadata(**doc))
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Failed to list documents: {e}", exc_info=True)
            return []

    async def delete_document_metadata(self, document_id: str) -> bool:
        """
        Delete document metadata by document_id

        Args:
            document_id: UUID string

        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            result = await self.collection.delete_one({"document_id": document_id})
            if result.deleted_count > 0:
                logger.info(f"Document metadata deleted: document_id={document_id}")
                return True
            else:
                logger.warning(f"Document not found for deletion: document_id={document_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete document metadata: {e}", exc_info=True)
            return False

    async def update_document_status(self, document_id: str, status: str) -> bool:
        """
        Update document status

        Args:
            document_id: UUID string
            status: New status (e.g., 'completed', 'failed')

        Returns:
            bool: True if updated, False otherwise
        """
        try:
            result = await self.collection.update_one(
                {"document_id": document_id},
                {"$set": {"status": status}}
            )
            if result.modified_count > 0:
                logger.info(f"Document status updated: document_id={document_id}, status={status}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update document status: {e}", exc_info=True)
            return False
