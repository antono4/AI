"""
AI Video Shorts App - Flask Web Application
Dashboard untuk membuat dan upload video shorts ke YouTube
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.video_generator import VideoProject, ContentGenerator, StockVideoFetcher
from app.modules.voiceover import VoiceoverGenerator, create_complete_audio
from app.modules.video_editor import VideoProcessor, auto_process_video
from app.modules.youtube_uploader import YouTubeUploader, YouTubeAuth, ThumbnailGenerator
from app.modules.scheduler import get_scheduler, start_automation, stop_automation

# Initialize Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max
CORS(app)

# Ensure directories exist
Path("output").mkdir(exist_ok=True)
Path("output/videos").mkdir(exist_ok=True)
Path("output/thumbnails").mkdir(exist_ok=True)


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """Get system status"""
    scheduler = get_scheduler()
    auth = YouTubeAuth()
    
    return jsonify({
        'youtube_connected': auth.is_authenticated(),
        'scheduler_running': scheduler._running,
        'scheduler_status': scheduler.get_status(),
        'output_dir': 'output/',
        'timestamp': datetime.now().isoformat()
    })


# ==================== VIDEO GENERATION ====================

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """Generate video from topic"""
    data = request.get_json()
    
    topic = data.get('topic', '')
    duration = data.get('duration', 45)
    language = data.get('language', 'id')
    
    if not topic:
        return jsonify({'status': 'error', 'message': 'Topic is required'})
    
    try:
        # Create project
        project = VideoProject()
        
        # Generate content
        content = project.prepare_content(topic, duration, language)
        
        # Fetch stock videos
        videos = project.fetch_stock_videos(topic, num_clips=3)
        
        # Create video
        final_video = project.create_video(content.get('title'))
        
        return jsonify({
            'status': 'success',
            'project': project.get_project_info(),
            'content': content,
            'videos': videos,
            'final_video': final_video
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/generate-script', methods=['POST'])
def generate_script():
    """Generate content script only"""
    data = request.get_json()
    
    topic = data.get('topic', '')
    duration = data.get('duration', 45)
    language = data.get('language', 'id')
    
    if not topic:
        return jsonify({'status': 'error', 'message': 'Topic is required'})
    
    generator = ContentGenerator()
    content = generator.generate_script(topic, duration, language)
    
    return jsonify({
        'status': 'success',
        'content': content
    })


# ==================== VIDEO EDITING ====================

@app.route('/api/process-video', methods=['POST'])
def process_video():
    """Process video with captions, music, effects"""
    data = request.get_json()
    
    video_path = data.get('video_path', '')
    script = data.get('script', {})
    music_volume = data.get('music_volume', 0.3)
    caption_style = data.get('caption_style', 'highlight')
    
    if not video_path or not os.path.exists(video_path):
        return jsonify({'status': 'error', 'message': 'Video file not found'})
    
    result = auto_process_video(
        video_path=video_path,
        script=script,
        music_volume=music_volume
    )
    
    return jsonify(result)


# ==================== VOICEOVER ====================

@app.route('/api/voiceover', methods=['POST'])
def generate_voiceover():
    """Generate voiceover from text"""
    data = request.get_json()
    
    text = data.get('text', '')
    provider = data.get('provider', 'gtts')
    voice_id = data.get('voice_id')
    
    if not text:
        return jsonify({'status': 'error', 'message': 'Text is required'})
    
    generator = VoiceoverGenerator()
    result = generator.generate(text, provider=provider, voice_id=voice_id)
    
    return jsonify(result)


@app.route('/api/voices')
def get_voices():
    """Get available voices"""
    provider = request.args.get('provider', 'elevenlabs')
    
    generator = VoiceoverGenerator()
    voices = generator.get_available_voices(provider)
    
    return jsonify({
        'status': 'success',
        'voices': voices
    })


# ==================== YOUTUBE ====================

@app.route('/api/youtube/auth')
def youtube_auth():
    """Start YouTube OAuth flow"""
    try:
        auth = YouTubeAuth()
        auth.get_authenticated_service()
        return jsonify({
            'status': 'success',
            'message': 'Authentication successful'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


@app.route('/api/youtube/connect')
def youtube_connect():
    """Check YouTube connection status"""
    auth = YouTubeAuth()
    return jsonify({
        'connected': auth.is_authenticated()
    })


@app.route('/api/youtube/channel')
def youtube_channel():
    """Get YouTube channel info"""
    uploader = YouTubeUploader()
    if uploader.connect():
        info = uploader.get_channel_info()
        return jsonify(info)
    return jsonify({'status': 'error', 'message': 'Not connected'})


@app.route('/api/youtube/upload', methods=['POST'])
def youtube_upload():
    """Upload video to YouTube"""
    data = request.get_json()
    
    video_path = data.get('video_path', '')
    title = data.get('title', '')
    description = data.get('description', '')
    tags = data.get('tags', [])
    privacy = data.get('privacy', 'private')
    schedule_time = data.get('schedule_time')
    
    if not video_path or not os.path.exists(video_path):
        return jsonify({'status': 'error', 'message': 'Video file not found'})
    
    if not title:
        return jsonify({'status': 'error', 'message': 'Title is required'})
    
    uploader = YouTubeUploader()
    
    scheduled = None
    if schedule_time:
        scheduled = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
    
    result = uploader.upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy=privacy,
        scheduled_time=scheduled
    )
    
    return jsonify(result)


@app.route('/api/youtube/thumbnail', methods=['POST'])
def generate_thumbnail():
    """Generate thumbnail for video"""
    data = request.get_json()
    
    title = data.get('title', '')
    style = data.get('style', 'default')
    
    if not title:
        return jsonify({'status': 'error', 'message': 'Title is required'})
    
    gen = ThumbnailGenerator()
    path = gen.create_thumbnail(title, style)
    
    return jsonify({
        'status': 'success' if path else 'error',
        'path': path
    })


# ==================== SCHEDULER ====================

@app.route('/api/scheduler/start')
def scheduler_start():
    """Start automation scheduler"""
    scheduler = start_automation()
    return jsonify({
        'status': 'success',
        'running': scheduler._running
    })


@app.route('/api/scheduler/stop')
def scheduler_stop():
    """Stop automation scheduler"""
    stop_automation()
    return jsonify({
        'status': 'success',
        'running': False
    })


@app.route('/api/scheduler/status')
def scheduler_status():
    """Get scheduler status"""
    scheduler = get_scheduler()
    return jsonify(scheduler.get_status())


@app.route('/api/scheduler/schedule', methods=['POST'])
def scheduler_schedule():
    """Schedule a video generation task"""
    data = request.get_json()
    
    topic = data.get('topic', '')
    schedule_time = data.get('schedule_time')
    cron = data.get('cron')
    interval = data.get('interval_minutes')
    upload_to_youtube = data.get('upload_to_youtube', False)
    
    if not topic:
        return jsonify({'status': 'error', 'message': 'Topic is required'})
    
    scheduler = get_scheduler()
    
    scheduled_time = None
    if schedule_time:
        scheduled_time = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
    
    task_id = scheduler.schedule_video_generation(
        topic=topic,
        schedule_time=scheduled_time,
        cron=cron,
        interval_minutes=interval,
        config={
            'topic': topic,
            'duration': data.get('duration', 45),
            'language': data.get('language', 'id'),
            'voice_provider': data.get('voice_provider', 'gtts'),
            'upload_to_youtube': upload_to_youtube
        }
    )
    
    return jsonify({
        'status': 'success',
        'task_id': task_id
    })


@app.route('/api/scheduler/batch', methods=['POST'])
def scheduler_batch():
    """Schedule batch of videos"""
    data = request.get_json()
    
    topics = data.get('topics', [])
    interval_hours = data.get('interval_hours', 4)
    upload_to_youtube = data.get('upload_to_youtube', False)
    
    if not topics:
        return jsonify({'status': 'error', 'message': 'Topics list is required'})
    
    scheduler = get_scheduler()
    task_ids = scheduler.schedule_batch(topics, interval_hours, upload_to_youtube)
    
    return jsonify({
        'status': 'success',
        'task_ids': task_ids,
        'count': len(task_ids)
    })


@app.route('/api/scheduler/cancel/<task_id>')
def scheduler_cancel(task_id):
    """Cancel a scheduled task"""
    scheduler = get_scheduler()
    scheduler.cancel_task(task_id)
    return jsonify({'status': 'success'})


# ==================== FULL PIPELINE ====================

@app.route('/api/pipeline/execute', methods=['POST'])
def execute_pipeline():
    """Execute complete pipeline: generate → edit → upload"""
    data = request.get_json()
    
    topic = data.get('topic', '')
    duration = data.get('duration', 45)
    language = data.get('language', 'id')
    voice_provider = data.get('voice_provider', 'gtts')
    upload_to_youtube = data.get('upload_to_youtube', False)
    schedule_time = data.get('schedule_time')
    
    if not topic:
        return jsonify({'status': 'error', 'message': 'Topic is required'})
    
    scheduled = None
    if schedule_time:
        scheduled = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
    
    # Execute pipeline
    from app.modules.scheduler import PipelineExecutor
    executor = PipelineExecutor()
    
    result = executor.execute_full_pipeline(
        topic=topic,
        duration=duration,
        language=language,
        voice_provider=voice_provider,
        upload_to_youtube=upload_to_youtube,
        schedule_time=scheduled
    )
    
    return jsonify(result)


# ==================== FILES ====================

@app.route('/api/videos')
def list_videos():
    """List generated videos"""
    videos_dir = Path("output")
    videos = []
    
    for f in videos_dir.rglob("*.mp4"):
        videos.append({
            'name': f.name,
            'path': str(f),
            'size': f.stat().st_size,
            'created': datetime.fromtimestamp(f.stat().st_ctime).isoformat()
        })
    
    return jsonify({
        'status': 'success',
        'videos': videos
    })


@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Download a file"""
    return send_file(filename, as_attachment=True)


# ==================== TOPICS SUGGESTIONS ====================

@app.route('/api/suggest-topics')
def suggest_topics():
    """Get topic suggestions"""
    suggestions = [
        "Fakta menarik tentang宇宙",
        "Tips produktivitas kerja",
        "Cara mudah belajar programming",
        "Fakta sains yang mengejutkan",
        "Tips kesehatan sehari-hari",
        "Sejarah peradaban kuno",
        "Misteri alam semesta",
        "Tips bisnis online",
        "Fakta hewan unik",
        "Cara membuat konten viral"
    ]
    return jsonify({
        'status': 'success',
        'topics': suggestions
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'status': 'error', 'message': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    print("🚀 Starting AI Video Shorts App...")
    print(f"📁 Output directory: {Path('output').absolute()}")
    print("🌐 Dashboard: http://localhost:5000")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )