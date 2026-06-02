"""
Constants and Enumerations Engine.
Defines system-wide strict enums and immutable parameters following SOLID design.
"""

from enum import Enum, unique

@unique
class CorrelationType(str, Enum):
    SESSION_ID = "SESSION_ID"
    JSESSIONID = "JSESSIONID"
    PHPSESSID = "PHPSESSID"
    ASP_SESSION = "ASP_SESSION"
    CSRF_TOKEN = "CSRF_TOKEN"
    VIEWSTATE = "VIEWSTATE"
    EVENTVALIDATION = "EVENTVALIDATION"
    JWT_TOKEN = "JWT_TOKEN"
    OAUTH_TOKEN = "OAUTH_TOKEN"
    CORRELATION_ID = "CORRELATION_ID"
    REQUEST_ID = "REQUEST_ID"
    TRACE_ID = "TRACE_ID"
    NONCE = "NONCE"
    TIMESTAMP = "TIMESTAMP"
    API_KEY = "API_KEY"
    TRANSACTION_ID = "TRANSACTION_ID"
    SAML_TOKEN = "SAML_TOKEN"
    SPRING_SECURITY = "SPRING_SECURITY"
    WORDPRESS_NONCE = "WORDPRESS_NONCE"
    HIDDEN_FIELD = "HIDDEN_FIELD"
    CUSTOM = "CUSTOM"

@unique
class ExtractorType(str, Enum):
    REGEX = "REGEX"
    JSON = "JSON"
    XPATH = "XPATH"
    BOUNDARY = "BOUNDARY"
    CSS = "CSS"

@unique
class HttpLocation(str, Enum):
    URL = "URL"
    BODY = "BODY"
    HEADERS = "HEADERS"
    COOKIES = "COOKIES"
    RESPONSE_CODE = "RESPONSE_CODE"

# Global System Constants
DEFAULT_ENCODING: str = "utf-8"
XML_JMX_NAMESPACE: str = "http://www.w3.org/2001/XMLSchema-instance"