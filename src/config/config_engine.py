"""
Application Configuration Validation Engine.
Converts schema runtime constraints into strict type-safe Pydantic matrices.
"""

import os
from typing import Optional
import yaml
from pydantic import BaseModel, Field, DirectoryPath, FilePath
from src.config.exceptions import ConfigurationException

class JmeterConfig(BaseModel):
    path: str = Field(..., description="Absolute path to the executable local JMeter binary.")
    version: str = Field(default="5.6.3")
    max_heap: str = Field(default="2g")
    min_heap: str = Field(default="1g")
    timeout_seconds: int = Field(default=1800, ge=60)

class CorrelationConfig(BaseModel):
    min_confidence_score: float = Field(default=0.60, ge=0.0, le=1.0)
    auto_replace: bool = Field(default=True)
    backup_jmx: bool = Field(default=True)
    naming_convention: str = Field(default="c_${param_name}")

class ReportingConfig(BaseModel):
    enabled: bool = Field(default=True)
    output_dir: str = Field(default="./reports")
    format: str = Field(default="html")
    theme: str = Field(default="dark")

class LoggingConfig(BaseModel):
    level: str = Field(default="INFO")
    log_to_file: bool = Field(default=True)
    file_path: str = Field(default="./logs/autocorrelator.log")
    max_bytes: int = Field(default=10485760, gt=0)
    backup_count: int = Field(default=5, ge=0)

class ApplicationConfiguration(BaseModel):
    jmeter: JmeterConfig
    correlation: CorrelationConfig
    reporting: ReportingConfig
    logging: LoggingConfig

    @classmethod
    def load_from_yaml(cls, path_to_yaml: str) -> "ApplicationConfiguration":
        """
        Parses external YAML payload safely into immutable domain schemas.
        """
        if not os.path.exists(path_to_yaml):
            raise ConfigurationException(f"Target system configuration map file not found: {path_to_yaml}")
        
        try:
            with open(path_to_yaml, 'r', encoding='utf-8') as stream:
                raw_data = yaml.safe_load(stream)
            return cls(**raw_data)
        except Exception as exc:
            raise ConfigurationException(f"Fatal compilation error processing App Configuration schema: {str(exc)}")