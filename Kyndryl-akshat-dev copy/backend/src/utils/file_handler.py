from fastapi import UploadFile
from configs.config import DocumentSettings
from lib.logger import logger
from PIL import Image
import io


class FileHandler:
    """Utility for file validation"""

    def __init__(self):
        self.settings = DocumentSettings()

    async def validate_file(self, upload_file: UploadFile) -> bytes:
        """
        Validate uploaded file for type, MIME type, and size

        Args:
            upload_file: FastAPI UploadFile object

        Returns:
            bytes: File content if valid

        Raises:
            ValueError: If file is invalid
        """
        # Read file content
        contents = await upload_file.read()

        # Validate file size
        file_size = len(contents)
        if file_size > self.settings.MAX_FILE_SIZE:
            raise ValueError(
                f"File size ({file_size} bytes) exceeds maximum allowed size "
                f"({self.settings.MAX_FILE_SIZE} bytes = {self.settings.MAX_FILE_SIZE / (1024*1024):.1f} MB)"
            )

        # Validate file extension
        filename = upload_file.filename or ""
        file_extension = filename[filename.rfind('.'):] if '.' in filename else ""

        if file_extension.lower() not in self.settings.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File type '{file_extension}' not allowed. "
                f"Allowed types: {', '.join(self.settings.ALLOWED_EXTENSIONS)}"
            )

        # Validate MIME type
        content_type = upload_file.content_type or ""
        valid_mime_types = [
            "application/pdf",          # PDF files
            "image/jpeg",               # JPEG images
            "image/jpg",                # JPG images (alternative)
            "image/png",                # PNG images
        ]

        if content_type not in valid_mime_types:
            raise ValueError(
                f"Invalid MIME type '{content_type}'. Supported types: PDF (application/pdf), "
                f"JPEG (image/jpeg), PNG (image/png)"
            )

        # Additional validation for image files
        if content_type.startswith("image/"):
            try:
                # Verify the file is a valid image by trying to open it with PIL
                image = Image.open(io.BytesIO(contents))
                image.verify()  # Verify it's a valid image

                # Check image dimensions (basic sanity check)
                # Re-open since verify() closes the image
                image = Image.open(io.BytesIO(contents))
                width, height = image.size

                if width < 10 or height < 10:
                    raise ValueError(f"Image dimensions too small: {width}x{height}. Minimum 10x10 pixels required.")

                if width > 10000 or height > 10000:
                    raise ValueError(f"Image dimensions too large: {width}x{height}. Maximum 10000x10000 pixels allowed.")

                logger.info(f"Image validation successful: {width}x{height} pixels, Format: {image.format}")

            except Exception as e:
                if "Image dimensions" in str(e):
                    raise  # Re-raise dimension validation errors
                raise ValueError(f"Invalid image file: {str(e)}")

        logger.info(
            f"File validation successful: {filename}, "
            f"Size={file_size} bytes, Type={content_type}"
        )

        return contents

    async def validate_audio_file(self, upload_file: UploadFile) -> tuple[bytes, str]:
        """
        Validate uploaded audio file for STT processing

        Args:
            upload_file: FastAPI UploadFile object

        Returns:
            tuple: (File content as bytes, audio format)

        Raises:
            ValueError: If audio file is invalid
        """
        # Read file content
        contents = await upload_file.read()

        # Validate file size (more lenient for audio - up to 50MB)
        max_audio_size = 50 * 1024 * 1024  # 50MB
        file_size = len(contents)
        if file_size > max_audio_size:
            raise ValueError(
                f"Audio file size ({file_size} bytes) exceeds maximum allowed size "
                f"({max_audio_size} bytes = {max_audio_size / (1024*1024):.1f} MB)"
            )

        if file_size < 100:  # Very small file, probably not valid audio
            raise ValueError("Audio file is too small to contain valid audio data")

        # Validate file extension
        filename = upload_file.filename or ""
        file_extension = filename[filename.rfind('.'):] if '.' in filename else ""

        supported_audio_extensions = [".wav", ".mp3", ".ogg", ".webm", ".m4a", ".flac"]

        if file_extension.lower() not in supported_audio_extensions:
            raise ValueError(
                f"Audio file type '{file_extension}' not supported. "
                f"Supported types: {', '.join(supported_audio_extensions)}"
            )

        # Validate MIME type
        content_type = upload_file.content_type or ""
        supported_audio_mime_types = [
            "audio/wav",
            "audio/wave",
            "audio/x-wav",
            "audio/mpeg",
            "audio/mp3",
            "audio/ogg",
            "audio/webm",
            "audio/x-m4a",
            "audio/flac",
            "audio/x-flac"
        ]

        if content_type and content_type not in supported_audio_mime_types:
            logger.warning(f"Unusual audio MIME type: {content_type}, proceeding with validation")

        # Determine audio format from extension
        audio_format = file_extension.lower().lstrip('.')
        if audio_format == "m4a":
            audio_format = "mp4"  # pydub uses mp4 for m4a files

        logger.info(
            f"Audio file validation successful: {filename}, "
            f"Size={file_size} bytes, Type={content_type}, Format={audio_format}"
        )

        return contents, audio_format
