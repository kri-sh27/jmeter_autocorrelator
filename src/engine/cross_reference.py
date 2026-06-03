"""
Cross-Reference Graph Engine.
Traces extracted parameters into subsequent requests to construct a data dependency map.
"""

import logging
from typing import List, Dict, Any, Optional
from src.core.constants import HttpLocation
from src.models.tracking import SampleResultRecord
from src.models.correlation import CorrelationCandidate, ParameterDependencyMatrix

logger = logging.getLogger("JMeterAutoCorrelator")

class CrossReferenceGraphEngine:
    """
    Analyzes historical data matrices to trace how extracted parameter values 
    propagate forward into downstream execution targets.
    """

    def __init__(self) -> None:
        self._dependency_graph: List[ParameterDependencyMatrix] = []
        self._source_usage_counts: Dict[str, int] = {}

    def get_dependency_graph(self) -> List[ParameterDependencyMatrix]:
        """Returns the completed cross-referenced parameters collection matrix."""
        return self._dependency_graph

    def get_usage_counts(self) -> Dict[str, int]:
        """Returns tracking frequencies mapped against unique candidate parameter strings."""
        return self._source_usage_counts

    def build_cross_references(
        self, 
        candidates_pool: List[CorrelationCandidate], 
        historical_records: List[SampleResultRecord]
    ) -> List[ParameterDependencyMatrix]:
        """
        Correlates extracted parameter values against subsequent transaction fields 
        to track forward data propagation.
        """
        self._dependency_graph.clear()
        self._source_usage_counts.clear()

        if not candidates_pool or not historical_records:
            logger.warning("Empty source matrix parameters passed down cross-reference calculation tracks.")
            return []

        # Iterate through every extracted candidate in the system pool
        for candidate in candidates_pool:
            param_value = candidate.extracted_value
            
            # Extract numerical sequence offset indexes from structural labels to guarantee sequential evaluation
            try:
                # Format constraint assumption fallback: "sampler_step_X"
                source_idx = int(candidate.source_sampler_id.split("_")[-1])
            except (ValueError, IndexError):
                source_idx = 0

            # Scan only chronological downstream requests to respect execution order boundaries
            for target_idx in range(source_idx + 1, len(historical_records)):
                target_record = historical_records[target_idx]
                target_sampler_id = f"sampler_step_{target_idx}"
                
                # Check for parameter re-use across available outgoing transport segments
                self._evaluate_target_headers(candidate, param_value, target_record, target_sampler_id)
                self._evaluate_target_cookies(candidate, param_value, target_record, target_sampler_id)
                self._evaluate_target_body(candidate, param_value, target_record, target_sampler_id)

        logger.info(f"Cross-reference compilation completed. Generated ({len(self._dependency_graph)}) explicit link maps.")
        return self._dependency_graph

    def _evaluate_target_headers(self, cand: CorrelationCandidate, val: str, rec: SampleResultRecord, t_id: str) -> None:
        """Inspects outgoing headers for occurrences of the candidate value."""
        for h_key, h_val in rec.request_headers.items():
            if val in h_val:
                self._register_dependency(cand, t_id, rec.sample_label, HttpLocation.HEADERS, h_key, h_val)

    def _evaluate_target_cookies(self, cand: CorrelationCandidate, val: str, rec: SampleResultRecord, t_id: str) -> None:
        """Inspects outgoing request cookies for occurrences of the candidate value."""
        # Check standard headers for inline cookies if explicit collections are not split out
        cookie_header = rec.request_headers.get("Cookie", "")
        if val in cookie_header:
            self._register_dependency(cand, t_id, rec.sample_label, HttpLocation.COOKIES, "Cookie", cookie_header)

    def _evaluate_target_body(self, cand: CorrelationCandidate, val: str, rec: SampleResultRecord, t_id: str) -> None:
        """Inspects outgoing payloads and form arguments for occurrences of the candidate value."""
        if not rec.request_body:
            return

        if val in rec.request_body:
            # Attempt to extract precise form keys if the request body uses query parameter string formatting
            matched_key: Optional[str] = None
            if "=" in rec.request_body:
                for parameter_token in rec.request_body.split("&"):
                    if "=" in parameter_token:
                        parts = parameter_token.split("=", 1)
                        if len(parts) == 2 and val in parts[1]:
                            matched_key = parts[0]
                            break

            # Bound structural display contexts gracefully
            snippet = rec.request_body if len(rec.request_body) <= 120 else f"{rec.request_body[:60]}...[TRUNCATED]...{rec.request_body[-40:]}"
            self._register_dependency(cand, t_id, rec.sample_label, HttpLocation.BODY, matched_key, snippet)

    def _register_dependency(
        self, 
        cand: CorrelationCandidate, 
        t_id: str, 
        t_name: str, 
        loc: HttpLocation, 
        key: Optional[str], 
        snippet: str
    ) -> None:
        """Appends structural links securely and increments total usage counters."""
        matrix_link = ParameterDependencyMatrix(
            candidate=cand,
            target_sampler_id=t_id,
            target_sampler_name=t_name,
            target_location=loc,
            target_parameter_key=key,
            usage_context_snippet=snippet
        )
        self._dependency_graph.append(matrix_link)
        
        # Track aggregate parameter occurrences globally
        p_name = cand.parameter_name
        self._source_usage_counts[p_name] = self._source_usage_counts.get(p_name, 0) + 1