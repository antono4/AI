"""Video processing utilities."""

import imageio
import numpy as np
from pathlib import Path
from PIL import Image
from typing import Union


def frames_to_video(
    frames: list[Image.Image],
    output_path: Union[str, Path],
    fps: int = 8,
    quality: int = 8,
) -> str:
    """Convert a list of PIL Images to a video file.

    Args:
        frames: List of PIL Image frames
        output_path: Path to save the video
        fps: Frames per second
        quality: Video quality (1-10, higher is better)

    Returns:
        Path to the saved video file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    frames_np = [np.array(frame) for frame in frames]

    writer = imageio.get_writer(
        output_path,
        fps=fps,
        codec='libx264',
        quality=quality,
        pixelformat='yuv420p',
    )

    for frame in frames_np:
        writer.append_data(frame)

    writer.close()

    return str(output_path)


def video_to_frames(
    video_path: Union[str, Path],
    output_dir: Union[str, Path],
) -> list[str]:
    """Extract frames from a video file.

    Args:
        video_path: Path to the video file
        output_dir: Directory to save extracted frames

    Returns:
        List of paths to extracted frame images
    """
    import cv2

    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    frame_paths = []

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)

        frame_path = output_dir / f"frame_{frame_idx:05d}.png"
        frame_pil.save(frame_path)
        frame_paths.append(str(frame_path))

        frame_idx += 1

    cap.release()
    return frame_paths


def resize_frames(
    frames: list[Image.Image],
    width: int,
    height: int,
) -> list[Image.Image]:
    """Resize frames to specified dimensions.

    Args:
        frames: List of PIL Image frames
        width: Target width
        height: Target height

    Returns:
        List of resized frames
    """
    return [frame.resize((width, height), Image.Resampling.LANCZOS) for frame in frames]


def add_watermark(
    frames: list[Image.Image],
    watermark_text: str,
    position: str = "bottom-right",
) -> list[Image.Image]:
    """Add watermark to video frames.

    Args:
        frames: List of PIL Image frames
        watermark_text: Text for watermark
        position: Position of watermark (bottom-right, bottom-left, top-right, top-left)

    Returns:
        List of watermarked frames
    """
    from PIL import ImageDraw, ImageFont

    watermarked_frames = []

    for frame in frames:
        draw = ImageDraw.Draw(frame)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except (OSError, IOError):
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        margin = 10

        positions = {
            "bottom-right": (frame.width - text_width - margin, frame.height - text_height - margin),
            "bottom-left": (margin, frame.height - text_height - margin),
            "top-right": (frame.width - text_width - margin, margin),
            "top-left": (margin, margin),
        }

        pos = positions.get(position, positions["bottom-right"])

        draw.text(
            pos,
            watermark_text,
            fill=(255, 255, 255, 128),
            font=font,
        )

        watermarked_frames.append(frame)

    return watermarked_frames


def create_gif(
    frames: list[Image.Image],
    output_path: Union[str, Path],
    duration: int = 100,
    loop: int = 0,
) -> str:
    """Create an animated GIF from frames.

    Args:
        frames: List of PIL Image frames
        output_path: Path to save the GIF
        duration: Duration per frame in milliseconds
        loop: Number of loops (0 = infinite)

    Returns:
        Path to the saved GIF file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop,
    )

    return str(output_path)