"""FastAPI server for video generation service."""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from src import __version__
from src.api.jobs import job_manager, JobStatus
from src.api.schemas import (
    GenerationRequest,
    GenerationResponse,
    HealthResponse,
    JobStatus as JobStatusSchema,
)
from src.models.video_generator import VideoGenerator
from src.utils.config import get_config, setup_directories


config = get_config()
generator: Optional[VideoGenerator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global generator

    setup_directories(config.storage)

    generator = VideoGenerator()

    asyncio.create_task(cleanup_task())

    yield

    if generator:
        generator.unload()


app = FastAPI(
    title="AI Video Generator API",
    description="Production-ready AI Video Generation Service using Hugging Face Transformers",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=generator.is_loaded if generator else False,
        model_name=config.model.model_name,
        device=config.model.device,
        version=__version__,
    )


@app.post("/generate", response_model=GenerationResponse)
async def generate_video(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
):
    """Generate a video from text prompt."""
    job = job_manager.create_job(
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        num_inference_steps=request.num_inference_steps,
        guidance_scale=request.guidance_scale,
        seed=request.seed,
        num_frames=request.num_frames,
    )

    background_tasks.add_task(job_manager.process_job, job)

    return GenerationResponse(
        job_id=job.job_id,
        status=job.status.value,
        message="Video generation started",
    )


@app.get("/jobs/{job_id}", response_model=JobStatusSchema)
async def get_job_status(job_id: str):
    """Get job status by ID."""
    job = await job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusSchema(
        job_id=job.job_id,
        status=job.status.value,
        progress=job.progress,
        video_url=f"/download/{job.job_id}" if job.video_path else None,
        error=job.error,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


@app.get("/jobs", response_model=list[JobStatusSchema])
async def list_jobs():
    """List all jobs."""
    jobs = await job_manager.get_all_jobs()
    return [
        JobStatusSchema(
            job_id=job.job_id,
            status=job.status.value,
            progress=job.progress,
            video_url=f"/download/{job.job_id}" if job.video_path else None,
            error=job.error,
            created_at=job.created_at,
            completed_at=job.completed_at,
        )
        for job in jobs
    ]


@app.get("/download/{job_id}")
async def download_video(job_id: str):
    """Download generated video."""
    job = await job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETED or not job.video_path:
        raise HTTPException(status_code=400, detail="Video not ready")

    from pathlib import Path
    video_path = Path(job.video_path)

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"{job_id}.mp4",
    )


async def cleanup_task():
    """Periodic cleanup task."""
    while True:
        await asyncio.sleep(3600)
        await job_manager.cleanup_old_jobs()


def run():
    """Run the server."""
    uvicorn.run(
        "src.api.server:app",
        host=config.api.host,
        port=config.api.port,
        workers=config.api.workers,
        reload=config.api.reload,
        log_level=config.api.log_level,
    )


if __name__ == "__main__":
    run()