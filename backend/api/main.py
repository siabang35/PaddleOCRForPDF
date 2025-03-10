from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from .models import SearchQuery, DocumentResponse, SearchResult
from .db import document_repository
from typing import List
from pydantic import BaseModel

# Create FastAPI application
app = FastAPI(
    title="Research Paper Analysis API",
    description="API for accessing and searching research paper analysis results",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Research Paper Analysis API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get(
    "/documents/{doc_id}",
    response_model=DocumentResponse,
    responses={
        404: {"description": "Document not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_document_by_id(doc_id: int):
    """
    Retrieve a document and its associated charts by ID.
    
    Args:
        doc_id: The ID of the document to retrieve
        
    Returns:
        DocumentResponse: The document and its associated data
        
    Raises:
        HTTPException: If document is not found or server error occurs
    """
    try:
        document = document_repository.get_document(doc_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {doc_id} not found"
            )
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

class SearchRequest(BaseModel):
    query: str
    limit: int = 10  # Default limit

@app.post("/search", response_model=List[dict])
def search_documents(request: SearchRequest):
    """Search documents in database using full-text search."""
    results = document_repository.search_documents(request.query, request.limit)
    if not results:
        return []
    return results
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)