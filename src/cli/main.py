"""Command-line interface for AI Video Generator."""

import sys
from pathlib import Path
from typing import Optional

import click

from src import __version__
from src.models.video_generator import VideoGenerator
from src.utils.config import get_config, setup_directories
from src.utils.video import create_gif


@click.group()
@click.version_option(version=__version__)
def cli():
    """AI Video Generator - Generate videos from text prompts."""
    pass


@cli.command()
@click.argument("prompt")
@click.option(
    "--output", "-o",
    type=click.Path(),
    help="Output video path",
)
@click.option(
    "--negative-prompt", "-np",
    help="Negative prompt",
)
@click.option(
    "--steps", "-s",
    type=int,
    help="Number of inference steps",
)
@click.option(
    "--guidance", "-g",
    type=float,
    help="Guidance scale",
)
@click.option(
    "--seed", type=int,
    help="Random seed for reproducibility",
)
@click.option(
    "--frames", "-f",
    type=int,
    help="Number of frames",
)
@click.option(
    "--fps", type=int,
    help="Frames per second",
)
@click.option(
    "--width", "-w",
    type=int,
    help="Video width",
)
@click.option(
    "--height", "-h",
    type=int,
    help="Video height",
)
@click.option(
    "--gif",
    is_flag=True,
    help="Also generate a GIF preview",
)
def generate(
    prompt: str,
    output: Optional[str],
    negative_prompt: Optional[str],
    steps: Optional[int],
    guidance: Optional[float],
    seed: Optional[int],
    frames: Optional[int],
    fps: Optional[int],
    width: Optional[int],
    height: Optional[int],
    gif: bool,
):
    """Generate a video from a text prompt."""
    config = get_config()
    setup_directories(config.storage)

    if output is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = str(config.storage.output_dir / f"video_{timestamp}.mp4")

    generator = VideoGenerator()

    click.echo(f"Loading model: {config.model.model_name}")
    generator.load_model()

    click.echo(f"Generating video for: {prompt}")
    click.echo("This may take a few minutes...")

    try:
        frames_list = generator.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            guidance_scale=guidance,
            seed=seed,
        )

        from src.utils.video import frames_to_video
        video_path = frames_to_video(
            frames=frames_list,
            output_path=output,
            fps=fps or config.generation.fps,
        )

        click.echo(f"Video saved to: {video_path}")

        if gif:
            gif_path = Path(output).with_suffix(".gif")
            create_gif(frames_list, gif_path)
            click.echo(f"GIF saved to: {gif_path}")

    except Exception as e:
        click.echo(f"Error generating video: {e}", err=True)
        sys.exit(1)
    finally:
        generator.unload()


@cli.command()
@click.option(
    "--port", "-p",
    type=int,
    help="API port",
)
@click.option(
    "--host",
    default="0.0.0.0",
    help="API host",
)
@click.option(
    "--reload", is_flag=True,
    help="Enable auto-reload",
)
@click.option(
    "--workers", "-w",
    type=int,
    help="Number of workers",
)
def serve(
    port: Optional[int],
    host: Optional[str],
    reload: bool,
    workers: Optional[int],
):
    """Start the API server."""
    config = get_config()

    if port:
        config.api.port = port
    if host:
        config.api.host = host
    if reload:
        config.api.reload = True
    if workers:
        config.api.workers = workers

    from src.api.server import run
    run()


@cli.command()
def info():
    """Show configuration information."""
    config = get_config()

    click.echo("AI Video Generator Configuration")
    click.echo("=" * 40)

    click.echo("\nModel Settings:")
    click.echo(f"  Model: {config.model.model_name}")
    click.echo(f"  Device: {config.model.device}")
    click.echo(f"  Data Type: {config.model.torch_dtype}")
    click.echo(f"  Use Safetensors: {config.model.use_safetensors}")

    click.echo("\nGeneration Settings:")
    click.echo(f"  Inference Steps: {config.generation.num_inference_steps}")
    click.echo(f"  Guidance Scale: {config.generation.guidance_scale}")
    click.echo(f"  Frames: {config.generation.num_frames}")
    click.echo(f"  Resolution: {config.generation.width}x{config.generation.height}")
    click.echo(f"  FPS: {config.generation.fps}")

    click.echo("\nStorage:")
    click.echo(f"  Output: {config.storage.output_dir}")
    click.echo(f"  Cache: {config.storage.cache_dir}")


if __name__ == "__main__":
    cli()