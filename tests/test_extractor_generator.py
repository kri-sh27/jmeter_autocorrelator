"""
Extractor Configuration Generator Verification Suite.
Validates code generation pipelines for post-processor components.
"""

import unittest
from src.core.constants import CorrelationType, ExtractorType, HttpLocation
from src.models.correlation import CorrelationCandidate, ParameterDependencyMatrix, GeneratedExtractorConfig
from src.generator.extractor_generator import ExtractorGeneratorEngine

class TestExtractorGeneratorEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.generator = ExtractorGeneratorEngine(variable_naming_template="c_${param_name}")
        
        # Build standard upstream verification validation metrics
        self.mock_candidate = CorrelationCandidate(
            parameter_name="c_oauth_token",
            extracted_value="GHI789_MNO456_TOKEN",
            source_sampler_id="sampler_step_3",
            source_sampler_name="Step 3 - Authenticate",
            location=HttpLocation.BODY,
            correlation_type=CorrelationType.OAUTH_TOKEN,
            extractor_type=ExtractorType.REGEX,
            extraction_expression="token\":\"(.*?)\"",
            confidence_score=0.92
        )
        
        self.mock_dependency = ParameterDependencyMatrix(
            candidate=self.mock_candidate,
            target_sampler_id="sampler_step_4",
            target_sampler_name="Step 4 - Query Metrics",
            target_location=HttpLocation.HEADERS,
            target_parameter_key="Authorization",
            usage_context_snippet="Bearer GHI789_MNO456_TOKEN"
        )

    def test_regex_extractor_generation_pipeline(self) -> None:
        config = self.generator.generate_extractor(self.mock_dependency)
        
        # Verify component initialization fields match specifications
        self.assertEqual(config.variable_name, "c_oauth_token")
        self.assertEqual(config.extractor_type, ExtractorType.REGEX)
        self.assertEqual(config.target_field, HttpLocation.BODY)
        self.assertEqual(config.template, "$1$")
        self.assertEqual(config.expression, "token\":\"(.*?)\"")
        self.assertEqual(config.default_fallback, "c_oauth_token_NOT_FOUND")

    def test_json_extractor_fallback_routing(self) -> None:
        # Tweak candidate configuration parameters to route through JSON pathways
        self.mock_candidate.extractor_type = ExtractorType.JSON
        self.mock_dependency.target_parameter_key = "access_token"
        
        config = self.generator.generate_extractor(self.mock_dependency)
        
        self.assertEqual(config.extractor_type, ExtractorType.JSON)
        self.assertEqual(config.expression, "$..access_token")