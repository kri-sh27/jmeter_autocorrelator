"""
Tracking Domain Models.
Defines execution record models capturing runtime transactional traffic details.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class SampleResultRecord(BaseModel):
    """
    Captures exhaustive transactional metric state and payload snapshots
    extracted sequentially from underlying log streams.
    """
    elapsed_ms: int = Field(..., description="Total execution time delta for the sampler.")
    response_code: str = Field(default="200", description="HTTP Status response code string.")
    response_message: str = Field(default="OK", description="HTTP status message context.")
    thread_name: str = Field(..., description="Origin execution thread path name tag.")
    data_type: str = Field(default="text", description="Payload encoding type identifier classification.")
    success: bool = Field(default=True, description="Indicates if assertion checkpoints passed cleanly.")
    bytes_received: int = Field(default=0, description="Payload network transport sizing footprints metrics.")
    sample_label: str = Field(..., description="Verbatim tracking name label matching source JMX sampler.")
    
    # Payload Snapshots
    request_headers: Dict[str, str] = Field(default_factory=dict, description="Mapped outgoing transport headers parsed.")
    response_headers: Dict[str, str] = Field(default_factory=dict, description="Mapped incoming server traffic configuration metrics.")
    request_body: str = Field(default="", description="Literal payload block passed down outbound pipeline channels.")
    response_body: str = Field(default="", description="Raw literal string content block fetched from target server responses.")
    cookies: Dict[str, str] = Field(default_factory=dict, description="Extracted transactional runtime state cookies map.")