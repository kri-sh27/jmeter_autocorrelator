"""
JMeter Extractor Component Generation Engine.
Transforms dynamic value traces into valid, structured JMeter post-processor parameter maps.
"""

import re
import html
import logging
from typing import List, Dict, Any, Optional
from src.core.constants import ExtractorType, HttpLocation, CorrelationType
from src.models.correlation import ParameterDependencyMatrix, GeneratedExtractorConfig

logger = logging.getLogger("JMeterAutoCorrelator")

class ExtractorGeneratorEngine:
    """
    Generates tailored post-processor configuration definitions based on evaluated data 
    dependency flows, tracking structural syntax patterns automatically.
    """

    def __init__(self, variable_naming_template: str = "c_{param_name}") -> None:
        self.naming_template = variable_naming_template

    def generate_extractor(self, dependency: ParameterDependencyMatrix) -> GeneratedExtractorConfig:
        """
        Evaluates cross-reference metrics to construct an optimal execution post-processor definition.
        """
        candidate = dependency.candidate
        raw_value = candidate.extracted_value
        source_location = candidate.location
        
        # Calculate a safe variable identifier handle matching system naming standards
        clean_param_name = candidate.parameter_name.replace("c_", "")
        var_name = self.naming_template.replace("${param_name}", clean_param_name)

        # Route matching patterns by extractor type configurations
        ext_type = candidate.extractor_type
        expression = ""
        template_str = "$1$"

        if ext_type == ExtractorType.JSON:
            expression = self._generate_json_path_expression(dependency, clean_param_name)
            template_str = ""
        elif ext_type == ExtractorType.REGEX:
            expression = self._generate_regex_boundary_expression(candidate.extraction_expression, raw_value)
        else:
            # Safe absolute boundary fallback if context structures deviate
            ext_type = ExtractorType.REGEX
            expression = f"({re.escape(raw_value)})"

        logger.debug(f"Generated extraction rule map framework for parameter [{var_name}] via type [{ext_type.value}].")
        
        return GeneratedExtractorConfig(
            variable_name=var_name,
            extractor_type=ext_type,
            target_field=source_location,
            expression=expression,
            template=template_str,
            match_number=1,
            default_fallback=f"{var_name}_NOT_FOUND"
        )

    def _generate_json_path_expression(self, dep: ParameterDependencyMatrix, param_key: str) -> str:
        """
        Generates standard JSONPath navigation parameters from structural metadata blocks.
        """
        # Look for explicit payload reference tags first
        meta_key = dep.target_parameter_key or param_key
        if meta_key:
            return f"$..{meta_key}"
        return "$..id"

    def _generate_regex_boundary_expression(self, base_expression: str, literal_value: str) -> str:
        """
        Wraps literal string boundaries into strict, safe regular expression match sequences.
        """
        if base_expression and base_expression != ".*":
            # If the detection loop already compiled a valid lookahead structure, preserve it
            if "(" in base_expression and ")" in base_expression:
                return base_expression
            return f"({base_expression})"
            
        # Fallback to generating an absolute positional literal grouping capture match pattern
        escaped_val = re.escape(literal_value)
        return f"({escaped_val})"