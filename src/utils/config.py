"""Configuration management for AI Video Generator."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelConfig(BaseSettings):
    """Configuration for AI model settings."""

    model_name: str = Field(
        default="damo-vilab/text-to-video-ms-1.7b",
        description="Hugging Face model name for video generation",
    )
    device: Literal["cuda", "mps", "cpu"] = Field(
        default="cuda",
        description="Device to run inference on",
    )
    torch_dtype: Literal["float32", "float16", "bfloat16"] = Field(
        default="float16",
        description="Torch data type for model weights",
    )
    use_safetensors: bool = Field(
        default=True,
        description="Use safetensors for model loading",
    )
    enable_xformers: bool = Field(
        default=False,
        description="Enable xformers memory efficient attention",
    )

    model_config = SettingsConfigDict(env_prefix="MODEL_")


class GenerationConfig(BaseSettings):
    """Configuration for video generation parameters."""

    num_inference_steps: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Number of denoising steps",
    )
    guidance_scale: float = Field(
        default=7.5,
        ge=1.0,
        le=20.0,
        description="Classifier-free guidance scale",
    )
    num_frames: int = Field(
        default=16,
        ge=8,
        le=64,
        description="Number of frames in generated video",
    )
    height: int = Field(
        default=256,
        description="Video height in pixels",
    )
    width: int = Field(
        default=256,
        description="Video width in pixels",
    )
    fps: int = Field(
        default=8,
        ge=1,
        le=60,
        description="Frames per second for output video",
    )

    model_config = SettingsConfigDict(env_prefix="GEN_")


class APIConfig(BaseSettings):
    """Configuration for API service."""

    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, ge=1, le=65535, description="API port")
    workers: int = Field(default=1, ge=1, description="Number of workers")
    reload: bool = Field(default=False, description="Enable auto-reload")
    log_level: Literal["debug", "info", "warning", "error"] = Field(
        default="info", description="Log level"
    )
    max_concurrent_requests: int = Field(
        default=5, ge=1, description="Maximum concurrent generation requests"
    )
    timeout_seconds: int = Field(
        default=300, ge=60, description="Request timeout in seconds"
    )

    model_config = SettingsConfigDict(env_prefix="API_")


class StorageConfig(BaseSettings):
    """Configuration for storage paths."""

    output_dir: Path = Field(
        default=Path("./outputs"),
        description="Directory for generated videos",
    )
    cache_dir: Path = Field(
        default=Path("./cache"),
        description="Directory for model cache",
    )
    temp_dir: Path = Field(
        default=Path("./temp"),
        description="Directory for temporary files",
    )

    model_config = SettingsConfigDict(env_prefix="STORAGE_")


class AppConfig(BaseSettings):
    """Main application configuration."""

    model: ModelConfig = Field(default_factory=ModelConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )


def get_config() -> AppConfig:
    """Get application configuration singleton."""
    return AppConfig()


def setup_directories(config: StorageConfig) -> None:
    """Create necessary directories if they don't exist."""
    config.output_dir.mkdir(parents=True, exist_ok=True)
    config.cache_dir.mkdir(parents=True, exist_ok=True)
    config.temp_dir.mkdir(parents=True, exist_ok=True)