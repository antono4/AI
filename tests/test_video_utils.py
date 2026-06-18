"""Tests for video utilities."""

import pytest
import numpy as np
from pathlib import Path
from PIL import Image

from src.utils.video import (
    frames_to_video,
    resize_frames,
    create_gif,
)


@pytest.fixture
def sample_frames():
    """Create sample frames for testing."""
    return [
        Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
        for _ in range(5)
    ]


class TestVideoUtils:
    """Test cases for video utilities."""

    def test_frames_to_video(self, sample_frames, tmp_path):
        """Test converting frames to video."""
        output_path = tmp_path / "output.mp4"

        result = frames_to_video(sample_frames, output_path, fps=8)

        assert Path(result).exists()
        assert Path(result).suffix == ".mp4"

    def test_frames_to_video_creates_directory(self, sample_frames, tmp_path):
        """Test that frames_to_video creates output directory."""
        output_path = tmp_path / "subdir" / "output.mp4"

        result = frames_to_video(sample_frames, output_path)

        assert Path(result).exists()

    def test_frames_to_video_custom_fps(self, sample_frames, tmp_path):
        """Test video with custom fps."""
        output_path = tmp_path / "output.mp4"

        result = frames_to_video(sample_frames, output_path, fps=30)

        assert Path(result).exists()

    def test_resize_frames(self, sample_frames):
        """Test resizing frames."""
        resized = resize_frames(sample_frames, width=50, height=50)

        assert len(resized) == len(sample_frames)
        assert all(f.size == (50, 50) for f in resized)

    def test_resize_frames_preserves_count(self, sample_frames):
        """Test that resize doesn't change frame count."""
        resized = resize_frames(sample_frames, width=200, height=200)

        assert len(resized) == len(sample_frames)

    def test_create_gif(self, sample_frames, tmp_path):
        """Test creating GIF from frames."""
        output_path = tmp_path / "output.gif"

        result = create_gif(sample_frames, output_path, duration=100)

        assert Path(result).exists()
        assert Path(result).suffix == ".gif"

    def test_create_gif_custom_duration(self, sample_frames, tmp_path):
        """Test GIF with custom duration."""
        output_path = tmp_path / "output.gif"

        result = create_gif(sample_frames, output_path, duration=500)

        assert Path(result).exists()

    def test_create_gif_creates_directory(self, sample_frames, tmp_path):
        """Test that create_gif creates output directory."""
        output_path = tmp_path / "subdir" / "output.gif"

        result = create_gif(sample_frames, output_path)

        assert Path(result).exists()

    def test_frames_to_video_with_string_path(self, sample_frames, tmp_path):
        """Test frames_to_video with string path."""
        output_path = str(tmp_path / "output.mp4")

        result = frames_to_video(sample_frames, output_path)

        assert Path(result).exists()