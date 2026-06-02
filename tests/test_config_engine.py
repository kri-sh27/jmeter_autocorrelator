"""
Configuration Pipeline Verification Tests.
"""

import os
import unittest
import yaml
from src.config.config_engine import ApplicationConfiguration
from src.config.exceptions import ConfigurationException

class TestConfigurationEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.valid_yaml_path = "test_valid_config.yaml"
        self.invalid_yaml_path = "test_invalid_config.yaml"
        
        self.valid_data = {
            "jmeter": {"path": "/opt/jmeter/bin/jmeter", "version": "5.6.3", "max_heap": "2g", "min_heap": "1g", "timeout_seconds": 1800},
            "correlation": {"min_confidence_score": 0.75, "auto_replace": True, "backup_jmx": True, "naming_convention": "c_${param_name}"},
            "reporting": {"enabled": True, "output_dir": "./out", "format": "html", "theme": "light"},
            "logging": {"level": "DEBUG", "log_to_file": False, "file_path": "x.log", "max_bytes": 1000, "backup_count": 1}
        }
        
        with open(self.valid_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.valid_data, f)

    def tearDown(self) -> None:
        for path in [self.valid_yaml_path, self.invalid_yaml_path]:
            if os.path.exists(path):
                os.remove(path)

    def test_successful_config_parse(self) -> None:
        config = ApplicationConfiguration.load_from_yaml(self.valid_yaml_path)
        self.assertEqual(config.jmeter.path, "/opt/jmeter/bin/jmeter")
        self.assertEqual(config.correlation.min_confidence_score, 0.75)
        self.assertFalse(config.logging.log_to_file)

    def test_missing_file_throws_exception(self) -> None:
        with self.assertRaises(ConfigurationException):
            ApplicationConfiguration.load_from_yaml("non_existent_file.yaml")

    def test_invalid_types_throw_exception(self) -> None:
        bad_data = self.valid_data.copy()
        bad_data["correlation"]["min_confidence_score"] = 5.5  # Boundary violation (max 1.0)
        
        with open(self.invalid_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(bad_data, f)
            
        with self.assertRaises(ConfigurationException):
            ApplicationConfiguration.load_from_yaml(self.invalid_yaml_path)