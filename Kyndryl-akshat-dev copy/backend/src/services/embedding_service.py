from openai import AzureOpenAI
from configs.config import AzureOpenAISettings
from typing import List
from lib.logger import logger


class EmbeddingService:
    """Service for generating embeddings using Azure OpenAI"""

    def __init__(self):
        self.settings = AzureOpenAISettings()
        self.client = AzureOpenAI(
            api_key=self.settings.AZURE_OPENAI_API_KEY,
            api_version=self.settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT
        )
        logger.info(
            f"Embedding Service initialized: "
            f"Model={self.settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}, "
            f"Dimension={self.settings.EMBEDDING_DIMENSION}"
        )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        Azure OpenAI has a limit of 16 texts per batch.

        Args:
            texts: List of text strings to embed

        Returns:
            List[List[float]]: List of 3072-dimensional embeddings
        """
        embeddings = []
        batch_size = 16  # Azure OpenAI limit

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]

            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
                )

                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

                logger.info(f"Generated embeddings for batch {i//batch_size + 1}: {len(batch)} texts")

            except Exception as e:
                logger.error(f"Failed to generate embeddings for batch {i//batch_size + 1}: {e}", exc_info=True)
                raise

        logger.info(f"Total embeddings generated: {len(embeddings)}")
        return embeddings

    def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text (query)

        Args:
            text: Text string to embed

        Returns:
            List[float]: 3072-dimensional embedding
        """
        try:
            response = self.client.embeddings.create(
                input=[text],
                model=self.settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
            )

            embedding = response.data[0].embedding
            logger.info(f"Generated single embedding: dimension={len(embedding)}")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate single embedding: {e}", exc_info=True)
            raise
