from typing import List, Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field, validator

class Entity(BaseModel):
    """Named entity model."""
    text: str = Field(..., description="The entity text")
    label: str = Field(..., description="The entity label/type")

class ChartCharacteristics(BaseModel):
    """Chart characteristics model."""
    has_lines: bool = Field(..., description="Whether the chart contains lines")
    has_shapes: bool = Field(..., description="Whether the chart contains shapes")
    regular_patterns: bool = Field(..., description="Whether the chart contains regular patterns")

class ChartInfo(BaseModel):
    """Chart information model."""
    image_path: str = Field(..., description="Path to the chart image")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score of chart detection")
    characteristics: ChartCharacteristics
    type: str = Field(..., description="Type of the chart")

class DocumentBase(BaseModel):
    """Base document model."""
    id: int = Field(..., description="Document ID")
    content: str = Field(..., description="Document content")
    entities: List[Entity] = Field(default_factory=list, description="Named entities found in the document")
    keywords: List[str] = Field(default_factory=list, description="Keywords extracted from the document")

class DocumentResponse(DocumentBase):
    """Document response model."""
    charts: List[ChartInfo] = Field(default_factory=list, description="Charts found in the document")
    
    @validator('charts', pre=True)
    def ensure_charts_list(cls, v):
        """Ensure charts is always a list."""
        if v is None:
            return []
        return v

class SearchQuery(BaseModel):
    """Search query model."""
    query: str = Field(..., min_length=1, description="Search query string")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Maximum number of results to return")

class SearchResult(DocumentBase):
    """Search result model."""
    rank: float = Field(..., description="Search result ranking score")
    charts: List[ChartInfo] = Field(default_factory=list, description="Charts in the document")