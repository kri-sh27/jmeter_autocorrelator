"""
Correlation Detection Engine.
Implements signature matching and heuristic evaluation to locate dynamic system parameters.
"""

import re
import logging
from typing import List, Dict, Any, Tuple
from src.core.constants import CorrelationType, ExtractorType, HttpLocation
from src.models.tracking import SampleResultRecord
from src.models.correlation import CorrelationCandidate

logger = logging.getLogger("JMeterAutoCorrelator")

class RegexPatternLibrary:
    """
    Central repository of regular expression signatures compiled for enterprise boundary tokens.
    """
    @staticmethod
    def get_rules() -> List[Tuple[CorrelationType, List[re.Pattern]]]:
        return [
            (CorrelationType.JSESSIONID, [
                re.compile(r"jsessionid=(?P<val>[a-zA-Z0-9_\-\.\~]+)", re.IGNORECASE),
                re.compile(r"JSESSIONID\":\"(?P<val>[a-zA-Z0-9_\-\.\~]+)\"", re.IGNORECASE)
            ]),
            (CorrelationType.PHPSESSID, [
                re.compile(r"PHPSESSID=(?P<val>[a-zA-Z0-9\,\-]+)", re.IGNORECASE),
                re.compile(r"PHPSESSID\":\"(?P<val>[a-zA-Z0-9\,\-]+)\"", re.IGNORECASE)
            ]),
            (CorrelationType.ASP_SESSION, [
                re.compile(r"ASPSESSIONID[A-Z]{8}=(?P<val>[a-zA-Z0-9]+)", re.IGNORECASE),
                re.compile(r"ASP\.NET_SessionId=(?P<val>[a-zA-Z0-9_\-\+]+)", re.IGNORECASE)
            ]),
            (CorrelationType.CSRF_TOKEN, [
                re.compile(r"csrf[_-]token['\"]?\s*[:=]\s*['\"](?P<val>[a-zA-Z0-9_\-\.\~\+\/]+)['\"]", re.IGNORECASE),
                re.compile(r"name=['\"]_csrf['\"][^>]*value=['\"](?P<val>[a-zA-Z0-9_\-\.\~\+\/]+)['\"]", re.IGNORECASE),
                re.compile(r"value=['\"](?P<val>[a-zA-Z0-9_\-\.\~\+\/]+)['\"][^>]*name=['\"]_csrf['\"]", re.IGNORECASE),
                re.compile(r"X-CSRF-TOKEN['\"]?\s*:\s*['\"](?P<val>[a-zA-Z0-9_\-\.]+)", re.IGNORECASE)
            ]),
            (CorrelationType.VIEWSTATE, [
                re.compile(r"id=['\"]__VIEWSTATE['\"]?[^>]*value=['\"](?P<val>[a-zA-Z0-9_\-\+\=\/]+)['\"]", re.IGNORECASE),
                re.compile(r"value=['\"](?P<val>[a-zA-Z0-9_\-\+\=\/]+)['\"][^>]*id=['\"]__VIEWSTATE['\"]", re.IGNORECASE)
            ]),
            (CorrelationType.EVENTVALIDATION, [
                re.compile(r"id=['\"]__EVENTVALIDATION['\"]?[^>]*value=['\"](?P<val>[a-zA-Z0-9_\-\+\=\/]+)['\"]", re.IGNORECASE),
                re.compile(r"value=['\"](?P<val>[a-zA-Z0-9_\-\+\=\/]+)['\"][^>]*id=['\"]__EVENTVALIDATION['\"]", re.IGNORECASE)
            ]),
            (CorrelationType.JWT_TOKEN, [
                re.compile(r"bearer\s+(?P<val>eyJb[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+)", re.IGNORECASE),
                re.compile(r"access_token['\"]?\s*[:=]\s*['\"](?P<val>eyJb[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+)['\"]", re.IGNORECASE),
                re.compile(r"id_token['\"]?\s*[:=]\s*['\"](?P<val>eyJb[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+)['\"]", re.IGNORECASE)
            ]),
            (CorrelationType.OAUTH_TOKEN, [
                re.compile(r"oauth_token['\"]?\s*[:=]\s*['\"](?P<val>[a-zA-Z0-9_\-\.\~\+\/]+)['\"]", re.IGNORECASE),
                re.compile(r"refresh_token['\"]?\s*[:=]\s*['\"](?P<val>[a-zA-Z0-9_\-\.\~\+\/]+)['\"]", re.IGNORECASE)
            ]),
            (CorrelationType.NONCE, [
                re.compile(r"nonce=['\"](?P<val>[a-zA-Z0-9_\-\.\~\+\/=]+)['\"]", re.IGNORECASE),
                re.compile(r"nonce['\"]?\s*[:=]\s*['\"](?P<val>[a-zA-Z0-9_\-\.\~\+\/=]+)['\"]", re.IGNORECASE)
            ]),
            (CorrelationType.TIMESTAMP, [
                re.compile(r"timestamp['\"]?\s*[:=]\s*(?P<val>\d{10,13})", re.IGNORECASE),
                re.compile(r"epoch['\"]?\s*[:=]\s*(?P<val>\d{10,13})", re.IGNORECASE)
            ]),
            (CorrelationType.API_KEY, [
                re.compile(r"api[_-]key['\"]?\s*[:=]\s*['\"](?P<val>[a-zA-Z0-9_\-]+)['\"]", re.IGNORECASE),
                re.compile(r"apikey['\"]?\s*[:=]\s*['\"](?P<val>[a-zA-Z0-9_\-]+)['\"]", re.IGNORECASE)
            ]),
            (CorrelationType.SPRING_SECURITY, [
                re.compile(r"name=['\"]_spring_security_.*_token['\"][^>]*value=['\"](?P<val>[a-zA-Z0-9_\-]+)", re.IGNORECASE)
            ]),
            (CorrelationType.WORDPRESS_NONCE, [
                re.compile(r"wpnonce=['\"](?P<val>[a-zA-Z0-9]{10})['\"]", re.IGNORECASE),
                re.compile(r"_wpnonce=(?P<val>[a-zA-Z0-9]{10})", re.IGNORECASE)
            ]),
            (CorrelationType.HIDDEN_FIELD, [
                re.compile(r"<input[^>]*type=['\"]hidden['\"][^>]*name=['\"](?P<name>[a-zA-Z0-9_\-]+)['\"][^>]*value=['\"](?P<val>[^'\"]*)['\"]", re.IGNORECASE)
            ]),
            (CorrelationType.CORRELATION_ID, [
                re.compile(r"(correlation[_-]id|request[_-]id|trace[_-]id)['\"]?\s*[:=]\s*['\"](?P<val>[a-zA-Z0-9_\-]+)['\"]", re.IGNORECASE)
            ])
        ]

class ConfidenceScoringEngine:
    """
    Calculates the confidence rating of extraction values based on pattern matches 
    and entropy profiles.
    """
    @staticmethod
    def evaluate(c_type: CorrelationType, param_name: str, value: str) -> float:
        # Prevent tracking empty inputs or system noise
        if not value or len(value) < 4:
            return 0.10

        score = 0.50

        # Structural high-reliability classification triggers
        if c_type in (CorrelationType.JSESSIONID, CorrelationType.VIEWSTATE, CorrelationType.JWT_TOKEN, CorrelationType.CSRF_TOKEN):
            score += 0.30

        # Property name match validation hooks
        clean_name = param_name.lower()
        clean_type = c_type.value.lower()
        if clean_type in clean_name or clean_name in clean_type:
            score += 0.15

        # Format profiling (e.g., matching standard UUID architectures)
        uuid_pattern = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)
        if uuid_pattern.match(value):
            score += 0.10

        return min(max(score, 0.0), 1.0)

class CorrelationDetectorEngine:
    """
    Scans runtime transactional records against the pattern library 
    to extract actionable correlation candidates.
    """
    def __init__(self, min_confidence: float = 0.60) -> None:
        self.min_confidence = min_confidence
        self.rules = RegexPatternLibrary.get_rules()

    def analyze_record(self, record: SampleResultRecord, index: int) -> List[CorrelationCandidate]:
        candidates: List[CorrelationCandidate] = []
        sampler_id = f"sampler_step_{index}"
        
        # Scenario A: Evaluate Response Headers
        for h_name, h_val in record.response_headers.items():
            scanned = self._scan_string_payload(h_val, HttpLocation.HEADERS)
            for c_type, extracted_name, val, expr in scanned:
                score = ConfidenceScoringEngine.evaluate(c_type, extracted_name or h_name, val)
                if score >= self.min_confidence:
                    candidates.append(self._build_candidate(
                        sampler_id, record.sample_label, extracted_name or h_name, val, 
                        HttpLocation.HEADERS, c_type, expr, score
                    ))

        # Scenario B: Evaluate Response Cookies
        for c_name, c_val in record.cookies.items():
            scanned = self._scan_string_payload(f"{c_name}={c_val}", HttpLocation.COOKIES)
            for c_type, extracted_name, val, expr in scanned:
                score = ConfidenceScoringEngine.evaluate(c_type, extracted_name or c_name, val)
                if score >= self.min_confidence:
                    candidates.append(self._build_candidate(
                        sampler_id, record.sample_label, extracted_name or c_name, val, 
                        HttpLocation.COOKIES, c_type, expr, score
                    ))

        # Scenario C: Evaluate Full Response Bodies
        if record.response_body:
            scanned = self._scan_string_payload(record.response_body, HttpLocation.BODY)
            for c_type, extracted_name, val, expr in scanned:
                # Generate a clean variable handle if no explicit field name is matched
                param_handle = extracted_name or f"{c_type.value.lower()}_{len(candidates)}"
                score = ConfidenceScoringEngine.evaluate(c_type, param_handle, val)
                if score >= self.min_confidence:
                    candidates.append(self._build_candidate(
                        sampler_id, record.sample_label, param_handle, val, 
                        HttpLocation.BODY, c_type, expr, score
                    ))

        return candidates

    def _scan_string_payload(self, text: str, loc: HttpLocation) -> List[Tuple[CorrelationType, Optional[str], str, str]]:
        hits: List[Tuple[CorrelationType, Optional[str], str, str]] = []
        if not text:
            return hits

        for c_type, patterns in self.rules:
            for regex in patterns:
                for match in regex.finditer(text):
                    dict_group = match.groupdict()
                    val = dict_group.get("val")
                    name = dict_group.get("name", None)
                    
                    if val:
                        hits.append((c_type, name, val, regex.pattern))
                    elif match.lastgroup is None and len(match.groups()) > 0:
                        # Fallback for patterns that capture unnamed groups
                        captured_value = match.group(1)
                        if captured_value:
                            hits.append((c_type, name, captured_value, regex.pattern))
        return hits

    def _build_candidate(self, s_id: str, s_name: str, p_name: str, val: str, 
                         loc: HttpLocation, c_type: CorrelationType, expr: str, score: float) -> CorrelationCandidate:
        # Determine the appropriate extractor strategy based on the payload location context
        ext_type = ExtractorType.REGEX
        if loc == HttpLocation.BODY and val.startswith("{") and val.endswith("}"):
            ext_type = ExtractorType.JSON

        return CorrelationCandidate(
            parameter_name=f"c_{p_name}",
            extracted_value=val,
            source_sampler_id=s_id,
            source_sampler_name=s_name,
            location=loc,
            correlation_type=c_type,
            extractor_type=ext_type,
            extraction_expression=expr,
            confidence_score=score
        )