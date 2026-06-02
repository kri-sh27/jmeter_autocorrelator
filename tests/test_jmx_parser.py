"""
JMX Parser Engine Verification Suite.
Validates extraction accuracy against mock XML configuration payloads.
"""

import os
import unittest
from src.parser.jmx_parser import JmxParserEngine
from src.config.exceptions import JmxParsingException

class TestJmxParserEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_jmx_path = "mock_test_script.jmx"
        
        # Construct a valid standard minimalist JMeter XML blueprint script programmatically
        self.raw_jmx_content = """<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan testname="Test Suite Plan" enabled="true">
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments">
        <collectionProp name="Arguments.arguments">
          <elementProp name="host_url" elementType="Argument">
            <stringProp name="Argument.name">host_url</stringProp>
            <stringProp name="Argument.value">api.enterprise.io</stringProp>
          </elementProp>
        </collectionProp>
      </elementProp>
    </TestPlan>
    <hashTree>
      <HTTPSamplerProxy testname="Execute Secure Login" enabled="true">
        <stringProp name="HTTPSampler.domain">api.enterprise.io</stringProp>
        <stringProp name="HTTPSampler.port">443</stringProp>
        <stringProp name="HTTPSampler.protocol">https</stringProp>
        <stringProp name="HTTPSampler.path">/v2/auth/login</stringProp>
        <stringProp name="HTTPSampler.method">POST</stringProp>
        <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
        <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
          <collectionProp name="Arguments.arguments">
            <elementProp name="username" elementType="HTTPargument">
              <stringProp name="Argument.name">username</stringProp>
              <stringProp name="Argument.value">perf_automation_user</stringProp>
            </elementProp>
            <elementProp name="password" elementType="HTTPargument">
              <stringProp name="Argument.name">password</stringProp>
              <stringProp name="Argument.value">SecurePass123!</stringProp>
            </elementProp>
          </collectionProp>
        </elementProp>
      </HTTPSamplerProxy>
      <hashTree/>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
"""
        with open(self.mock_jmx_path, "w", encoding="utf-8") as file_stream:
            file_stream.write(self.raw_jmx_content)

    def tearDown(self) -> None:
        if os.path.exists(self.mock_jmx_path):
            os.remove(self.mock_jmx_path)

    def test_invalid_file_path_throws_parsing_exception(self) -> None:
        with self.assertRaises(JmxParsingException):
            engine = JmxParserEngine("missing_file_target.jmx")
            engine.parse()

    def test_successful_jmx_extraction_sequence(self) -> None:
        engine = JmxParserEngine(self.mock_jmx_path)
        sequence = engine.parse()

        # Validate structural counts
        self.assertEqual(len(sequence), 1)
        
        # Inspect extracted structural models
        sampler = sequence[0]
        self.assertEqual(sampler.sampler_name, "Execute Secure Login")
        self.assertEqual(sampler.domain, "api.enterprise.io")
        self.assertEqual(sampler.protocol, "https")
        self.assertEqual(sampler.method, "POST")
        self.assertEqual(sampler.path, "/v2/auth/login")
        
        # Verify nested argument processing parameters 
        self.assertEqual(len(sampler.arguments), 2)
        self.assertEqual(sampler.arguments[0].name, "username")
        self.assertEqual(sampler.arguments[0].value, "perf_automation_user")

    def test_global_user_defined_variable_extraction(self) -> None:
        engine = JmxParserEngine(self.mock_jmx_path)
        engine.parse()
        global_vars = engine.get_global_variables()
        
        self.assertIn("host_url", global_vars)
        self.assertEqual(global_vars["host_url"], "api.enterprise.io")