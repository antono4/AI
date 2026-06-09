# 🎬 AI Video Shorts Generator

Aplikasi AI untuk auto-generate video shorts dan auto-upload ke YouTube. Mendukung berbagai sumber konten termasuk stock video, AI voiceover, dan video generation.

## ✨ Fitur

### 🎥 Pembuatan Video
- **AI Content Generator**: Generate script otomatis menggunakan GPT/Claude
- **Stock Video**: Integrasi dengan Pexels & Pixabay
- **AI Video Generation**: Dukungan untuk Runway Gen-2/Gen-3, Pika Labs
- **Video Editor**: Tambah caption, subtitle, transisi, dan efek

### 🎙️ Audio
- **Multi-Provider TTS**: Google TTS (free), ElevenLabs, OpenAI TTS
- **Background Music**: Ambient music generation
- **Voice Mixing**: Mix voiceover dengan background music

### 📤 YouTube Integration
- **OAuth Authentication**: Secure YouTube API integration
- **Auto Upload**: Upload video langsung ke YouTube
- **Thumbnail Generator**: Generate thumbnail otomatis
- **Scheduling**: Jadwalkan upload untuk waktu tertentu
- **Metadata**: Auto-generate title, description, tags

### ⏰ Automation
- **Scheduler**: Jadwalkan pembuatan video otomatis
- **Batch Processing**: Generate multiple videos sekaligus
- **Pipeline**: Full pipeline dari generate sampai upload

## 🚀 Instalasi

### 1. Clone atau Download
```bash
git clone <repository-url>
cd ai-video-shorts-app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
```bash
# Copy contoh environment file
cp .env.example .env

# Edit .env dengan API keys Anda
nano .env
```

### 4. Setup YouTube API (Opsional)
1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Buat project baru
3. Enable YouTube Data API v3
4. Buat OAuth 2.0 credentials
5. Download `client_secret.json`
6. Letakkan di root project

### 5. Jalankan Aplikasi
```bash
python app/main.py
```

Buka browser ke `http://localhost:5000`

## 📁 Struktur Project

```
ai-video-shorts-app/
├── app/
│   ├── modules/
│   │   ├── video_generator.py    # Video generation logic
│   │   ├── voiceover.py          # TTS & audio
│   │   ├── video_editor.py      # Video editing
│   │   ├── youtube_uploader.py  # YouTube API
│   │   └── scheduler.py         # Automation
│   ├── templates/
│   │   └── dashboard.html       # Web UI
│   └── main.py                  # Flask app
├── config/
│   └── settings.py              # Configuration
├── output/                      # Generated videos
├── logs/                        # Application logs
├── .env                         # Environment variables
├── client_secret.json          # YouTube OAuth
└── requirements.txt            # Dependencies
```

## 🔑 API Keys yang Dibutuhkan

### Free (No API Key Required)
- **Google TTS**: Built-in, tidak perlu API key

### Optional ( untuk fitur premium )
- **OpenAI**: [Get API Key](https://platform.openai.com/)
- **ElevenLabs**: [Get API Key](https://elevenlabs.io/)
- **Pexels**: [Get API Key](https://www.pexels.com/api/)
- **Pixabay**: [Get API Key](https://pixabay.com/api/)
- **Replicate**: [Get API Key](https://replicate.com/)

## 📡 API Endpoints

### Video Generation
- `POST /api/generate` - Generate video dari topic
- `POST /api/generate-script` - Generate script saja
- `POST /api/process-video` - Process video dengan effects

### Voiceover
- `POST /api/voiceover` - Generate voiceover
- `GET /api/voices` - Get available voices

### YouTube
- `GET /api/youtube/connect` - Check connection
- `POST /api/youtube/upload` - Upload video
- `POST /api/youtube/thumbnail` - Generate thumbnail

### Scheduler
- `GET /api/scheduler/status` - Get scheduler status
- `POST /api/scheduler/schedule` - Schedule task
- `POST /api/scheduler/batch` - Schedule batch

### Pipeline
- `POST /api/pipeline/execute` - Execute full pipeline

## 🎯 Usage Examples

### Generate Video Sederhana
```python
from app.modules.video_generator import create_video_from_topic

result = create_video_from_topic(
    topic="Fakta menarik tentang AI",
    duration=45,
    language='id'
)
print(result)
```

### Full Pipeline dengan Upload
```python
from app.modules.scheduler import PipelineExecutor

executor = PipelineExecutor()
result = executor.execute_full_pipeline(
    topic="Tips produktivitas kerja",
    duration=60,
    language='id',
    voice_provider='gtts',
    upload_to_youtube=True
)
```

### Schedule Batch Videos
```python
from app.modules.scheduler import get_scheduler

scheduler = get_scheduler()
scheduler.start()

scheduler.schedule_batch(
    topics=[
        "Fakta sains 1",
        "Fakta sains 2",
        "Fakta sains 3"
    ],
    interval_hours=4,
    upload_to_youtube=True
)
```

## ⚙️ Configuration

Edit `config/settings.py` atau `.env` untuk mengubah:

```python
# Video Settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # Vertical (9:16)
VIDEO_FPS = 30

# Limits
MAX_DAILY_VIDEOS = 10
MAX_CONCURRENT_UPLOADS = 2

# YouTube
DEFAULT_PRIVACY_STATUS = 'private'  # private, public, unlisted
AUTO_GENERATE_THUMBNAIL = True
```

## 🖥️ Dashboard UI

Dashboard web dengan fitur:
- Input topik video
- Pilihan durasi & bahasa
- Pilihan voice provider
- Toggle untuk music, captions, auto-upload
- Statistik video
- Activity log
- Scheduler controls

## 🔧 Troubleshooting

### Video tidak ter-generate
1. Cek apakah moviepy terinstall dengan benar
2. Pastikan ffmpeg terinstall di sistem
3. Cek logs di `logs/` directory

### YouTube upload gagal
1. Pastikan `client_secret.json` ada di root
2. Cek apakah OAuth sudah authorize
3. Verifikasi API key YouTube

### TTS tidak bekerja
1. Untuk Google TTS: Pastikan internet connection
2. Untuk ElevenLabs: Cek API key
3. Untuk OpenAI: Cek API key dan quota

## 📝 License

MIT License - Bebas digunakan untuk personal dan commercial projects.

## 🤝 Contributing

Kontribusi sangat diterima! Silakan buat pull request atau issue.

---

Made with ❤️ for content creators 🚀