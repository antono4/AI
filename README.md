# 🎬 AI Video Generator

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-00D084?style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/🤗%20Diffusers-F5D642?style=for-the-badge" alt="Hugging Face">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

> **Create stunning videos from text prompts using state-of-the-art AI diffusion models**

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎥 **Text-to-Video** | Generate videos from natural language prompts |
| 🚀 **FastAPI API** | Production-ready REST API with async support |
| 💻 **CLI Tool** | Easy command-line interface for quick generation |
| 🐳 **Docker Ready** | Containerized deployment with GPU support |
| 🎨 **Modern Web UI** | Beautiful, responsive interface |
| ⚡ **GPU Accelerated** | CUDA support for fast generation |
| 🧪 **Tested** | Comprehensive unit tests |

## 🚀 Live Demo

**🌐 Web UI:** [https://antono4.github.io/AI/](https://antono4.github.io/AI/)

## 📦 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/antono4/AI.git
cd AI
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Web UI

Simply open `index.html` in your browser, or:

```bash
# Start the API server
python -m src.api.server

# Then open http://localhost:8000
```

## 💻 Usage

### 🌐 Web UI

1. Open [https://antono4.github.io/AI/](https://antono4.github.io/AI/)
2. Enter your video prompt
3. Adjust settings (resolution, FPS, duration)
4. Click "Generate Video"

### 🖥️ Command Line

```bash
# Basic generation
video-gen generate "A cat playing piano in a jazz club"

# With custom parameters
video-gen generate "A sunset over the ocean" \
    --steps 30 \
    --guidance 9.5 \
    --fps 24 \
    --seed 42 \
    --output my_video.mp4

# Start API server
video-gen serve --port 8000

# Show configuration
video-gen info
```

### 🐍 Python API

```python
from src.models.video_generator import VideoGenerator

# Initialize generator
generator = VideoGenerator(
    model_name="damo-vilab/text-to-video-ms-1.7b",
    device="cuda"
)

# Load model
generator.load_model()

# Generate video
video_path = generator.generate_to_video(
    prompt="A beautiful sunset over the ocean with dolphins jumping",
    output_path="output.mp4",
    num_inference_steps=25,
    guidance_scale=7.5,
    seed=42,
    num_frames=16,
    fps=24
)

print(f"Video saved to: {video_path}")
```

### 🌐 REST API

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
  -d '{
    "prompt": "A cat in space",
    "num_inference_steps": 25,
    "guidance_scale": 7.5,
    "seed": 42
  }'
```

## ⚙️ Configuration

### Environment Variables

```bash
# Model Settings
MODEL__MODEL_NAME=damo-vilab/text-to-video-ms-1.7b
MODEL__DEVICE=cuda              # cuda, mps, cpu
MODEL__TORCH_DTYPE=float16     # float32, float16, bfloat16

# Generation Settings
GEN__NUM_INFERENCE_STEPS=25
GEN__GUIDANCE_SCALE=7.5
GEN__NUM_FRAMES=16
GEN__HEIGHT=256
GEN__WIDTH=256
GEN__FPS=8

# API Settings
API__HOST=0.0.0.0
API__PORT=8000

# Storage
STORAGE__OUTPUT_DIR=./outputs
STORAGE__CACHE_DIR=./cache
```

### Or use .env file

```bash
cp .env.example .env
# Edit .env with your settings
```

## 🧩 Supported Models

| Model | Type | Description |
|-------|------|-------------|
| `damo-vilab/text-to-video-ms-1.7b` | Text-to-Video | High-quality video generation (Recommended) |
| `modelscope/text-to-video-ms` | Text-to-Video | Alternative text-to-video model |
| `stabilityai/stable-video-diffusion-img2vid` | Video-to-Video | Image to video diffusion |

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t ai-video-generator .
```

### Run Container

```bash
# CPU
docker run -p 8000:8000 ai-video-generator

# GPU (NVIDIA)
docker run --gpus all -p 8000:8000 ai-video-generator
```

### Docker Compose

```bash
docker-compose up -d
```

## 🧪 Development

### Setup Development Environment

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## 📁 Project Structure

```
AI/
├── index.html              # Web UI
├── src/
│   ├── models/
│   │   └── video_generator.py   # AI Video Generator
│   ├── api/
│   │   └── server.py           # FastAPI Server
│   ├── cli/
│   │   └── main.py             # CLI Interface
│   └── utils/
│       ├── config.py            # Configuration
│       └── video.py             # Video utilities
├── tests/
│   ├── test_video_generator.py
│   └── test_video_utils.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🎯 Performance Tips

| Tip | Description |
|-----|-------------|
| 🖥️ **Use GPU** | Set `MODEL__DEVICE=cuda` for 10x faster generation |
| 📐 **Lower Resolution** | Use 256px for testing, 768px for final output |
| 🔢 **Fewer Steps** | 15-20 steps for preview, 25-30 for quality |
| 💾 **Clear Cache** | Delete `./cache` if you encounter issues |

## 🐛 Troubleshooting

### Out of Memory (OOM)
- Reduce resolution or number of frames
- Enable CPU offload: `MODEL__DEVICE=mps`

### Slow Generation
- Make sure GPU is available: `python -c "import torch; print(torch.cuda.is_available())"`
- Reduce inference steps for testing

### Model Download Issues
- Check internet connection
- Use custom cache: `STORAGE__CACHE_DIR=/path/to/cache`

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co/) - Transformers & Diffusers Libraries
- [ModelScope](https://modelscope.cn/) - Text-to-Video Model
- [Stability AI](https://stability.ai/) - Video Diffusion Research

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/antono4/AI?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/antono4/AI?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/antono4/AI?style=for-the-badge)

---

<p align="center">
  Made with ❤️ using <a href="https://github.com/huggingface/diffusers">Hugging Face Diffusers</a>
</p>
