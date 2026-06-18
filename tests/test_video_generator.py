"""Tests for video generator model."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import numpy as np

from src.models.video_generator import VideoGenerator
from src.utils.config import ModelConfig, GenerationConfig, StorageConfig


@pytest.fixture
def model_config():
    """Create test model config."""
    return ModelConfig(
        model_name="damo-vilab/text-to-video-ms-1.7b",
        device="cpu",
        torch_dtype="float32",
    )


@pytest.fixture
def generation_config():
    """Create test generation config."""
    return GenerationConfig(
        num_inference_steps=5,
        guidance_scale=7.5,
        num_frames=4,
        height=128,
        width=128,
    )


@pytest.fixture
def storage_config(tmp_path):
    """Create test storage config."""
    return StorageConfig(
        output_dir=tmp_path / "outputs",
        cache_dir=tmp_path / "cache",
        temp_dir=tmp_path / "temp",
    )


@pytest.fixture
def generator(model_config, generation_config, storage_config):
    """Create video generator instance."""
    return VideoGenerator(
        model_config=model_config,
        generation_config=generation_config,
        storage_config=storage_config,
    )


class TestVideoGenerator:
    """Test cases for VideoGenerator class."""

    def test_initialization(self, generator, model_config, generation_config, storage_config):
        """Test generator initialization."""
        assert generator.model_config == model_config
        assert generator.generation_config == generation_config
        assert generator.storage_config == storage_config
        assert generator._pipeline is None

    def test_get_torch_dtype(self, generator):
        """Test torch dtype conversion."""
        assert generator._get_torch_dtype() is not None

    def test_is_loaded_property(self, generator):
        """Test is_loaded property."""
        assert generator.is_loaded is False

    @patch("src.models.video_generator.DiffusionPipeline")
    def test_load_model(self, mock_pipeline, generator):
        """Test model loading."""
        mock_pipeline.from_pretrained.return_value = Mock()

        generator.load_model()

        assert generator.is_loaded is True
        mock_pipeline.from_pretrained.assert_called_once()

    def test_unload(self, generator):
        """Test model unloading."""
        generator._pipeline = Mock()
        generator.unload()

        assert generator.is_loaded is False

    @patch("src.models.video_generator.DiffusionPipeline")
    def test_generate_returns_frames(self, mock_pipeline, generator):
        """Test generate returns list of frames."""
        mock_frames = [
            Image.fromarray(np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8))
            for _ in range(4)
        ]

        mock_instance = Mock()
        mock_instance.return_value = Mock(frames=[mock_frames])
        mock_pipeline.from_pretrained.return_value = mock_instance

        frames = generator.generate(prompt="test prompt")

        assert isinstance(frames, list)
        assert all(isinstance(f, Image.Image) for f in frames)

    @patch("src.models.video_generator.DiffusionPipeline")
    def test_generate_with_seed(self, mock_pipeline, generator):
        """Test generation with seed for reproducibility."""
        mock_frames = [
            Image.fromarray(np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8))
            for _ in range(4)
        ]

        mock_instance = Mock()
        mock_instance.return_value = Mock(frames=[mock_frames])
        mock_pipeline.from_pretrained.return_value = mock_instance

        frames1 = generator.generate(prompt="test", seed=42)
        frames2 = generator.generate(prompt="test", seed=42)

        assert len(frames1) == len(frames2)

    @patch("src.models.video_generator.DiffusionPipeline")
    @patch("src.utils.video.frames_to_video")
    def test_generate_to_video(self, mock_frames_to_video, mock_pipeline, generator, tmp_path):
        """Test video generation to file."""
        mock_frames = [
            Image.fromarray(np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8))
            for _ in range(4)
        ]

        mock_instance = Mock()
        mock_instance.return_value = Mock(frames=[mock_frames])
        mock_pipeline.from_pretrained.return_value = mock_instance

        output_path = tmp_path / "test_video.mp4"
        mock_frames_to_video.return_value = str(output_path)

        result = generator.generate_to_video(
            prompt="test",
            output_path=str(output_path),
        )

        assert result == str(output_path)
        mock_frames_to_video.assert_called_once()