"""Application configuration for Phi-3 Stat Studio."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
import os


DEFAULT_LANGUAGE = "zh"
SUPPORTED_LANGUAGES = ["zh", "en"]


@dataclass
class ModelConfig:
    """Configuration for local Ollama model usage."""

    host: str = os.environ.get("OLLAMA_HOST", "http://127.0.0.1")
    port: int = int(os.environ.get("OLLAMA_PORT", 11434))
    model: str = os.environ.get("OLLAMA_MODEL", "phi3:mini")
    request_timeout: int = 60

    def base_url(self) -> str:
        return f"{self.host}:{self.port}"


@dataclass
class PathsConfig:
    """Filesystem paths used by the application."""

    root_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    assets_dir: Path = field(init=False)
    templates_dir: Path = field(init=False)
    reports_dir: Path = field(init=False)
    storage_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        self.assets_dir = self.root_dir / "assets"
        self.templates_dir = self.root_dir / "templates"
        self.reports_dir = self.root_dir / "reports"
        self.storage_dir = self.root_dir / "storage"

        for path in [self.assets_dir, self.templates_dir, self.reports_dir, self.storage_dir]:
            path.mkdir(parents=True, exist_ok=True)


@dataclass
class AppConfig:
    """Top level application configuration."""

    default_language: str = DEFAULT_LANGUAGE
    supported_languages: List[str] = field(default_factory=lambda: SUPPORTED_LANGUAGES.copy())
    model: ModelConfig = field(default_factory=ModelConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    debug: bool = bool(int(os.environ.get("PHI3_STAT_DEBUG", "0")))

    def to_dict(self) -> Dict[str, str]:
        return {
            "default_language": self.default_language,
            "supported_languages": ",".join(self.supported_languages),
            "model_host": self.model.host,
            "model_port": str(self.model.port),
            "model_name": self.model.model,
            "debug": str(self.debug),
        }


CONFIG = AppConfig()


