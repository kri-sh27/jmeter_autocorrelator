"""
Sampler Domain Model.
Defines structured object representations of parsed JMX samplers and configurations.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class HttpArgument(BaseModel):
    """Represents a key-value parameter within an HTTP Sampler."""
    name: str = Field(..., description="The parameter query key or form data name.")
    value: str = Field(..., description="The value assigned to the argument parameter.")
    metadata: str = Field(default="=", description="The argument metadata delimiter.")
    use_equals: bool = Field(default=True, description="Indicates if an equality sign is present.")

class HeaderEntry(BaseModel):
    """Represents a header key-value pair from Header Managers."""
    name: str = Field(..., description="The HTTP header field name (e.g., Content-Type).")
    value: str = Field(..., description="The value string for the target header field.")

class CookieEntry(BaseModel):
    """Represents a predefined cookie item from Cookie Managers."""
    name: str = Field(..., description="The cookie key identifier name.")
    value: str = Field(..., description="The cookie value sequence payload.")
    domain: str = Field(default="", description="The specific structural target server domain.")
    path: str = Field(default="", description="The web application path matching domain context.")
    secure: bool = Field(default=False, description="Specifies SSL transport level flag requirement.")

class JmeterSamplerContext(BaseModel):
    """
    Unified execution-sequence-mapped entity capturing the precise state 
    and configurations of an HTTP sampler wrapper extracted from JMX DOM trees.
    """
    sampler_id: str = Field(..., description="The distinct positional layout or GUID string of the sampler element.")
    sampler_name: str = Field(..., description="The human-readable title given to the target testing sampler.")
    domain: str = Field(default="", description="The remote web host server address parsed.")
    port: str = Field(default="", description="The web application listener port parsed.")
    protocol: str = Field(default="http", description="The communication transport standard (http/https).")
    path: str = Field(default="", description="The target request application path endpoint string.")
    method: str = Field(default="GET", description="The target HTTP request verb command type used.")
    follow_redirects: bool = Field(default=True)
    auto_redirects: bool = Field(default=False)
    use_keepalive: bool = Field(default=True)
    post_body_raw: Optional[str] = Field(default=None, description="The full literal continuous raw string payload body.")
    arguments: List[HttpArgument] = Field(default_factory=list, description="Collection of form data parsed elements.")
    headers: List[HeaderEntry] = Field(default_factory=list, description="Aggregated scoped header options applied.")
    cookies: List[CookieEntry] = Field(default_factory=list, description="Aggregated scoped cookie definitions applied.")
    parent_controller_name: str = Field(default="Thread Group", description="Context thread group layout or controller string path.")
    execution_order_index: int = Field(..., description="Explicit chronological relative position execution index scale.")

class JmeterExecutionSummary(BaseModel):
    """
    Holds execution statistics parsed from the headless execution run.
    """
    total_requests: int = Field(..., description="Total number of samples executed.")
    error_count: int = Field(..., description="Total number of failed actions detected.")
    error_percentage: float = Field(..., description="Calculated ratio of execution failures.")
    average_response_time_ms: float = Field(default=0.0, description="Mean latency across execution metrics.")
    stdout_raw: str = Field(default="", description="Complete captured standard console output string.")
    stderr_raw: str = Field(default="", description="Complete captured error channel output string.")
    jtl_output_path: str = Field(..., description="Target filesystem path to the generated JTL trace artifact.")
    jmeter_log_path: str = Field(..., description="Target filesystem path to the engine runtime log.")