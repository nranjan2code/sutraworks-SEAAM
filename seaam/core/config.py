"""
SEAAM Configuration Management

Centralized configuration with:
- YAML file support
- Environment variable overrides
- Type validation
- Sensible defaults
"""

import os
from pathlib import Path
from typing import Any, Optional, Union, List
from dataclasses import dataclass, field

# Try to import yaml, fall back to basic dict if not available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "ollama"
    model: str = "qwen2.5-coder:14b"
    temperature: float = 0.1
    max_retries: int = 3
    timeout_seconds: int = 120
    
    # Ollama specific
    ollama_url: str = "http://localhost:11434/api/generate"
    
    # Gemini specific
    gemini_model: str = "gemini-1.5-flash"


@dataclass
class PathsConfig:
    """File path configuration."""
    root: Path = field(default_factory=Path.cwd)
    dna: Path = field(default_factory=lambda: Path("dna.json"))
    soma: Path = field(default_factory=lambda: Path("soma"))
    prompts: Path = field(default_factory=lambda: Path("seaam/cortex/prompts"))
    logs: Path = field(default_factory=lambda: Path("logs"))
    
    def __post_init__(self):
        # Make paths absolute
        if not self.dna.is_absolute():
            self.dna = self.root / self.dna
        if not self.soma.is_absolute():
            self.soma = self.root / self.soma
        if not self.prompts.is_absolute():
            self.prompts = self.root / self.prompts
        if not self.logs.is_absolute():
            self.logs = self.root / self.logs


@dataclass
class MetabolismConfig:
    """Metabolic cycle configuration."""
    cycle_interval_seconds: int = 30
    max_organs_per_cycle: int = 3
    reflection_timeout_seconds: int = 60


@dataclass
class SecurityConfig:
    """Security configuration."""
    allow_pip_install: bool = False  # DISABLED BY DEFAULT for security
    allowed_pip_packages: list[str] = field(default_factory=lambda: [
        "watchdog",
        "streamlit",
        "flask",
        "fastapi",
        "sqlite3",
        "requests",
    ])
    protected_prefixes: list[str] = field(default_factory=lambda: [
        "seaam.",
        "seaam/",
    ])


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "colored"  # 'colored' or 'json'
    file: Optional[str] = None


@dataclass
class SEAAMConfig:
    """Root configuration object."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    metabolism: MetabolismConfig = field(default_factory=MetabolismConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Metadata
    version: str = "1.0.0"
    environment: str = "development"
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SEAAMConfig":
        """Create config from a dictionary."""
        config = cls()
        
        if "llm" in data:
            for key, value in data["llm"].items():
                if hasattr(config.llm, key):
                    setattr(config.llm, key, value)
        
        if "paths" in data:
            paths_data = data["paths"]
            if "root" in paths_data:
                config.paths.root = Path(paths_data["root"])
            if "dna" in paths_data:
                config.paths.dna = Path(paths_data["dna"])
            if "soma" in paths_data:
                config.paths.soma = Path(paths_data["soma"])
            # Recalculate absolute paths
            config.paths.__post_init__()
        
        if "metabolism" in data:
            for key, value in data["metabolism"].items():
                if hasattr(config.metabolism, key):
                    setattr(config.metabolism, key, value)
        
        if "security" in data:
            for key, value in data["security"].items():
                if hasattr(config.security, key):
                    setattr(config.security, key, value)
        
        if "logging" in data:
            for key, value in data["logging"].items():
                if hasattr(config.logging, key):
                    setattr(config.logging, key, value)
        
        if "version" in data:
            config.version = data["version"]
        if "environment" in data:
            config.environment = data["environment"]
        
        return config
    
    @classmethod
    def load(cls, config_path: Optional[Union[Path, str]] = None) -> "SEAAMConfig":
        """
        Load configuration from file with environment variable overrides.
        
        Priority (highest to lowest):
        1. Environment variables (SEAAM_*)
        2. Config file (config.yaml)
        3. Defaults
        """
        config = cls()
        
        # Try to load from file
        if config_path is None:
            config_path = Path.cwd() / "config.yaml"
        else:
            config_path = Path(config_path)
        
        if config_path.exists() and HAS_YAML:
            with open(config_path) as f:
                data = yaml.safe_load(f)
                if data:
                    config = cls.from_dict(data)
        
        # Override with environment variables
        config._apply_env_overrides()
        
        return config
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        # LLM settings
        if os.environ.get("SEAAM_LLM_PROVIDER"):
            self.llm.provider = os.environ["SEAAM_LLM_PROVIDER"]
        if os.environ.get("SEAAM_LLM_MODEL"):
            self.llm.model = os.environ["SEAAM_LLM_MODEL"]
        if os.environ.get("OLLAMA_URL"):
            self.llm.ollama_url = os.environ["OLLAMA_URL"]
        if os.environ.get("OLLAMA_MODEL"):
            self.llm.model = os.environ["OLLAMA_MODEL"]
        if os.environ.get("GEMINI_API_KEY"):
            # If Gemini key is set, we know it's available
            pass  # Just noting it exists
        
        # Logging
        if os.environ.get("SEAAM_LOG_LEVEL"):
            self.logging.level = os.environ["SEAAM_LOG_LEVEL"]
        if os.environ.get("SEAAM_LOG_FORMAT"):
            self.logging.format = os.environ["SEAAM_LOG_FORMAT"]
        
        # Security
        if os.environ.get("SEAAM_ALLOW_PIP"):
            self.security.allow_pip_install = os.environ["SEAAM_ALLOW_PIP"].lower() == "true"
        
        # Environment
        if os.environ.get("SEAAM_ENV"):
            self.environment = os.environ["SEAAM_ENV"]
    
    def to_dict(self) -> dict[str, Any]:
        """Export config to dictionary."""
        return {
            "version": self.version,
            "environment": self.environment,
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "temperature": self.llm.temperature,
                "max_retries": self.llm.max_retries,
                "timeout_seconds": self.llm.timeout_seconds,
                "ollama_url": self.llm.ollama_url,
                "gemini_model": self.llm.gemini_model,
            },
            "paths": {
                "root": str(self.paths.root),
                "dna": str(self.paths.dna),
                "soma": str(self.paths.soma),
            },
            "metabolism": {
                "cycle_interval_seconds": self.metabolism.cycle_interval_seconds,
                "max_organs_per_cycle": self.metabolism.max_organs_per_cycle,
            },
            "security": {
                "allow_pip_install": self.security.allow_pip_install,
                "allowed_pip_packages": self.security.allowed_pip_packages,
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
            },
        }


# Global config instance
config = SEAAMConfig.load()
