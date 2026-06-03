"""
Reporting Engine Verification Suite.
Validates reporting structures and document creation rules.
"""

import os
import shutil
import unittest
from src.core.constants import CorrelationType, ExtractorType, HttpLocation
from src.models.correlation import CorrelationCandidate, ParameterDependencyMatrix
from src.reporter.analytics_reporter import AnalyticsReportEngine

class TestAnalyticsReportEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_stats = {
            "status": "SUCCESS",
            "samplers_count": 5,
            "total_requests": 25,
            "error_percentage": 4.0,
            "detected_candidates": 2,
            "applied_correlations": 1
        }
        
        # Build dummy structured candidate fields to check visualization output pipelines
        mock_candidate = CorrelationCandidate(
            parameter_name="c_session_token",
            extracted_value="ABC123XYZ",
            source_sampler_id="sampler_step_0",
            source_sampler_name="Step 0 - Auth Login",
            location=HttpLocation.HEADERS,
            correlation_type=CorrelationType.SESSION_ID,
            extractor_type=ExtractorType.REGEX,
            extraction_expression=".*",
            confidence_score=0.95
        )
        
        self.mock_dependency = ParameterDependencyMatrix(
            candidate=mock_candidate,
            target_sampler_id="sampler_step_2",
            target_sampler_name="Step 2 - Execute Payment",
            target_location=HttpLocation.HEADERS,
            target_parameter_key="X-Auth-Token",
            usage_context_snippet="X-Auth-Token: ABC123XYZ"
        )
        
        self.reporter = AnalyticsReportEngine(self.mock_stats, [self.mock_dependency])

    def tearDown(self) -> None:
        if os.path.exists("./workspace/reports"):
            shutil.rmtree("./workspace/reports")

    def test_markdown_report_generation(self) -> None:
        path = self.reporter.generate_markdown_summary()
        self.assertTrue(os.path.exists(path))
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("# JMeter Auto-Correlation Performance Report", content)
            self.assertIn("c_session_token", content)
            self.assertIn("Step 2 - Execute Payment", content)

    def test_html_dashboard_generation(self) -> None:
        path = self.reporter.generate_html_dashboard()
        self.assertTrue(os.path.exists(path))
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("JMeter Auto-Correlation Analytics Hub", content)
            self.assertIn("c_session_token", content)