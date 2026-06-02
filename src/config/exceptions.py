"""
Domain-Specific Exception Hierarchy.
Provides precise architectural boundaries for predictable runtime recovery blocks.
"""

class AutoCorrelatorException(Exception):
    """Base exception matrix element for all tool errors."""
    def __init__(self, message: str, context: str = "SYSTEM") -> None:
        super().__init__(message)
        self.message = message
        self.context = context

class ConfigurationException(AutoCorrelatorException):
    """Raised when environment or initialization values violate specifications."""
    def __init__(self, message: str) -> None:
        super().__init__(message, context="CONFIG")

class JmxParsingException(AutoCorrelatorException):
    """Raised when the target XML structure violates DOM validation paths."""
    def __init__(self, message: str) -> None:
        super().__init__(message, context="PARSER")

class ExecutionException(AutoCorrelatorException):
    """Raised when JMeter binary pipelines fail execution boundaries."""
    def __init__(self, message: str) -> None:
        super().__init__(message, context="EXECUTOR")