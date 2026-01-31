from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response schema for document upload"""
    document_id: str = Field(..., description="Unique document identifier (UUID)")
    filename: str = Field(..., description="Original filename")
    total_chunks: int = Field(..., description="Number of chunks generated")
    total_pages: int = Field(..., description="Total pages in PDF")
    status: str = Field(default="processing_complete", description="Processing status")
    message: str = Field(..., description="Success message")
    timestamp: str = Field(..., description="Upload timestamp (ISO format)")
    processing_type: str = Field(..., description="Processing type: 'pdf' or 'ocr'")


class DocumentListResponse(BaseModel):
    """Response schema for listing documents"""
    documents: list
    total: int = Field(..., description="Total number of documents")
