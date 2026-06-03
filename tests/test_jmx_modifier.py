"""
JMX Modifier Engine Verification Suite.
Validates structural DOM node injection and variable parameter substitution.
"""

import os
import unittest
import xml.etree.ElementTree as ET
from src.core.constants import CorrelationType, ExtractorType, HttpLocation
from src.models.correlation import GeneratedExtractorConfig, CorrelationCandidate, ParameterDependencyMatrix
from src.modifier.jmx_modifier import JmxModificationEngine

class TestJmxModificationEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.test_jmx = "modifier_sandbox.jmx"
        self.output_jmx = "modifier_output.jmx"
        
        self.raw_xml_blueprint = """<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2">
  <hashTree>
    <HTTPSamplerProxy testname="Login_Sampler" enabled="true">
      <stringProp name="HTTPSampler.path">/auth/login</stringProp>
    </HTTPSamplerProxy>
    <hashTree>
      </hashTree>
    <HTTPSamplerProxy testname="Checkout_Sampler" enabled="true">
      <stringProp name="HTTPSampler.path">/api/checkout?session=XYZ_TOKEN_99</stringProp>
    </HTTPSamplerProxy>
    <hashTree/>
  </hashTree>
</jmeterTestPlan>
"""
        with open(self.test_jmx, "w", encoding="utf-8") as f:
            f.write(self.raw_xml_blueprint)

        # Setup standard input variables to test the modification run
        self.mock_extractor = GeneratedExtractorConfig(
            variable_name="c_session_token",
            extractor_type=ExtractorType.REGEX,
            target_field=HttpLocation.BODY,
            expression="token\":\"(.*?)\"",
            template="$1$",
            match_number=1,
            default_fallback="NOT_FOUND"
        )

        self.mock_candidate = CorrelationCandidate(
            parameter_name="c_session_token",
            extracted_value="XYZ_TOKEN_99",
            source_sampler_id="sampler_step_0",
            source_sampler_name="Login_Sampler",
            location=HttpLocation.BODY,
            correlation_type=CorrelationType.SESSION_ID,
            extractor_type=ExtractorType.REGEX,
            extraction_expression=".*",
            confidence_score=1.0
        )

        self.mock_dependency = ParameterDependencyMatrix(
            candidate=self.mock_candidate,
            target_sampler_id="sampler_step_1",
            target_sampler_name="Checkout_Sampler",
            target_location=HttpLocation.BODY,
            target_parameter_key="session",
            usage_context_snippet="/api/checkout?session=XYZ_TOKEN_99"
        )

    def tearDown(self) -> None:
        for path in [self.test_jmx, self.output_jmx]:
            if os.path.exists(path):
                os.remove(path)

    def test_structural_jmx_modification_and_injection(self) -> None:
        modifier = JmxModificationEngine(self.test_jmx)
        modifier.apply_correlations([self.mock_extractor], [self.mock_dependency])
        modifier.save_modified_jmx(self.output_jmx)
        
        # Parse the modified output file to verify its structure
        updated_tree = ET.parse(self.output_jmx)
        updated_root = updated_tree.getroot()
        
        # Verify that the new RegexExtractor component was successfully injected
        has_extractor = any(el.tag == "RegexExtractor" for el in updated_root.iter())
        self.assertTrue(has_extractor)
        
        # Verify that the hardcoded value was updated with the variable reference
        checkout_sampler = [el for el in updated_root.iter("HTTPSamplerProxy") if el.attrib.get("testname") == "Checkout_Sampler"][0]
        path_text = checkout_sampler.find("./stringProp[@name='HTTPSampler.path']").text
        self.assertEqual(path_text, "/api/checkout?session=${c_session_token}")