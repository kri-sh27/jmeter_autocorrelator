"""
Dynamic Core Data Models.
Tracks extracted parameters across transaction matrices with strict metadata.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from src.core.constants import CorrelationType, ExtractorType, HttpLocation

class CorrelationCandidate(BaseModel):
    """
    Identifies a raw extracted dynamic parameter model mapping candidate context.
    """
    parameter_name: str = Field(..., description="The calculated programmatic runtime variable handle.")
    extracted_value: str = Field(..., description="Raw underlying payload sample string scanned.")
    source_sampler_id: str = Field(..., description="UUID or internal tag reference index tracking source.")
    source_sampler_name: str = Field(..., description="Verbatim human-readable string identifier of origin sampler.")
    location: HttpLocation = Field(..., description="HTTP pipeline location component.")
    correlation_type: CorrelationType = Field(..., description="Classification category mapping pattern behaviors.")
    extractor_type: ExtractorType = Field(..., description="The calculated targeting extraction component tool.")
    extraction_expression: str = Field(..., description="Valid runtime processing search pattern rule string.")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Algorithmic reliability validation evaluation scale.")
    meta_properties: Dict[str, Any] = Field(default_factory=dict, description="Open-ended tracking parameters block.")