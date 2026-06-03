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

class ParameterDependencyMatrix(BaseModel):
    """
    Defines an explicit transactional target link where a detected dynamic candidate 
    is reused in subsequent outgoing requests.
    """
    candidate: CorrelationCandidate = Field(..., description="The source metadata configuration model mapping origin.")
    target_sampler_id: str = Field(..., description="Chronological tracker index string identifying the destination sampler.")
    target_sampler_name: str = Field(..., description="Verbatim tracking label identifier name of target sampler.")
    target_location: HttpLocation = Field(..., description="HTTP pipeline segment location matching target reuse.")
    target_parameter_key: Optional[str] = Field(default=None, description="The specific parameter key matching value reuse fields.")
    usage_context_snippet: str = Field(..., description="Text segment snippet capturing contextual reuse conditions.")

class GeneratedExtractorConfig(BaseModel):
    """
    Holds the complete code-generation parameters required to construct
    and inject an extraction component node into the JMX syntax tree.
    """
    variable_name: str = Field(..., description="Target variable reference names handle.")
    extractor_type: ExtractorType = Field(..., description="Structural plugin extractor type categorization.")
    target_field: HttpLocation = Field(..., description="The context region inside the sampler response to extract from.")
    expression: str = Field(..., description="The calculated search query path or matching expression syntax pattern.")
    template: str = Field(default="$1$", description="The grouping extraction reference format string.")
    match_number: int = Field(default=1, description="The specific match instance index tracking offset.")
    default_fallback: str = Field(default="NOT_FOUND", description="Fallback value returned if lookup checks fail.")