"""
JMeter Headless Execution Engine.
Spawns and tracks native cross-platform Java subprocesses securely following SOLID design patterns.
"""

import os
import subprocess
import logging
import re
import shutil
from typing import List, Dict, Any, Tuple
from src.config.config_engine import ApplicationConfiguration
from src.config.exceptions import ExecutionException
from src.models.sampler import JmeterExecutionSummary

logger = logging.getLogger("JMeterAutoCorrelator")

class JmeterExecutorEngine:
    """
    Manages non-GUI execution lifecycles, parses runtime diagnostic outputs, 
    and handles platform-specific variations seamlessly.
    """

    def __init__(self, config: ApplicationConfiguration) -> None:
        self.config = config
        self.jmeter_path = config.jmeter.path
        self.timeout = config.jmeter.timeout_seconds
        self._validate_binary_presence()

    def _validate_binary_presence(self) -> None:
        """Verifies that the target path or alias resolves to an executable binary command."""
        # Check explicit path pathing first, fallback to systemic search
        if not os.path.exists(self.jmeter_path) and not shutil.which(self.jmeter_path):
            raise ExecutionException(
                f"Configured JMeter executable target could not be resolved or lacks binary access: {self.jmeter_path}"
            )

    def execute_jmx(self, input_jmx_path: str, run_id: str = "baseline") -> JmeterExecutionSummary:
        """
        Executes a targeted test plan file in headless non-GUI mode.
        Automatically outputs isolated tracking log and trace artifacts (.jtl).
        """
        if not os.path.exists(input_jmx_path):
            raise ExecutionException(f"Target execution JMX script file does not exist: {input_jmx_path}")

        # Set up a structured output directory for run artifacts
        workspace_dir = os.path.abspath("./workspace")
        os.makedirs(workspace_dir, exist_ok=True)

        jtl_output = os.path.join(workspace_dir, f"run_{run_id}.jtl")
        jmeter_log = os.path.join(workspace_dir, f"jmeter_{run_id}.log")

        # Clean existing files to prevent appending errors or mixups
        for path in [jtl_output, jmeter_log]:
            if os.path.exists(path):
                os.remove(path)

        # Build cross-platform CLI runtime arguments string array
        cmd = self._build_command_arguments(input_jmx_path, jtl_output, jmeter_log)
        
        logger.info(f"Launching JMeter non-GUI Subprocess Pipeline. Command matrix: {' '.join(cmd)}")
        
        try:
            # Execute cross-platform subprocess safely with explicit timeouts and isolated environments
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout,
                check=False,
                env=os.environ.copy()
            )
        except subprocess.TimeoutExpired as err:
            raise ExecutionException(f"JMeter engine run exceeded the max timeout threshold limit of {self.timeout}s: {str(err)}")
        except Exception as exc:
            raise ExecutionException(f"Fatal operating system failure when spawning process worker: {str(exc)}")

        logger.info(f"Headless execution execution finalized. Process return exit code: {process.returncode}")

        # Process standard output channels for performance metrics
        summary = self._parse_console_metrics(
            stdout=process.stdout,
            stderr=process.stderr,
            jtl_path=jtl_output,
            log_path=jmeter_log
        )

        if process.returncode != 0:
            logger.warning(f"JMeter process terminated with a non-zero exit code ({process.returncode}). Check log outputs.")
            if "Error in NonGUIDriver" in process.stdout or not os.path.exists(jtl_output):
                raise ExecutionException(f"Fatal JMeter structural configuration runtime execution failure: {process.stderr or process.stdout}")

        return summary

    def _build_command_arguments(self, jmx: str, jtl: str, log: str) -> List[str]:
        """Assembles CLI argument vectors containing heap settings and headless configuration switches."""
        # Handle custom JVM Heap adjustments gracefully via standard environment injectors inside JMeter paths
        jvm_args = f"-Xms{self.config.jmeter.min_heap} -Xmx{self.config.jmeter.max_heap}"
        os.environ["JVM_ARGS"] = jvm_args

        arguments = [
            self.jmeter_path,
            "-n",                  # Run in headless non-GUI mode
            "-t", jmx,             # Path to the source JMX file
            "-l", jtl,             # Target path for output log results (.jtl format)
            "-j", log,             # Target path for runtime execution log entries
            "-Dsampleresult.timestamp.start=true"  # Enforce standardized start-time epoch offsets
        ]
        return arguments

    def _parse_console_metrics(self, stdout: str, stderr: str, jtl_path: str, log_path: str) -> JmeterExecutionSummary:
        """
        Parses JMeter console summaries using regular expressions 
        to capture real-time execution statistics.
        """
        # Target signature format example: "summary =     16 in 00:00:04 =    4.0/s Avg:   122 Min:    45 Max:   890 Err:     0 (0.00%)"
        summary_pattern = re.compile(
            r"summary\s+=\s+(?P<count>\d+)\s+in\s+(?P<time>[^\s=]+)\s+=\s+(?P<rate>[^\s/]+)/s\s+Avg:\s+(?P<avg>\d+).*?Err:\s+(?P<errors>\d+)\s+\((?P<pct>[0-9.]+)%\)"
        )

        total_requests = 0
        error_count = 0
        error_percentage = 0.0
        avg_time = 0.0

        matches = summary_pattern.findall(stdout)
        if matches:
            # We target the final consolidated reporting metric block line entry matched
            final_match = matches[-1]
            try:
                total_requests = int(final_match[0])
                avg_time = float(final_match[3])
                error_count = int(final_match[4])
                error_percentage = float(final_match[5])
            except (ValueError, IndexError) as parse_err:
                logger.debug(f"Non-critical text parsing offset skipped over matching telemetry blocks: {str(parse_err)}")

        return JmeterExecutionSummary(
            total_requests=total_requests,
            error_count=error_count,
            error_percentage=error_percentage,
            average_response_time_ms=avg_time,
            stdout_raw=stdout,
            stderr_raw=stderr,
            jtl_output_path=jtl_path,
            jmeter_log_path=log_path
        )