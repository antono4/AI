"""Video generation model using Hugging Face Diffusers."""

import torch
from diffusers import (
    DiffusionPipeline,
    StableVideoDiffusionPipeline,
    AutoencoderKL,
)
from diffusers.utils import export_to_video
from PIL import Image
from typing import Optional, List
import logging

from src.utils.config import ModelConfig, GenerationConfig, StorageConfig

logger = logging.getLogger(__name__)


class VideoGenerator:
    """AI Video Generator using Hugging Face Diffusers."""

    # Supported models
    SUPPORTED_MODELS = {
        "text-to-video": [
            "damo-vilab/text-to-video-ms-1.7b",
            "damo-vilab/text-to-video-ms-1.7b-unofficial",
            "modelscope/text-to-video-ms",
            "stabilityai/stable-diffusion-xl-base-1.0",
        ],
        "video-to-video": [
            "stabilityai/stable-video-diffusion-img2vid",
            "stabilityai/stable-video-diffusion",
        ],
    }

    def __init__(
        self,
        model_config: Optional[ModelConfig] = None,
        generation_config: Optional[GenerationConfig] = None,
        storage_config: Optional[StorageConfig] = None,
    ):
        """Initialize the video generator."""
        self.model_config = model_config or ModelConfig()
        self.generation_config = generation_config or GenerationConfig()
        self.storage_config = storage_config or StorageConfig()
        self._pipeline: Optional[DiffusionPipeline] = None
        self._model_type = self._detect_model_type()

    def _detect_model_type(self) -> str:
        """Detect the type of model based on model name."""
        model_name = self.model_config.model_name.lower()
        
        if "stable-video" in model_name or "video-diffusion" in model_name:
            return "video-to-video"
        return "text-to-video"

    def _get_torch_dtype(self) -> torch.dtype:
        """Get torch dtype from config string."""
        dtype_map = {
            "float32": torch.float32,
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
        }
        return dtype_map.get(self.model_config.torch_dtype, torch.float16)

    def load_model(self) -> None:
        """Load the diffusion model pipeline."""
        if self._pipeline is not None:
            logger.info("Model already loaded")
            return

        dtype = self._get_torch_dtype()
        device = self.model_config.device
        model_name = self.model_config.model_name

        logger.info(f"Loading model: {model_name}")

        try:
            self._pipeline = DiffusionPipeline.from_pretrained(
                model_name,
                torch_dtype=dtype,
                safety_checker=None,
                use_safetensors=self.model_config.use_safetensors,
                cache_dir=str(self.storage_config.cache_dir),
            )

            # Enable optimizations
            if self.model_config.enable_xformers:
                try:
                    self._pipeline.enable_xformers_memory_efficient_attention()
                except Exception as e:
                    logger.warning(f"xformers not available: {e}")

            self._pipeline = self._pipeline.to(device)

            if device == "cuda" and torch.cuda.is_available():
                self._pipeline.enable_model_cpu_offload()

            self._pipeline.enable_attention_slicing()
            logger.info("Model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
        num_frames: Optional[int] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
    ) -> List[Image.Image]:
        """Generate video frames from a text prompt."""
        if self._pipeline is None:
            self.load_model()

        # Setup generator
        if seed is not None:
            generator = torch.Generator(device=self.model_config.device)
            generator.manual_seed(seed)
        else:
            generator = None

        # Get parameters
        steps = num_inference_steps or self.generation_config.num_inference_steps
        guidance = guidance_scale or self.generation_config.guidance_scale
        frames = num_frames or self.generation_config.num_frames
        h = height or self.generation_config.height
        w = width or self.generation_config.width

        logger.info(f"Generating: {prompt[:50]}...")

        output = self._pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            guidance_scale=guidance,
            num_frames=frames,
            height=h,
            width=w,
            generator=generator,
        )

        # Extract frames
        if hasattr(output, 'frames'):
            frames_list = output.frames[0]
        elif hasattr(output, 'video'):
            frames_list = output.video[0]
        else:
            frames_list = output

        return frames_list

    def generate_to_video(
        self,
        prompt: str,
        output_path: str,
        fps: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Generate a video and save it to file."""
        frames = self.generate(prompt, **kwargs)
        fps_value = fps or self.generation_config.fps
        
        # Save video using diffusers utility
        video_path = export_to_video(frames, output_path, fps=fps_value)
        logger.info(f"Video saved: {video_path}")
        return video_path

    def generate_to_gif(
        self,
        prompt: str,
        output_path: str,
        fps: int = 12,
        **kwargs,
    ) -> str:
        """Generate a video and save as GIF."""
        frames = self.generate(prompt, **kwargs)
        
        if frames:
            # Resize for GIF
            resized = [f.copy() for f in frames]
            for i, frame in enumerate(resized):
                frame.thumbnail((512, 512), Image.Resampling.LANCZOS)
                resized[i] = frame
            
            resized[0].save(
                output_path,
                save_all=True,
                append_images=resized[1:],
                duration=int(1000 / fps),
                loop=0,
            )
            logger.info(f"GIF saved: {output_path}")
            return output_path
        
        raise ValueError("No frames generated")

    def get_model_info(self) -> dict:
        """Get model information."""
        return {
            "model_name": self.model_config.model_name,
            "model_type": self._model_type,
            "device": self.model_config.device,
            "is_loaded": self.is_loaded,
        }

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._pipeline is not None

    def unload(self) -> None:
        """Unload model from memory."""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Model unloaded")
