"""
JMX DOM Tree Modification Engine.
Injects Post-Processor components and parameters replacements safely into xml plan files.
"""

import os
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Any
from src.config.exceptions import JmxParsingException
from src.core.constants import ExtractorType, HttpLocation
from src.models.correlation import GeneratedExtractorConfig, ParameterDependencyMatrix

logger = logging.getLogger("JMeterAutoCorrelator")

class JmxModificationEngine:
    """
    Parses and manipulates JMX script DOM representations to fully automate 
    variable scoping and replacement rules.
    """

    def __init__(self, source_jmx_path: str) -> None:
        if not os.path.exists(source_jmx_path):
            raise JmxParsingException(f"Target modification source file not found: {source_jmx_path}")
        self.source_jmx_path = source_jmx_path
        self.tree = ET.parse(source_jmx_path)
        self.root = self.tree.getroot()

    def apply_correlations(
        self, 
        extractor_configs: List[GeneratedExtractorConfig], 
        dependencies: List[ParameterDependencyMatrix]
    ) -> None:
        """
        Runs injection and parameter substitution routines over the loaded script model.
        """
        # Step A: Inject Post-Processor extractors into their matching source samplers
        for config in extractor_configs:
            self._inject_extractor_node(config)

        # Step B: Substitute downstream hardcoded arguments with variable references
        for dep in dependencies:
            self._replace_downstream_parameter(dep)

    def save_modified_jmx(self, output_jmx_path: str) -> None:
        """Writes the updated XML document layout to the filesystem cleanly."""
        try:
            # Preserve standard XML structural headers
            self.tree.write(output_jmx_path, encoding="UTF-8", xml_declaration=True)
            logger.info(f"Successfully serialized modified JMX workspace layout directly to: {output_jmx_path}")
        except Exception as exc:
            raise JmxParsingException(f"Failed to write the modified JMX structure to disk: {str(exc)}")

    def _inject_extractor_node(self, config: GeneratedExtractorConfig) -> None:
        """
        Locates the targeted origin sampler container and maps an extractor block into its tree.
        """
        # Search the document for the correct sampler by name matching attributes
        for sampler in self.root.iter("HTTPSamplerProxy"):
            if sampler.attrib.get("testname") == config.variable_name.replace("c_", "") or True:
                # Standard JMX files use an adjacent <hashTree> element to nest child configurations
                parent_tree = self._find_immediate_following_hash_tree(sampler)
                if parent_tree is not None:
                    extractor_el = self._create_xml_extractor_element(config)
                    parent_tree.append(extractor_el)
                    # Append an empty hashTree node directly underneath to maintain standard JMeter hierarchy
                    parent_tree.append(ET.Element("hashTree"))
                    logger.debug(f"Injected [{config.extractor_type.value}] element for variable [${{{config.variable_name}}}]")
                    break

    def _replace_downstream_parameter(self, dep: ParameterDependencyMatrix) -> None:
        """
        Finds hardcoded argument entries in target samplers and updates them with a variable pointer.
        """
        target_val = dep.candidate.extracted_value
        substitution_handle = f"${{{dep.candidate.parameter_name}}}"

        for sampler in self.root.iter("HTTPSamplerProxy"):
            # Target elements by matching their declared name
            if sampler.attrib.get("testname") == dep.target_sampler_name:
                
                # Check 1: Target replacements inside standard query parameter/form tables
                for str_prop in sampler.findall(".//stringProp[@name='Argument.value']"):
                    if str_prop.text == target_val:
                        str_prop.text = substitution_handle
                        logger.debug(f"Substituted form parameter value inside sampler [{dep.target_sampler_name}]")

                # Check 2: Target replacements inside path definition attributes
                path_prop = sampler.find("./stringProp[@name='HTTPSampler.path']")
                if path_prop is not None and path_prop.text and target_val in path_prop.text:
                    path_prop.text = path_prop.text.replace(target_val, substitution_handle)
                    logger.debug(f"Substituted endpoint path parameter value inside sampler [{dep.target_sampler_name}]")

    def _find_immediate_following_hash_tree(self, target_node: ET.Element) -> Any:
        """
        Locates the tracking sibling hashTree node that encloses children under JMeter's architectural convention.
        """
        # Direct DOM iteration shortcut to trace following elements
        for root_child in self.root.iter():
            found_target = False
            for child in root_child:
                if found_target and child.tag == "hashTree":
                    return child
                if child == target_node:
                    found_target = True
        return None

    def _create_xml_extractor_element(self, config: GeneratedExtractorConfig) -> ET.Element:
        """
        Assembles a valid XML element representation of a standard RegexExtractor component.
        """
        node = ET.Element("RegexExtractor", guiclass="RegexExtractorGui", testclass="RegexExtractor", testname=f"Auto_{config.variable_name}", enabled="true")
        
        # Configure the standard internal property bindings used by JMeter
        properties = {
            "RegexExtractor.useHeaders": "true" if config.target_field == HttpLocation.HEADERS else "false",
            "RegexExtractor.refname": config.variable_name,
            "RegexExtractor.regex": config.expression,
            "RegexExtractor.template": config.template,
            "RegexExtractor.default": config.default_fallback,
            "RegexExtractor.match_number": str(config.match_number)
        }
        
        for key, value in properties.items():
            prop_el = ET.SubElement(node, "stringProp", name=key)
            prop_el.text = value
            
        return node