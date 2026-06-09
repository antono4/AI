"""
AI Video Generator Module
Generate video shorts using AI and stock footage
"""

import os
import json
import random
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Import config
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    PEXELS_API_KEY, PIXABAY_API_KEY, REPLICATE_API_TOKEN,
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, OUTPUT_DIR
)


class ContentGenerator:
    """Generate video content ideas and scripts using AI"""
    
    def __init__(self, openai_key: str = None):
        self.openai_key = openai_key or os.getenv('OPENAI_API_KEY')
        
    def generate_script(self, topic: str, duration: int = 45, language: str = 'id') -> Dict:
        """Generate video script from topic"""
        if not self.openai_key:
            return self._generate_simple_script(topic, duration, language)
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            prompt = f"""Buatkan script video short ({(duration//15)+1} bagian) tentang: {topic}
            
Format output JSON seperti berikut:
{{
    "title": "Judul video yang menarik",
    "description": "Deskripsi untuk YouTube",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "segments": [
        {{
            "text": "Teks untuk bagian 1",
            "duration": 15
        }},
        {{
            "text": "Teks untuk bagian 2", 
            "duration": 15
        }}
    ],
    "hashtags": "#hashtag1 #hashtag2 #hashtag3"
}}

Rules:
- Durasi total {duration} detik
- 3-4 segmen dengan transisi menarik
- Bahasa {language}
- Hook yang kuat di awal
- Call to action di akhir
- Tidak lebih dari 80 karakter per segmen
"""
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.9
            )
            
            content = json.loads(response.choices[0].message.content)
            content['generated_at'] = datetime.now().isoformat()
            return content
            
        except Exception as e:
            print(f"Error generating script: {e}")
            return self._generate_simple_script(topic, duration, language)
    
    def _generate_simple_script(self, topic: str, duration: int, language: str) -> Dict:
        """Fallback script generator"""
        segments = []
        num_segments = (duration // 15) + 1
        
        for i in range(num_segments):
            if i == 0:
                text = f"🔥 FAKTA MENARIK tentang {topic}!"
            elif i == num_segments - 1:
                text = f"👍 LIKE & SUBSCRIBE untuk fakta menarik lainnya!"
            else:
                text = f"Fakta #{i+1} tentang {topic} yang perlu kamu tahu!"
            
            segments.append({
                "text": text,
                "duration": 15
            })
        
        return {
            "title": f"Fakta Menarik tentang {topic} 🎬",
            "description": f"Video lengkap tentang {topic}\n\nJangan lupa like, comment, dan subscribe!",
            "tags": [topic, "fakta", "menarik", "viral", "trending"],
            "segments": segments,
            "hashtags": f"#{topic.replace(' ', '')} #faktamenarik #viral",
            "generated_at": datetime.now().isoformat()
        }


class StockVideoFetcher:
    """Fetch stock videos from Pexels and Pixabay"""
    
    def __init__(self):
        self.pexels_key = PEXELS_API_KEY
        self.pixabay_key = PIXABAY_API_KEY
        self.cache_dir = Path(OUTPUT_DIR) / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def search_videos(self, query: str, num_videos: int = 5) -> List[Dict]:
        """Search and download stock videos"""
        videos = []
        
        # Try Pexels first
        if self.pexels_key:
            pexels_videos = self._search_pexels(query, num_videos)
            videos.extend(pexels_videos)
        
        # Try Pixabay
        if self.pixabay_key and len(videos) < num_videos:
            pixabay_videos = self._search_pixabay(query, num_videos - len(videos))
            videos.extend(pixabay_videos)
        
        # If no API keys, generate placeholder
        if not videos:
            videos = self._generate_placeholder_videos(query, num_videos)
        
        return videos[:num_videos]
    
    def _search_pexels(self, query: str, num_videos: int) -> List[Dict]:
        """Search Pexels API"""
        try:
            headers = {"Authorization": self.pexels_key}
            params = {"query": query, "per_page": num_videos, "orientation": "portrait"}
            
            response = requests.get(
                "https://api.pexels.com/videos/search",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                
                for video in data.get('videos', []):
                    # Get HD video file
                    video_files = sorted(
                        video.get('video_files', []),
                        key=lambda x: x.get('height', 0),
                        reverse=True
                    )
                    
                    hd_file = next((f for f in video_files if f.get('height') >= 720), video_files[0] if video_files else None)
                    
                    if hd_file:
                        videos.append({
                            "source": "pexels",
                            "id": video['id'],
                            "url": hd_file['link'],
                            "thumbnail": video['image'],
                            "duration": video.get('duration', 15),
                            "width": hd_file.get('width', 1080),
                            "height": hd_file.get('height', 1920),
                            "download_path": None  # Will be downloaded later
                        })
                
                return videos
                
        except Exception as e:
            print(f"Pexels API error: {e}")
        
        return []
    
    def _search_pixabay(self, query: str, num_videos: int) -> List[Dict]:
        """Search Pixabay API"""
        try:
            params = {
                "key": self.pixabay_key,
                "q": query,
                "video_type": "film",
                "per_page": num_videos,
                "orientation": "vertical"
            }
            
            response = requests.get(
                "https://pixabay.com/api/videos/",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                
                for video in data.get('hits', []):
                    videos.append({
                        "source": "pixabay",
                        "id": video['id'],
                        "url": video['videos']['hd']['url'] if 'hd' in video['videos'] else video['videos']['full']['url'],
                        "thumbnail": video['largeImageURL'],
                        "duration": video.get('duration', 15),
                        "width": 1920,
                        "height": 1080,
                        "download_path": None
                    })
                
                return videos
                
        except Exception as e:
            print(f"Pixabay API error: {e}")
        
        return []
    
    def _generate_placeholder_videos(self, query: str, num_videos: int) -> List[Dict]:
        """Generate placeholder videos (for testing without API keys)"""
        placeholders = []
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        
        for i in range(num_videos):
            placeholders.append({
                "source": "placeholder",
                "id": f"placeholder_{i}",
                "url": None,
                "thumbnail": None,
                "duration": 15,
                "width": 1080,
                "height": 1920,
                "color": random.choice(colors),
                "text": query.upper(),
                "index": i
            })
        
        return placeholders
    
    def download_video(self, video_info: Dict, output_path: str) -> bool:
        """Download video from URL"""
        if video_info.get('source') == 'placeholder':
            return self._create_placeholder_video(video_info, output_path)
        
        if not video_info.get('url'):
            return False
        
        try:
            response = requests.get(video_info['url'], stream=True, timeout=60)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                video_info['download_path'] = output_path
                return True
        except Exception as e:
            print(f"Download error: {e}")
        
        return False
    
    def _create_placeholder_video(self, video_info: Dict, output_path: str) -> bool:
        """Create placeholder video with colored background"""
        try:
            from moviepy import ColorClip, TextClip, CompositeVideoClip
            
            clip = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=tuple(int(video_info['color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)))
            clip = clip.with_duration(video_info['duration'])
            
            # Add text overlay
            txt = TextClip(
                text=f"{video_info.get('text', 'AI Video')}\nPart {video_info.get('index', 1) + 1}",
                font_size=60,
                color='white',
                font='Helvetica-Bold',
                method='caption'
            ).with_duration(video_info['duration']).with_position('center')
            
            final = CompositeVideoClip([clip, txt])
            final.write_videofile(output_path, fps=VIDEO_FPS, codec='libx264', audio=False, verbose=False, logger=None)
            
            return True
        except Exception as e:
            print(f"Placeholder creation error: {e}")
            return False


class AIVideoGenerator:
    """Generate videos using AI (Runway, Pika, etc.)"""
    
    def __init__(self):
        self.replicate_key = REPLICATE_API_TOKEN
        
    def generate_video(self, prompt: str, model: str = "runway") -> Dict:
        """Generate video from text prompt using AI"""
        if not self.replicate_key:
            return {
                "status": "no_api_key",
                "message": "Replicate API key not configured",
                "video_url": None
            }
        
        try:
            import replicate
            
            # This is a placeholder - actual implementation depends on available models
            if model == "runway":
                # Runway Gen-2/Gen-3 implementation
                output = replicate.run(
                    "stability-ai/stable-video:3f6117fa",
                    input={
                        "prompt": prompt,
                        "frames": 24,
                        "fps": 8
                    }
                )
                
                return {
                    "status": "success",
                    "model": model,
                    "video_url": output,
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unsupported_model",
                    "message": f"Model {model} not supported",
                    "video_url": None
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "video_url": None
            }


class VideoProject:
    """Manage video project creation and assembly"""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(OUTPUT_DIR) / self.project_id
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.content = None
        self.video_clips = []
        self.audio_files = []
        self.final_video_path = None
        
    def prepare_content(self, topic: str, duration: int = 45, language: str = 'id') -> Dict:
        """Prepare content script for video"""
        generator = ContentGenerator()
        self.content = generator.generate_script(topic, duration, language)
        
        # Save content
        with open(self.output_dir / "script.json", 'w') as f:
            json.dump(self.content, f, indent=2, ensure_ascii=False)
        
        return self.content
    
    def fetch_stock_videos(self, query: str, num_clips: int = 5) -> List[Dict]:
        """Fetch stock videos for the project"""
        fetcher = StockVideoFetcher()
        videos = fetcher.search_videos(query, num_clips)
        
        # Download videos
        downloaded = []
        for i, video in enumerate(videos):
            output_path = str(self.output_dir / f"clip_{i+1}.mp4")
            
            if fetcher.download_video(video, output_path):
                video['local_path'] = output_path
                downloaded.append(video)
                self.video_clips.append(output_path)
        
        return downloaded
    
    def create_video(self, title: str = None) -> str:
        """Assemble final video from clips"""
        if not self.video_clips:
            raise ValueError("No video clips available")
        
        title = title or self.content.get('title', 'AI Generated Video')
        
        try:
            from moviepy import (
                VideoFileClip, concatenate_videoclips, 
                ColorClip, TextClip, CompositeVideoClip, ImageClip
            )
            
            clips = []
            
            for clip_path in self.video_clips:
                if os.path.exists(clip_path):
                    clip = VideoFileClip(clip_path)
                    # Resize to portrait if needed
                    if clip.w < clip.h:
                        clip = clip.resize(width=VIDEO_WIDTH)
                    else:
                        clip = clip.resize(height=VIDEO_HEIGHT)
                    
                    # Crop to center
                    clip = clip.crop(
                        x1=(clip.w - VIDEO_WIDTH)//2,
                        y1=(clip.h - VIDEO_HEIGHT)//2,
                        width=VIDEO_WIDTH,
                        height=VIDEO_HEIGHT
                    )
                    
                    clips.append(clip)
            
            if not clips:
                # Create fallback video
                final_clip = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(50, 50, 50))
                final_clip = final_clip.with_duration(sum(seg.get('duration', 15) for seg in self.content.get('segments', [{'duration': 45}])))
                
                # Add title
                txt = TextClip(
                    text=title,
                    font_size=50,
                    color='white',
                    method='caption'
                ).with_duration(5).with_position('center')
                
                final = CompositeVideoClip([final_clip, txt])
            else:
                # Concatenate clips
                final = concatenate_videoclips(clips)
            
            # Add intro and outro
            intro = self._create_intro(title)
            outro = self._create_outro()
            
            if intro:
                final = concatenate_videoclips([intro, final])
            if outro:
                final = concatenate_videoclips([final, outro])
            
            # Export
            output_path = str(self.output_dir / "final_video.mp4")
            final.write_videofile(
                output_path,
                fps=VIDEO_FPS,
                codec='libx264',
                audio_codec='aac',
                preset='fast',
                verbose=False,
                logger=None
            )
            
            self.final_video_path = output_path
            return output_path
            
        except Exception as e:
            print(f"Video creation error: {e}")
            # Create simple fallback
            return self._create_simple_video(title)
    
    def _create_intro(self, title: str) -> Optional:
        """Create intro clip"""
        try:
            from moviepy import ColorClip, TextClip, CompositeVideoClip
            
            intro = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0))
            intro = intro.with_duration(2)
            
            txt = TextClip(
                text=f"🎬 {title}",
                font_size=40,
                color='white',
                method='caption'
            ).with_duration(2).with_position('center')
            
            return CompositeVideoClip([intro, txt])
        except:
            return None
    
    def _create_outro(self) -> Optional:
        """Create outro clip with CTA"""
        try:
            from moviepy import ColorClip, TextClip, CompositeVideoClip
            
            outro = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(30, 30, 30))
            outro = outro.with_duration(3)
            
            txt = TextClip(
                text="👍 LIKE | 💬 COMMENT | 🔔 SUBSCRIBE",
                font_size=35,
                color='white',
                method='caption'
            ).with_duration(3).with_position('center')
            
            return CompositeVideoClip([outro, txt])
        except:
            return None
    
    def _create_simple_video(self, title: str) -> str:
        """Create simple placeholder video"""
        try:
            from moviepy import ColorClip, TextClip, CompositeVideoClip
            
            duration = sum(seg.get('duration', 15) for seg in self.content.get('segments', [{'duration': 45}]))
            
            clip = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(40, 40, 40))
            clip = clip.with_duration(duration)
            
            txt = TextClip(
                text=title,
                font_size=50,
                color='white',
                method='caption'
            ).with_duration(duration).with_position('center')
            
            final = CompositeVideoClip([clip, txt])
            
            output_path = str(self.output_dir / "final_video.mp4")
            final.write_videofile(output_path, fps=VIDEO_FPS, codec='libx264', verbose=False, logger=None)
            
            self.final_video_path = output_path
            return output_path
            
        except Exception as e:
            print(f"Simple video creation error: {e}")
            return ""
    
    def get_project_info(self) -> Dict:
        """Get project information"""
        return {
            "project_id": self.project_id,
            "output_dir": str(self.output_dir),
            "content": self.content,
            "video_clips": self.video_clips,
            "final_video": self.final_video_path,
            "exists": os.path.exists(self.final_video_path) if self.final_video_path else False
        }


# Standalone function for quick video creation
def create_video_from_topic(topic: str, duration: int = 45, language: str = 'id') -> Dict:
    """Create complete video from topic"""
    project = VideoProject()
    
    # Prepare content
    content = project.prepare_content(topic, duration, language)
    
    # Fetch videos
    videos = project.fetch_stock_videos(topic, num_clips=3)
    
    # Create final video
    final_path = project.create_video(content.get('title'))
    
    return {
        "status": "success" if final_path else "failed",
        "project": project.get_project_info(),
        "content": content,
        "videos": videos,
        "final_video": final_path
    }


if __name__ == "__main__":
    # Test the module
    result = create_video_from_topic("teknologi AI 2024", duration=45)
    print(json.dumps(result, indent=2, ensure_ascii=False))