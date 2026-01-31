from fastapi import APIRouter, UploadFile, File, HTTPException
from services.azure_storage_service import AzureStorageService
from services.mongodb_service import MongoDBService
from services.ocr.enhanced_ocr_service import EnhancedOCRService
from services.rag_service import RAGService
from utils.file_handler import FileHandler
from models.db_models import DocumentMetadata
from schema.upload import UploadResponse
from configs.config import DocumentSettings
from lib.logger import logger
import uuid
from datetime import datetime
import os

router = APIRouter(prefix="/upload", tags=["Document Upload"])


@router.post("/", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF or image) for processing using Enhanced OCR Service

    Supported formats: PDF, JPG, JPEG, PNG

    Flow:
    1. Validate file type, MIME type, and size
    2. Generate UUID document_id
    3. Upload to Azure Blob Storage
    4. Process document with Enhanced OCR Service:
       - PDF: Advanced text extraction with enhanced metadata
       - Image: Multi-method OCR with confidence scoring
    5. Store embeddings in Qdrant
    6. Store metadata in MongoDB
    7. Return document_id and metadata

    Enhanced Features:
    - Improved text extraction quality
    - Better chunking with context preservation
    - Enhanced confidence scoring for OCR
    - Comprehensive processing metadata
    """
    document_id = None
    blob_name = None

    try:
        # Initialize services
        file_handler = FileHandler()
        azure_storage = AzureStorageService()
        mongodb_service = MongoDBService()
        enhanced_ocr_service = EnhancedOCRService()
        rag_service = RAGService()
        doc_settings = DocumentSettings()

        logger.info(f"Upload started with Enhanced OCR Service: {file.filename}")

        # Validate Enhanced OCR Service availability
        if not enhanced_ocr_service.is_available():
            logger.error("Enhanced OCR Service is not available")
            raise HTTPException(
                status_code=503,
                detail="OCR services are temporarily unavailable. Please try again later."
            )

        # Step 1: Validate file
        file_content = await file_handler.validate_file(file)
        file_size = len(file_content)

        # Step 2: Generate document_id
        document_id = str(uuid.uuid4())

        # Step 3: Upload to Azure Blob Storage
        blob_name = f"{document_id}_{file.filename}"
        blob_url = await azure_storage.upload_blob(file_content, blob_name)

        logger.info(f"File uploaded to Azure: {blob_name}")

        # Step 4: Determine file type and process with Enhanced OCR Service
        file_extension = os.path.splitext(file.filename or "")[1].lower()
        filename = file.filename or "unknown_file"

        if file_extension in doc_settings.IMAGE_EXTENSIONS:
            # Enhanced image OCR processing
            logger.info(f"Processing image file with Enhanced OCR Service: {filename}")

            # Process image with enhanced OCR
            chunks_with_metadata, total_pages, processing_type = enhanced_ocr_service.process_document(
                file_content=file_content,
                document_id=document_id,
                filename=filename,
                file_type='image'
            )

            # Validate processing results
            if not chunks_with_metadata:
                raise ValueError("No text could be extracted from the image or content is too short")

            # Log enhanced processing results
            avg_confidence = sum(
                chunk.get('ocr_confidence', 0) for chunk in chunks_with_metadata
            ) / len(chunks_with_metadata)

            logger.info(
                f"Enhanced OCR processing complete: {filename}, "
                f"chunks={len(chunks_with_metadata)}, "
                f"avg_confidence={avg_confidence:.2f}%"
            )

        else:
            # Enhanced PDF processing
            logger.info(f"Processing PDF file with Enhanced OCR Service: {filename}")

            # Process PDF with enhanced text extraction
            chunks_with_metadata, total_pages, processing_type = enhanced_ocr_service.process_document(
                file_content=file_content,
                document_id=document_id,
                filename=filename,
                file_type='pdf'
            )

            # Validate processing results
            if not chunks_with_metadata:
                raise ValueError("No text could be extracted from the PDF or content is too short")

            logger.info(
                f"Enhanced PDF processing complete: {filename}, "
                f"pages={total_pages}, chunks={len(chunks_with_metadata)}"
            )

        # Step 5: Generate embeddings and store in Qdrant
        rag_service.store_document_embeddings(chunks_with_metadata)

        logger.info(f"Embeddings stored in Qdrant: {len(chunks_with_metadata)} chunks")

        # Step 6: Store enhanced metadata in MongoDB (optional - disable if MongoDB not available)
        try:
            # Prepare enhanced metadata
            enhanced_metadata = DocumentMetadata(
                document_id=document_id,
                filename=filename,
                blob_url=blob_url,
                blob_name=blob_name,
                file_size=file_size,
                total_pages=total_pages,
                total_chunks=len(chunks_with_metadata),
                upload_timestamp=datetime.utcnow(),
                status="completed"
            )

            # Add processing-specific metadata
            if processing_type == 'ocr' and chunks_with_metadata:
                # Add OCR-specific metadata
                avg_confidence = sum(
                    chunk.get('ocr_confidence', 0) for chunk in chunks_with_metadata
                ) / len(chunks_with_metadata)

                enhanced_metadata.processing_metadata = {
                    'processing_type': processing_type,
                    'avg_ocr_confidence': round(avg_confidence, 2),
                    'enhanced_processing': True
                }
            else:
                enhanced_metadata.processing_metadata = {
                    'processing_type': processing_type,
                    'enhanced_processing': True
                }

            success = await mongodb_service.store_document_metadata(enhanced_metadata)

            if not success:
                logger.warning("Failed to store enhanced metadata in MongoDB, but processing completed")
        except Exception as mongo_error:
            logger.warning(f"MongoDB enhanced metadata storage skipped: {mongo_error}")

        # Get processing statistics for response
        processing_stats = enhanced_ocr_service.get_processing_statistics()

        logger.info(f"Enhanced document upload completed: {document_id}")

        # Step 7: Return enhanced response (maintaining API compatibility)
        response_message = (
            f"Document processed successfully with {len(chunks_with_metadata)} chunks "
            f"using Enhanced {processing_type.upper()} processing"
        )

        # Add confidence information for OCR processing
        if processing_type == 'ocr' and chunks_with_metadata:
            avg_confidence = sum(
                chunk.get('ocr_confidence', 0) for chunk in chunks_with_metadata
            ) / len(chunks_with_metadata)
            response_message += f" (avg confidence: {avg_confidence:.1f}%)"

        return UploadResponse(
            document_id=document_id,
            filename=filename,
            total_chunks=len(chunks_with_metadata),
            total_pages=total_pages,
            status="processing_complete",
            message=response_message,
            timestamp=datetime.utcnow().isoformat(),
            processing_type=processing_type
        )

    except ValueError as e:
        # Validation or processing error
        logger.error(f"Enhanced OCR validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Processing error - cleanup with enhanced logging
        logger.error(f"Enhanced OCR upload failed: {e}", exc_info=True)

        # Cleanup: Delete blob if it was created
        if blob_name:
            try:
                azure_storage = AzureStorageService()
                await azure_storage.delete_blob(blob_name)
                logger.info(f"Cleaned up blob after Enhanced OCR failure: {blob_name}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup blob: {cleanup_error}")

        # Cleanup: Delete MongoDB metadata if it was created
        if document_id:
            try:
                mongodb_service = MongoDBService()
                await mongodb_service.delete_document_metadata(document_id)
                logger.info(f"Cleaned up MongoDB metadata after Enhanced OCR failure: {document_id}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup MongoDB metadata: {cleanup_error}")

        raise HTTPException(
            status_code=500,
            detail=f"Enhanced OCR document processing failed: {str(e)}"
        )


@router.get("/status")
async def get_upload_service_status():
    """
    Get upload service status including Enhanced OCR Service availability
    """
    try:
        enhanced_ocr_service = EnhancedOCRService()
        processing_stats = enhanced_ocr_service.get_processing_statistics()

        return {
            "service_name": "Enhanced Document Upload Service",
            "status": "available" if enhanced_ocr_service.is_available() else "unavailable",
            "enhanced_ocr_service": processing_stats,
            "supported_formats": {
                "images": [".jpg", ".jpeg", ".png"],
                "documents": [".pdf"]
            },
            "features": [
                "Enhanced OCR with multiple extraction methods",
                "Advanced PDF text extraction with metadata",
                "Context-aware text chunking",
                "Confidence scoring and quality assessment",
                "Multi-language support",
                "Comprehensive processing metadata"
            ]
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "service_name": "Enhanced Document Upload Service",
            "status": "error",
            "error": str(e)
        }