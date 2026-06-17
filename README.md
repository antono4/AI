# AI Video Generator

Production-ready AI Video Generator using Hugging Face Transformers and Diffusers.

## Features

- **Text-to-Video Generation**: Generate videos from text prompts using state-of-the-art diffusion models
- **Production-Ready API**: FastAPI-based REST API with async job management
- **CLI Interface**: Easy-to-use command-line tool for quick generation
- **Docker Support**: Containerized deployment with GPU support
- **Configurable**: Extensive configuration options for fine-tuning generation
- **Comprehensive Testing**: Unit tests with high coverage

## Supported Models

- [damo-vilab/text-to-video-ms-1.7b](https://huggingface.co/damo-vilab/text-to-video-ms-1.7b) (default)
- [stabilityai/stable-video-diffusion](https://huggingface.co/stabilityai/stable-video-diffusion)
- [modelscope/text-to-video-ms](https://huggingface.co/modelscope/text-to-video-ms)

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/antono4/AI.git
cd AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Using Docker

```bash
# Build the Docker image
docker build -t ai-video-generator .

# Run with GPU support
docker run --gpus all -p 8000:8000 ai-video-generator

# Or use Docker Compose
docker-compose up -d
```

## Usage

### CLI

```bash
# Generate a video from a text prompt
video-gen generate "A cat playing piano in a jazz club"

# With custom parameters
video-gen generate "A sunset over the ocean" \
  --steps 30 \
  --guidance 9.5 \
  --frames 24 \
  --fps 12 \
  --seed 42 \
  --output my_video.mp4

# Generate a GIF preview
video-gen generate "A flowing river" --gif

# Start API server
video-gen serve --port 8000

# Show configuration
video-gen info
```

### Python API

```python
from src.models.video_generator import VideoGenerator
from src.utils.video import frames_to_video

# Initialize generator
generator = VideoGenerator()

# Load model
generator.load_model()

# Generate frames
frames = generator.generate(
    prompt="A serene lake at sunset",
    num_inference_steps=25,
    guidance_scale=7.5,
    seed=42,
)

# Save as video
video_path = frames_to_video(frames, "output.mp4", fps=8)
```

### REST API

Start the server:

```bash
python -m src.api.server
# or
video-gen serve
```

API endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Generate video
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cat in space", "num_inference_steps": 25}'

# Check job status
curl http://localhost:8000/jobs/{job_id}

# Download video
curl http://localhost:8000/download/{job_id} -o video.mp4
```

## Configuration

### Environment Variables

```bash
# Model settings
MODEL__MODEL_NAME=damo-vilab/text-to-video-ms-1.7b
MODEL__DEVICE=cuda  # cuda, mps, cpu
MODEL__TORCH_DTYPE=float16  # float32, float16, bfloat16

# Generation settings
GEN__NUM_INFERENCE_STEPS=25
GEN__GUIDANCE_SCALE=7.5
GEN__NUM_FRAMES=16
GEN__HEIGHT=256
GEN__WIDTH=256
GEN__FPS=8

# API settings
API__HOST=0.0.0.0
API__PORT=8000
API__WORKERS=1
API__LOG_LEVEL=info

# Storage
STORAGE__OUTPUT_DIR=./outputs
STORAGE__CACHE_DIR=./cache
STORAGE__TEMP_DIR=./temp
```

Or use a `.env` file:

```bash
cp .env.example .env
# Edit .env with your settings
```

## Development

### Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_video_generator.py
```

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint
flake8 src tests

# Type check
mypy src
```

## Architecture

```
ai-video-generator/
├── src/
│   ├── models/          # AI model implementations
│   ├── utils/           # Utility functions
│   ├── api/             # FastAPI server and endpoints
│   └── cli/             # Command-line interface
├── tests/               # Test suite
├── configs/             # Configuration files
├── docker/              # Docker-related files
├── docs/                # Documentation
├── outputs/             # Generated videos
├── cache/               # Model cache
└── temp/                # Temporary files
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Acknowledgments

- [Hugging Face](https://huggingface.co/) for Transformers and Diffusers
- [ModelScope](https://modelscope.cn/) for the text-to-video model
- [ Stability AI](https://stability.ai/) for video diffusion research