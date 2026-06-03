"""
Cross-Reference Dependency Engine Verification Suite.
Validates mapping logic for forward parameter propagation.
"""

import unittest
from src.core.constants import CorrelationType, ExtractorType, HttpLocation
from src.models.correlation import CorrelationCandidate
from src.models.tracking import SampleResultRecord
from src.engine.cross_reference import CrossReferenceGraphEngine

class TestCrossReferenceGraphEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.engine = CrossReferenceGraphEngine()
        
        # 1. Build an upstream source candidate
        self.mock_candidate = CorrelationCandidate(
            parameter_name="c_session_id",
            extracted_value="SECURE_987654321_ABC",
            source_sampler_id="sampler_step_0",
            source_sampler_name="Step 0 - Initial Handshake",
            location=HttpLocation.HEADERS,
            correlation_type=CorrelationType.SESSION_ID,
            extractor_type=ExtractorType.REGEX,
            extraction_expression="id=(.*)",
            confidence_score=0.90
        )
        
        # 2. Build a timeline of execution steps to verify forward propagation tracking
        self.step_0_record = SampleResultRecord(
            elapsed_ms=5, response_code="200", thread_name="T-1", sample_label="Step 0 - Initial Handshake"
        )
        self.step_1_record = SampleResultRecord(
            elapsed_ms=12, response_code="200", thread_name="T-1", sample_label="Step 1 - Account Action",
            request_headers={"Authorization": "Bearer SECURE_987654321_ABC"}
        )
        self.step_2_record = SampleResultRecord(
            elapsed_ms=20, response_code="200", thread_name="T-1", sample_label="Step 2 - Complete Checkout",
            request_body="action=confirm&session_id_field=SECURE_987654321_ABC&status=true"
        )

        self.historical_records = [self.step_0_record, self.step_1_record, self.step_2_record]

    def test_successful_cross_reference_mapping(self) -> None:
        graph = self.engine.build_cross_references(
            candidates_pool=[self.mock_candidate], 
            historical_records=self.historical_records
        )
        
        # Verify that occurrences are detected across downstream steps 1 and 2
        self.assertEqual(len(graph), 2)
        
        # Validate header reuse metrics in Step 1
        link_1 = graph[0]
        self.assertEqual(link_1.target_sampler_name, "Step 1 - Account Action")
        self.assertEqual(link_1.target_location, HttpLocation.HEADERS)
        self.assertEqual(link_1.target_parameter_key, "Authorization")
        
        # Validate body parameter reuse metrics in Step 2
        link_2 = graph[1]
        self.assertEqual(link_2.target_sampler_name, "Step 2 - Complete Checkout")
        self.assertEqual(link_2.target_location, HttpLocation.BODY)
        self.assertEqual(link_2.target_parameter_key, "session_id_field")

    def test_usage_frequency_aggregation(self) -> None:
        self.engine.build_cross_references([self.mock_candidate], self.historical_records)
        counts = self.engine.get_usage_counts()
        
        self.assertIn("c_session_id", counts)
        self.assertEqual(counts["c_session_id"], 2)