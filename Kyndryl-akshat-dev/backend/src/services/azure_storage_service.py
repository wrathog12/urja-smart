from azure.storage.blob import BlobServiceClient, ContentSettings, CorsRule, generate_blob_sas, BlobSasPermissions
from configs.config import AzureStorageSettings
from lib.logger import logger
from typing import Optional
from datetime import datetime, timedelta


class AzureStorageService:
    """Service for Azure Blob Storage operations"""

    def __init__(self):
        self.settings = AzureStorageSettings()
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.settings.AZURE_STORAGE_CONNECTION_STRING
            )
            self.container_name = self.settings.AZURE_STORAGE_CONTAINER_NAME

            # Extract account name and key for SAS token generation
            self._parse_connection_string()

            self._ensure_container_exists()
            self._configure_cors()
            logger.info(f"Azure Storage Service initialized: Container={self.container_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Storage Service: {e}", exc_info=True)
            raise

    def _parse_connection_string(self):
        """Parse connection string to extract account name and key for SAS token generation"""
        try:
            conn_str = self.settings.AZURE_STORAGE_CONNECTION_STRING
            parts = dict(part.split('=', 1) for part in conn_str.split(';') if '=' in part)
            self.account_name = parts.get('AccountName')
            self.account_key = parts.get('AccountKey')

            if not self.account_name or not self.account_key:
                raise ValueError("Could not extract AccountName or AccountKey from connection string")

            logger.info(f"Parsed Azure credentials for account: {self.account_name}")
        except Exception as e:
            logger.error(f"Failed to parse connection string: {e}", exc_info=True)
            raise

    def _ensure_container_exists(self):
        """Create container if it doesn't exist (private by default for security)"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                # Create PRIVATE container (no public access for security)
                container_client.create_container()
                logger.info(f"Created private container (SAS token access): {self.container_name}")
            else:
                logger.info(f"Container already exists (private): {self.container_name}")
        except Exception as e:
            logger.error(f"Error checking/creating container: {e}", exc_info=True)
            raise

    def _configure_cors(self):
        """Configure CORS settings for Azure Blob Storage to allow browser audio playback"""
        try:
            # Define CORS rule to allow all origins (for development)
            # In production, replace '*' with your specific frontend domain
            cors_rule = CorsRule(
                allowed_origins=['*'],  # Allow all origins
                allowed_methods=['GET', 'HEAD', 'OPTIONS'],
                allowed_headers=['*'],
                exposed_headers=['*'],
                max_age_in_seconds=3600
            )

            # Set CORS rules for the blob service
            self.blob_service_client.set_service_properties(cors=[cors_rule])
            logger.info("CORS configured successfully for Azure Blob Storage")

        except Exception as e:
            logger.warning(f"Failed to configure CORS (may require storage account permissions): {e}")
            logger.info("If audio playback fails, manually enable CORS in Azure Portal:")
            logger.info("  1. Go to Azure Portal > Storage Account > Resource Sharing (CORS)")
            logger.info("  2. Add rule: Origins=*, Methods=GET,HEAD,OPTIONS, Headers=*, Max age=3600")

    def _generate_sas_url(self, blob_name: str, expiry_hours: int = 1) -> str:
        """
        Generate a secure SAS (Shared Access Signature) URL for a blob

        Args:
            blob_name: Name of the blob
            expiry_hours: Number of hours until the URL expires (default: 1 hour)

        Returns:
            str: Secure signed URL with SAS token that expires after specified time

        Security features:
            - READ-ONLY access (no write/delete permissions)
            - Time-limited (expires after specified hours)
            - Blob-specific (not container-wide)
        """
        try:
            # Set expiry time
            start_time = datetime.utcnow()
            expiry_time = start_time + timedelta(hours=expiry_hours)

            # Generate SAS token with READ-ONLY permission
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),  # READ-ONLY for security
                expiry=expiry_time,
                start=start_time
            )

            # Construct full URL with SAS token
            blob_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"

            logger.info(f"Generated SAS URL for {blob_name} (expires in {expiry_hours}h)")
            return blob_url

        except Exception as e:
            logger.error(f"Failed to generate SAS URL for {blob_name}: {e}", exc_info=True)
            raise

    async def upload_blob(self, file_content: bytes, blob_name: str, expiry_hours: int = 24) -> str:
        """
        Upload file to Azure Blob Storage and return a secure SAS URL

        Args:
            file_content: File content as bytes
            blob_name: Name for the blob (e.g., "{document_id}_{filename}.pdf")
            expiry_hours: Hours until the SAS URL expires (default: 24 hours for PDFs)

        Returns:
            str: Secure signed URL with SAS token (read-only, time-limited)

        Security:
            - Container is PRIVATE (no public access)
            - Returns SAS URL with READ-ONLY permission
            - URL expires after specified hours (24h default for documents)
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            # Set content type for PDF
            content_settings = ContentSettings(content_type='application/pdf')

            # Upload the blob
            blob_client.upload_blob(
                file_content,
                overwrite=True,
                content_settings=content_settings
            )

            # Generate secure SAS URL (read-only, time-limited)
            sas_url = self._generate_sas_url(blob_name, expiry_hours=expiry_hours)

            logger.info(f"Blob uploaded with SAS: {blob_name}, Expires in {expiry_hours}h")
            return sas_url

        except Exception as e:
            logger.error(f"Failed to upload blob {blob_name}: {e}", exc_info=True)
            raise

    async def upload_audio_blob(self, audio_content: bytes, blob_name: str, expiry_hours: int = 2) -> str:
        """
        Upload audio file to Azure Blob Storage and return a secure SAS URL

        Args:
            audio_content: Audio content as bytes (MP3 format)
            blob_name: Name for the blob (e.g., "audio_{timestamp}.mp3")
            expiry_hours: Hours until the SAS URL expires (default: 2 hours)

        Returns:
            str: Secure signed URL with SAS token (read-only, time-limited)

        Security:
            - Container is PRIVATE (no public access)
            - Returns SAS URL with READ-ONLY permission
            - URL expires after specified hours
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            # Set content type for MP3 audio
            content_settings = ContentSettings(content_type='audio/mpeg')

            # Upload the audio blob
            blob_client.upload_blob(
                audio_content,
                overwrite=True,
                content_settings=content_settings
            )

            # Generate secure SAS URL (read-only, time-limited)
            sas_url = self._generate_sas_url(blob_name, expiry_hours=expiry_hours)

            logger.info(f"Audio blob uploaded with SAS: {blob_name}, Size={len(audio_content)} bytes, Expires in {expiry_hours}h")
            return sas_url

        except Exception as e:
            logger.error(f"Failed to upload audio blob {blob_name}: {e}", exc_info=True)
            raise

    async def get_blob_url(self, blob_name: str, expiry_hours: int = 1) -> Optional[str]:
        """
        Get secure SAS URL for a blob

        Args:
            blob_name: Name of the blob
            expiry_hours: Hours until the SAS URL expires (default: 1 hour)

        Returns:
            str: Secure signed URL with SAS token or None if not found

        Security:
            - Returns SAS URL with READ-ONLY permission
            - URL expires after specified hours
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            if blob_client.exists():
                # Return secure SAS URL instead of regular URL
                return self._generate_sas_url(blob_name, expiry_hours=expiry_hours)
            else:
                logger.warning(f"Blob not found: {blob_name}")
                return None

        except Exception as e:
            logger.error(f"Failed to get blob URL for {blob_name}: {e}", exc_info=True)
            return None

    async def download_blob(self, blob_name: str) -> Optional[bytes]:
        """
        Download blob content

        Args:
            blob_name: Name of the blob

        Returns:
            bytes: Blob content or None if not found
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            if blob_client.exists():
                download_stream = blob_client.download_blob()
                content = download_stream.readall()
                logger.info(f"Blob downloaded successfully: {blob_name}, Size={len(content)} bytes")
                return content
            else:
                logger.warning(f"Blob not found for download: {blob_name}")
                return None

        except Exception as e:
            logger.error(f"Failed to download blob {blob_name}: {e}", exc_info=True)
            return None

    async def delete_blob(self, blob_name: str) -> bool:
        """
        Delete blob from Azure Storage

        Args:
            blob_name: Name of the blob

        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            if blob_client.exists():
                blob_client.delete_blob()
                logger.info(f"Blob deleted successfully: {blob_name}")
                return True
            else:
                logger.warning(f"Blob not found for deletion: {blob_name}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete blob {blob_name}: {e}", exc_info=True)
            return False

    async def blob_exists(self, blob_name: str) -> bool:
        """
        Check if blob exists

        Args:
            blob_name: Name of the blob

        Returns:
            bool: True if exists, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            return blob_client.exists()

        except Exception as e:
            logger.error(f"Failed to check blob existence {blob_name}: {e}", exc_info=True)
            return False
