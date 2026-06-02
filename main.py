"""
Central Application Bootstrapper.
Parses CLI statements to coordinate system configuration and execution context.
"""

import sys
import argparse
import logging
from src.config.config_engine import ApplicationConfiguration
from src.core.logging_infra import LoggingInfrastructure
from src.config.exceptions import AutoCorrelatorException

def bootstrap_cli() -> argparse.Namespace:
    """
    Constructs and processes explicit terminal parameters.
    """
    parser = argparse.ArgumentParser(
        description="Enterprise Production-Grade JMeter Dynamic Load Test Auto-Correlation Automation Engine Framework."
    )
    parser.add_argument(
        "--jmx",
        required=True,
        help="Path to the source, un-correlated Apache JMeter project XML descriptor asset."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Target filepath to write out the fully refactored, dynamic correlation project configuration."
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Location map parsing settings configuration overrides framework file."
    )
    return parser.parse_parse_args() if hasattr(parser, 'parse_parse_args') else parser.parse_args()

def main() -> None:
    """
    System entry point. Orchestrates structural initializations and handles system exceptions.
    """
    args = bootstrap_cli()
    
    try:
        # Load System Settings Matrix
        app_config = ApplicationConfiguration.load_from_yaml(args.config)
        
        # Instantiate System Logger Framework Interfacing
        logger = LoggingInfrastructure.setup(app_config.logging.model_dump())
        
        logger.info("Initializing Enterprise JMeter Auto-Correlator Core Orchestration Stack Engine.")
        logger.info(f"Target Source JMX Script Reference Path: {args.jmx}")
        logger.info(f"Target Generation Structural Export File Location: {args.output}")
        
        # Core Subsystem Engines execute in subsequent phases...
        logger.info("Phase 1 Project Foundation Framework Bootstrapped Successfully.")
        
    except AutoCorrelatorException as error_context:
        print(f"Operational Exception Interrupt Occurred Context [{error_context.context}]: {error_context.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as fatal_unhandled:
        print(f"Fatal Structural Global Integration Failure Unhandled: {str(fatal_unhandled)}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()