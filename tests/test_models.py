"""
Domain Model Validation Suite.
"""

import unittest
from pydantic import ValidationError
from src.models.correlation import CorrelationCandidate
from src.core.constants import CorrelationType, ExtractorType, HttpLocation

class TestDomainModels(unittest.TestCase):

    def test_valid_correlation_candidate_instantiation(self) -> None:
        candidate = CorrelationCandidate(
            parameter_name="c_csrfToken",
            extracted_value="AABBCCDD11223344",
            source_sampler_id="sampler_001",
            source_sampler_name="HTTP_Login_Page",
            location=HttpLocation.BODY,
            correlation_type=CorrelationType.CSRF_TOKEN,
            extractor_type=ExtractorType.REGEX,
            extraction_expression="token='(.*?)'",
            confidence_score=0.95
        )
        self.assertEqual(candidate.parameter_name, "c_csrfToken")
        self.assertEqual(candidate.location, "BODY")

    def test_invalid_confidence_score_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            CorrelationCandidate(
                parameter_name="c_invalid",
                extracted_value="val",
                source_sampler_id="id",
                source_sampler_name="name",
                location=HttpLocation.HEADERS,
                correlation_type=CorrelationType.CUSTOM,
                extractor_type=ExtractorType.JSON,
                extraction_expression="$.id",
                confidence_score=1.5  # Invalid: must be <= 1.0
            )