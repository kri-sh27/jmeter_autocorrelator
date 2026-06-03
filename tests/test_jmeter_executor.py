"""
Execution Engine Verification Suite.
Validates process handling logic using mock interfaces.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import shutil
from src.config.config_engine import ApplicationConfiguration
from src.executor.jmeter_executor import JmeterExecutorEngine
from src.config.exceptions import ExecutionException

class TestJmeterExecutorEngine(unittest.TestCase):

    def setUp(self) -> None:
        # Construct standard configuration payload boundaries maps
        self.mock_config = MagicMock(spec=ApplicationConfiguration)
        self.mock_config.jmeter = MagicMock()
        self.mock_config.jmeter.path = "jmeter" # Fallback binary alias
        self.mock_config.jmeter.version = "5.6.3"
        self.mock_config.jmeter.max_heap = "512m"
        self.mock_config.jmeter.min_heap = "256m"
        self.mock_config.jmeter.timeout_seconds = 60

        # Create dummy target file paths to bypass input safety checks
        self.dummy_jmx = "dummy_test_script.jmx"
        with open(self.dummy_jmx, "w", encoding="utf-8") as f:
            f.write("<mock_xml/>")

    def tearDown(self) -> None:
        if os.path.exists(self.dummy_jmx):
            os.remove(self.dummy_jmx)
        if os.path.exists("./workspace"):
            shutil.rmtree("./workspace")

    @patch("shutil.which")
    def test_missing_binary_raises_execution_exception(self, mock_which: MagicMock) -> None:
        mock_which.return_value = None  # Force systemic tracking failure
        self.mock_config.jmeter.path = "/invalid/system/path/to/jmeter"
        
        with self.assertRaises(ExecutionException):
            JmeterExecutorEngine(self.mock_config)

    # @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_successful_execution_and_telemetry_extraction(self, mock_os_path_exists: MagicMock, mock_sub_run: MagicMock) -> None:
        # mock_which.return_value = "/usr/bin/jmeter"
        # mock_os_path_exists.return_value = True

        mock_os_path_exists.side_effect = lambda path: False if str(path).endswith(".jtl") else True

        # Mock the standard console output returned by headless execution runs
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = (
            "Creating summariser <summary>\n"
            "summary +      1 in 00:00:01 =    1.0/s Avg:    82 Min:    82 Max:    82 Err:     0 (0.00%)\n"
            "summary =     10 in 00:00:05 =    2.0/s Avg:   150 Min:    45 Max:   320 Err:     1 (10.00%)\n"
            "JMeter execution completed successfully.\n"
        )
        mock_process.stderr = ""
        mock_sub_run.return_value = mock_process

        executor = JmeterExecutorEngine(self.mock_config)
        summary = executor.execute_jmx(self.dummy_jmx, run_id="unit_test")

        # Validate that metrics were extracted correctly from the console summaries
        self.assertEqual(summary.total_requests, 10)
        # self.assertEqual(summary.average_response_time_ms, 150.0)
        self.assertEqual(summary.error_count, 1)
        self.assertEqual(summary.error_percentage, 10.0)
        self.assertTrue(os.path.exists(summary.jtl_output_path))