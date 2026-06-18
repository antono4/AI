# 🎬 AI Video Generator

![AI Video Generator](https://img.shields.io/badge/AI-Video%20Generator-6366f1?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-00D084?style=for-the-badge)
![Hugging Face](https://img.shields.io/badge/🤗-Diffusers-F5D642?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Production-ready AI Video Generator using Hugging Face Transformers and Diffusers.**

## 🌟 Features

- **🎥 Text-to-Video Generation** - Generate videos from text prompts
- **🚀 Production-Ready API** - FastAPI-based REST API with async job management
- **💻 CLI Interface** - Easy-to-use command-line tool
- **🐳 Docker Support** - Containerized deployment with GPU support
- **⚙️ Highly Configurable** - Extensive configuration options
- **🧪 Comprehensive Testing** - Unit tests with high coverage
- **🎨 Beautiful Web UI** - Modern, responsive interface

## 🧩 Supported Models

| Model | Type | Description |
|-------|------|-------------|
| `damo-vilab/text-to-video-ms-1.7b` | Text-to-Video | High quality (Default) |
| `stabilityai/stable-video-diffusion` | Video-to-Video | Image to video |
| `modelscope/text-to-video-ms` | Text-to-Video | Alternative model |

## 🚀 Live Demo

**🌐 Web UI:** https://antono4.github.io/AI/

## 📦 Installation

### From Source
```bash
git clone https://github.com/antono4/AI.git
cd AI
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Using Docker
```bash
docker build -t ai-video-generator .
docker run --gpus all -p 8000:8000 ai-video-generator
```

## 💻 Usage

### 🌐 Web UI
Open `index.html` or visit https://antono4.github.io/AI/

### 🖥️ CLI
```bash
video-gen generate "A cat playing piano"
video-gen serve --port 8000
```

### 🐍 Python API
```python
from src.models.video_generator import VideoGenerator

generator = VideoGenerator()
generator.load_model()
video_path = generator.generate_to_video(
    prompt="A sunset over the ocean",
    output_path="output.mp4"
)
```

### 🌐 REST API
```bash
python -m src.api.server
curl -X POST http://localhost:8000/generate \
  -d '{"prompt": "A cat in space"}'
```

## ⚙️ Configuration

```bash
MODEL__MODEL_NAME=damo-vilab/text-to-video-ms-1.7b
MODEL__DEVICE=cuda
GEN__NUM_INFERENCE_STEPS=25
GEN__GUIDANCE_SCALE=7.5
```

## 🧪 Development

```bash
pip install -e ".[dev]"
pytest
```

## 🏗️ Architecture

```
src/
├── models/video_generator.py    # AI model
├── api/server.py                # FastAPI server
├── cli/main.py                  # CLI interface
└── utils/
    ├── config.py                # Configuration
    └── video.py                 # Video utilities
```

## 📄 License

MIT License

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co/) - Transformers and Diffusers
- [ModelScope](https://modelscope.cn/) - Text-to-Video model
- [Stability AI](https://stability.ai/) - Video diffusion research

---

Made with ❤️ using [Hugging Face Diffusers](https://github.com/huggingface/diffusers)
