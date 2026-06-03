# """
# Central Application Bootstrapper.
# Parses CLI statements to coordinate system configuration and execution context.
# """

# import sys
# import argparse
# import logging
# from src.config.config_engine import ApplicationConfiguration
# from src.core.logging_infra import LoggingInfrastructure
# from src.config.exceptions import AutoCorrelatorException

# def bootstrap_cli() -> argparse.Namespace:
#     """
#     Constructs and processes explicit terminal parameters.
#     """
#     parser = argparse.ArgumentParser(
#         description="Enterprise Production-Grade JMeter Dynamic Load Test Auto-Correlation Automation Engine Framework."
#     )
#     parser.add_argument(
#         "--jmx",
#         required=True,
#         help="Path to the source, un-correlated Apache JMeter project XML descriptor asset."
#     )
#     parser.add_argument(
#         "--output",
#         required=True,
#         help="Target filepath to write out the fully refactored, dynamic correlation project configuration."
#     )
#     parser.add_argument(
#         "--config",
#         default="config.yaml",
#         help="Location map parsing settings configuration overrides framework file."
#     )
#     return parser.parse_parse_args() if hasattr(parser, 'parse_parse_args') else parser.parse_args()

# def main() -> None:
#     """
#     System entry point. Orchestrates structural initializations and handles system exceptions.
#     """
#     args = bootstrap_cli()
    
#     try:
#         # Load System Settings Matrix
#         app_config = ApplicationConfiguration.load_from_yaml(args.config)
        
#         # Instantiate System Logger Framework Interfacing
#         logger = LoggingInfrastructure.setup(app_config.logging.model_dump())
        
#         logger.info("Initializing Enterprise JMeter Auto-Correlator Core Orchestration Stack Engine.")
#         logger.info(f"Target Source JMX Script Reference Path: {args.jmx}")
#         logger.info(f"Target Generation Structural Export File Location: {args.output}")
        
#         # Core Subsystem Engines execute in subsequent phases...
#         logger.info("Phase 1 Project Foundation Framework Bootstrapped Successfully.")
        
#     except AutoCorrelatorException as error_context:
#         print(f"Operational Exception Interrupt Occurred Context [{error_context.context}]: {error_context.message}", file=sys.stderr)
#         sys.exit(1)
#     except Exception as fatal_unhandled:
#         print(f"Fatal Structural Global Integration Failure Unhandled: {str(fatal_unhandled)}", file=sys.stderr)
#         sys.exit(2)

# if __name__ == "__main__":
#     main()


"""
JMeter Auto-Correlator Core CLI Entrypoint.
Provides a clean, unified command-line interface to launch the correlation orchestration engine.
"""

import os
import sys
import argparse
import logging
from src.config.config_engine import ConfigurationEngine
from src.core.logging_infra import LoggingInfrastructure
from src.orchestrator.correlation_orchestrator import AutoCorrelationOrchestrator
from src.config.exceptions import JmeterAutoCorrelatorException

def main() -> None:
    # 1. Initialize parsing interfaces for incoming CLI flags
    parser = argparse.ArgumentParser(
        description="Automates correlation workflows for Apache JMeter test plan scripts (.jmx)."
    )
    parser.add_argument(
        "--jmx", required=True, help="Path to the original un-correlated source JMX file."
    )
    parser.add_argument(
        "--output", required=True, help="Destination path where the correlated script will be written."
    )
    parser.add_argument(
        "--config", default="config.yaml", help="Path to the tool's runtime YAML configuration file."
    )
    args = parser.parse_args()

    # 2. Initialize application logging infrastructure
    LoggingInfrastructure.setup_logging(log_level="INFO")
    logger = logging.getLogger("JMeterAutoCorrelator")
    
    logger.info("Initializing JMeter Auto-Correlator Framework...")

    try:
        # 3. Load configurations from disk files
        if not os.path.exists(args.config):
            logger.warning(f"Target configuration file '{args.config}' not found. Initializing defaults.")
        
        config_engine = ConfigurationEngine(config_path=args.config)
        app_config = config_engine.get_config()

        # 4. Instantiate the orchestrator engine and run the pipeline
        orchestrator = AutoCorrelationOrchestrator(app_config)
        results = orchestrator.run_pipeline(source_jmx=args.jmx, output_jmx=args.output)

        # 5. Output pipeline execution statistics
        print("\n" + "="*50)
        print("        PIPELINE AUTO-CORRELATION COMPLETE")
        print("="*50)
        print(f" Status:               {results['status']}")
        print(f" Source Samplers:      {results['samplers_count']}")
        print(f" Live Requests Run:    {results['total_requests']}")
        print(f" Baseline Error Rate:  {results['error_percentage']}%")
        print(f" Parameter Candidates: {results['detected_candidates']}")
        print(f" Correlations Applied: {results['applied_correlations']}")
        print(f" Exported Script:      {results['output_script_path']}")
        print("="*50 + "\n")

    except JmeterAutoCorrelatorException as err:
        logger.error(f"Application Execution Error: {str(err)}")
        sys.exit(1)
    except Exception as exc:
        logger.critical(f"Unhandled Runtime Failure: {str(exc)}", exc_info=True)
        sys.exit(2)

if __name__ == "__main__":
    main()