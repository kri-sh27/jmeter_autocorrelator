"""
Auto-Correlation Pipeline Orchestrator.
Coordinates the end-to-end workflow from script execution to variable substitution.
"""

import os
import logging
from typing import Dict, Any, List
from src.config.config_engine import ApplicationConfiguration
from src.parser.jmx_parser import JmxParserEngine
from src.executor.jmeter_executor import JmeterExecutorEngine
from src.collector.jtl_collector import JtlResponseCollectorEngine
from src.detector.correlation_detector import CorrelationDetectorEngine
from src.engine.cross_reference import CrossReferenceGraphEngine
from src.generator.extractor_generator import ExtractorGeneratorEngine
from src.modifier.jmx_modifier import JmxModificationEngine

logger = logging.getLogger("JMeterAutoCorrelator")

class AutoCorrelationOrchestrator:
    """
    Unified manager interface that drives the entire auto-correlation lifecycle.
    """

    def __init__(self, config: ApplicationConfiguration) -> None:
        self.config = config
        self.detector = CorrelationDetectorEngine(min_confidence=config.correlation.min_confidence)
        self.generator = ExtractorGeneratorEngine(variable_naming_template=config.correlation.variable_naming_pattern)

    # def run_pipeline(self, source_jmx: str, output_jmx: str) -> Dict[str, Any]:
    #     """
    #     Executes the auto-correlation pipeline stages sequentially.
    #     """
    #     logger.info(f"Starting auto-correlation pipeline for: {source_jmx}")

    #     # Stage 1: Parse and validate the source JMX file structure
    #     parser = JmxParserEngine(source_jmx)
    #     initial_samplers = parser.parse()
    #     logger.info(f"Stage 1 Complete: Extracted {len(initial_samplers)} base sampler components.")

    #     # Stage 2: Execute a headless baseline run to capture live trace data
    #     executor = JmeterExecutorEngine(self.config)
    #     run_summary = executor.execute_jmx(source_jmx, run_id="baseline_trace")
    #     logger.info(f"Stage 2 Complete: Baseline run finished. Error rate: {run_summary.error_percentage}%")

    #     # Stage 3: Stream and parse transactional records from the generated JTL log
    #     collector = JtlResponseCollectorEngine(run_summary.jtl_output_path)
    #     historical_records = list(collector.stream_records())
    #     logger.info(f"Stage 3 Complete: Streamed {len(historical_records)} transaction records from log file.")

    #     # Stage 4: Scan trace records to find dynamic parameter candidates
    #     candidate_pool = []
    #     for idx, record in enumerate(historical_records):
    #         candidates = self.detector.analyze_record(record, index=idx)
    #         candidate_pool.extend(candidates)
    #     logger.info(f"Stage 4 Complete: Extracted {len(candidate_pool)} correlation candidates.")

    #     # Stage 5: Map downstream parameter re-use to build the dependency graph
    #     xref_engine = CrossReferenceGraphEngine()
    #     dependencies = xref_engine.build_cross_references(candidate_pool, historical_records)
    #     logger.info(f"Stage 5 Complete: Mapped {len(dependencies)} dynamic forward dependencies.")

    #     # Stage 6: Generate post-processor extractor configurations for the matches
    #     extractor_configs = []
    #     for dep in dependencies:
    #         cfg = self.generator.generate_extractor(dep)
    #         extractor_configs.append(cfg)
    #     logger.info(f"Stage 6 Complete: Compiled {len(extractor_configs)} extractor configurations.")

    #     # Stage 7: Apply the modifications and save the final JMX script
    #     modifier = JmxModificationEngine(source_jmx)
    #     modifier.apply_correlations(extractor_configs, dependencies)
    #     modifier.save_modified_jmx(output_jmx)
    #     logger.info(f"Stage 7 Complete: Modified script successfully exported to: {output_jmx}")

    #     return {
    #         "status": "SUCCESS",
    #         "samplers_count": len(initial_samplers),
    #         "total_requests": run_summary.total_requests,
    #         "error_percentage": run_summary.error_percentage,
    #         "detected_candidates": len(candidate_pool),
    #         "applied_correlations": len(dependencies),
    #         "output_script_path": output_jmx
    #     }

    def run_pipeline(self, source_jmx: str, output_jmx: str) -> Dict[str, Any]:
        """
        Executes the auto-correlation pipeline stages sequentially and generates analytics documentation.
        """
        logger.info(f"Starting auto-correlation pipeline for: {source_jmx}")

        # Stage 1: Parse and validate the source JMX file structure
        parser = JmxParserEngine(source_jmx)
        initial_samplers = parser.parse()
        logger.info(f"Stage 1 Complete: Extracted {len(initial_samplers)} base sampler components.")

        # Stage 2: Execute a headless baseline run to capture live trace data
        executor = JmeterExecutorEngine(self.config)
        run_summary = executor.execute_jmx(source_jmx, run_id="baseline_trace")
        logger.info(f"Stage 2 Complete: Baseline run finished. Error rate: {run_summary.error_percentage}%")

        # Stage 3: Stream and parse transactional records from the generated JTL log
        collector = JtlResponseCollectorEngine(run_summary.jtl_output_path)
        historical_records = list(collector.stream_records())
        logger.info(f"Stage 3 Complete: Streamed {len(historical_records)} transaction records from log file.")

        # Stage 4: Scan trace records to find dynamic parameter candidates
        candidate_pool = []
        for idx, record in enumerate(historical_records):
            candidates = self.detector.analyze_record(record, index=idx)
            candidate_pool.extend(candidates)
        logger.info(f"Stage 4 Complete: Extracted {len(candidate_pool)} correlation candidates.")

        # Stage 5: Map downstream parameter re-use to build the dependency graph
        xref_engine = CrossReferenceGraphEngine()
        dependencies = xref_engine.build_cross_references(candidate_pool, historical_records)
        logger.info(f"Stage 5 Complete: Mapped {len(dependencies)} dynamic forward dependencies.")

        # Stage 6: Generate post-processor extractor configurations for the matches
        extractor_configs = []
        for dep in dependencies:
            cfg = self.generator.generate_extractor(dep)
            extractor_configs.append(cfg)
        logger.info(f"Stage 6 Complete: Compiled {len(extractor_configs)} extractor configurations.")

        # Stage 7: Apply the modifications and save the final JMX script
        modifier = JmxModificationEngine(source_jmx)
        modifier.apply_correlations(extractor_configs, dependencies)
        modifier.save_modified_jmx(output_jmx)
        logger.info(f"Stage 7 Complete: Modified script successfully exported to: {output_jmx}")

        # Stage 8: Generate Enterprise Analytics Dashboards and Reports
        from src.reporter.analytics_reporter import AnalyticsReportEngine
        pipeline_stats = {
            "status": "SUCCESS",
            "samplers_count": len(initial_samplers),
            "total_requests": run_summary.total_requests,
            "error_percentage": run_summary.error_percentage,
            "detected_candidates": len(candidate_pool),
            "applied_correlations": len(dependencies)
        }
        reporter = AnalyticsReportEngine(pipeline_stats, dependencies)
        md_report = reporter.generate_markdown_summary()
        html_report = reporter.generate_html_dashboard()
        logger.info(f"Stage 8 Complete: Analytics summaries successfully written to local workspace.")

        # Enriched return map summary metadata records
        pipeline_stats["output_script_path"] = output_jmx
        pipeline_stats["markdown_report_path"] = md_report
        pipeline_stats["html_dashboard_path"] = html_report
        return pipeline_stats