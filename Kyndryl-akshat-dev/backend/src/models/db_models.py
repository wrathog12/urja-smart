from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DocumentMetadata(BaseModel):
    """MongoDB document metadata model"""
    document_id: str = Field(..., description="Unique UUID for document")
    filename: str = Field(..., description="Original filename")
    blob_url: str = Field(..., description="Azure Blob Storage URL")
    blob_name: str = Field(..., description="Blob name in container")
    file_size: int = Field(..., description="File size in bytes")
    total_pages: int = Field(..., description="Total pages in PDF")
    total_chunks: int = Field(..., description="Total chunks generated")
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Upload time")
    status: str = Field(default="completed", description="processing_complete or failed")
