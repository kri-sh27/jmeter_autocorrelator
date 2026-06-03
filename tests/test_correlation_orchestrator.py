"""
Orchestrator Pipeline Verification Suite.
Validates end-to-end data flow and lifecycle stage execution using mocks.
"""

import unittest
from unittest.mock import MagicMock, patch
from src.config.config_engine import ApplicationConfiguration
from src.orchestrator.correlation_orchestrator import AutoCorrelationOrchestrator
from src.models.sampler import JmeterSamplerContext, JmeterExecutionSummary
from src.models.tracking import SampleResultRecord

class TestAutoCorrelationOrchestrator(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_config = MagicMock(spec=ApplicationConfiguration)
        self.mock_config.correlation = MagicMock()
        self.mock_config.correlation.min_confidence = 0.60
        self.mock_config.correlation.variable_naming_pattern = "c_${param_name}"
        self.mock_config.jmeter = MagicMock()
        self.mock_config.jmeter.path = "jmeter"

        self.orchestrator = AutoCorrelationOrchestrator(self.mock_config)

    @patch("src.orchestrator.correlation_orchestrator.JmxParserEngine")
    @patch("src.orchestrator.correlation_orchestrator.JmeterExecutorEngine")
    @patch("src.orchestrator.correlation_orchestrator.JtlResponseCollectorEngine")
    @patch("src.orchestrator.correlation_orchestrator.JmxModificationEngine")
    def test_pipeline_execution_flow_and_data_propagation(
        self, mock_mod_engine: MagicMock, mock_col_engine: MagicMock, 
        mock_exe_engine: MagicMock, mock_par_engine: MagicMock
    ) -> None:
        # Mock Stage 1: Return a mock sampler list
        mock_par = mock_par_engine.return_value
        mock_par.parse.return_value = [
            JmeterSamplerContext(sampler_id="s_0", sampler_name="Login", execution_order_index=0)
        ]

        # Mock Stage 2: Return a mock run execution summary
        mock_exe = mock_exe_engine.return_value
        mock_exe.execute_jmx.return_value = JmeterExecutionSummary(
            total_requests=2, error_count=0, error_percentage=0.0,
            jtl_output_path="mock.jtl", jmeter_log_path="mock.log"
        )

        # Mock Stage 3: Return mock transaction logs containing a cookie pattern match
        mock_col = mock_col_engine.return_value
        mock_col.stream_records.return_value = [
            SampleResultRecord(
                elapsed_ms=10, sample_label="Login", thread_name="T-1",
                cookies={"JSESSIONID": "MOCK_TOKEN_VAL"}
            ),
            SampleResultRecord(
                elapsed_ms=15, sample_label="Dashboard", thread_name="T-1",
                request_headers={"Cookie": "JSESSIONID=MOCK_TOKEN_VAL"}
            )
        ]

        # Trigger the pipeline execution workflow loop
        report = self.orchestrator.run_pipeline("source.jmx", "output.jmx")

        # Verify that all components were invoked correctly in sequence
        self.assertEqual(report["status"], "SUCCESS")
        self.assertEqual(report["detected_candidates"], 1)
        self.assertEqual(report["applied_correlations"], 1)
        
        # Verify that the final modified script was saved to disk
        mock_mod_engine.return_value.save_modified_jmx.assert_called_once_with("output.jmx")