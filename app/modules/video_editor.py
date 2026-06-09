"""
Video Editor Module
Add captions, subtitles, music, transitions, and effects
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import random

try:
    from moviepy import (
        VideoFileClip, AudioFileClip, TextClip, ImageClip,
        CompositeVideoClip, concatenate_videoclips,
        ColorClip, vfx, afx, concataudio
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False


class CaptionGenerator:
    """Generate stylish captions for videos"""
    
    def __init__(self):
        self.font_dir = Path("app/fonts")
        self.output_dir = Path("output/captions")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Default caption styles
        self.styles = {
            'default': {
                'font_size': 48,
                'font_color': 'white',
                'stroke_color': 'black',
                'stroke_width': 2,
                'bg_color': None,
                'position': 'center'
            },
            'bold': {
                'font_size': 56,
                'font_color': '#FFD700',
                'stroke_color': 'black',
                'stroke_width': 3,
                'bg_color': (0, 0, 0, 0.7),
                'position': 'center'
            },
            'minimal': {
                'font_size': 40,
                'font_color': 'white',
                'stroke_color': None,
                'stroke_width': 0,
                'bg_color': None,
                'position': 'bottom'
            },
            'highlight': {
                'font_size': 52,
                'font_color': 'white',
                'stroke_color': '#FF6B6B',
                'stroke_width': 2,
                'bg_color': (255, 107, 107, 0.8),
                'position': 'center'
            },
            'subtitle': {
                'font_size': 44,
                'font_color': 'white',
                'stroke_color': 'black',
                'stroke_width': 1,
                'bg_color': (0, 0, 0, 0.6),
                'position': 'bottom_center'
            }
        }
    
    def create_caption(
        self, 
        text: str, 
        duration: float,
        style: str = 'default',
        position: Tuple = None
    ) -> 'TextClip':
        """Create a single caption clip"""
        if not MOVIEPY_AVAILABLE:
            return None
        
        style_config = self.styles.get(style, self.styles['default'])
        
        try:
            # Build text clip
            txt_clip = TextClip(
                text=text,
                font_size=style_config['font_size'],
                color=style_config['font_color'],
                stroke_color=style_config['stroke_color'],
                stroke_width=style_config['stroke_width'],
                font='Helvetica-Bold',
                method='caption',
                size=(1000, None),  # Max width
                debug=False
            ).with_duration(duration)
            
            # Position
            if position:
                txt_clip = txt_clip.with_position(position)
            else:
                pos = style_config['position']
                if pos == 'center':
                    txt_clip = txt_clip.with_position('center')
                elif pos == 'bottom':
                    txt_clip = txt_clip.with_position(('center', 0.85))
                elif pos == 'bottom_center':
                    txt_clip = txt_clip.with_position(('center', 0.9))
                elif pos == 'top':
                    txt_clip = txt_clip.with_position(('center', 0.1))
            
            # Add background if specified
            if style_config['bg_color']:
                bg = ColorClip(
                    size=(txt_clip.w + 40, txt_clip.h + 20),
                    color=style_config['bg_color'][:3]
                ).with_duration(duration).with_opacity(style_config['bg_color'][3] if len(style_config['bg_color']) > 3 else 0.7)
                bg = bg.with_position('center')
                
                final = CompositeVideoClip([bg, txt_clip])
                return final
            
            return txt_clip
            
        except Exception as e:
            print(f"Caption creation error: {e}")
            return None
    
    def add_captions_to_video(
        self,
        video_path: str,
        captions: List[Dict],
        style: str = 'default'
    ) -> str:
        """Add captions to video at specified times"""
        if not MOVIEPY_AVAILABLE:
            return video_path
        
        try:
            video = VideoFileClip(video_path)
            caption_clips = []
            
            for cap in captions:
                start = cap.get('start', 0)
                duration = cap.get('duration', 3)
                text = cap.get('text', '')
                
                if text:
                    cap_clip = self.create_caption(text, duration, style)
                    if cap_clip:
                        cap_clip = cap_clip.with_start(start)
                        caption_clips.append(cap_clip)
            
            # Composite
            final = CompositeVideoClip([video] + caption_clips, size=video.size)
            
            # Save
            output_path = video_path.replace('.mp4', '_captioned.mp4')
            final.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            return output_path
            
        except Exception as e:
            print(f"Add captions error: {e}")
            return video_path


class TransitionEffects:
    """Add transitions and effects between clips"""
    
    @staticmethod
    def crossfade(clip1: 'VideoFileClip', clip2: 'VideoFileClip', duration: float = 0.5) -> List['VideoFileClip']:
        """Create crossfade transition between clips"""
        fade_in = clip1.fx(vfx.fadein, duration=duration)
        fade_out = clip2.fx(vfx.fadeout, duration=duration)
        return [fade_in, fade_out]
    
    @staticmethod
    def slide(clip1: 'VideoFileClip', clip2: 'VideoFileClip', direction: str = 'left') -> List['VideoFileClip']:
        """Create slide transition"""
        w, h = clip1.size
        
        if direction == 'left':
            clip2 = clip2.with_position(lambda t: (w * (1 - t / 0.5), 0))
        elif direction == 'right':
            clip2 = clip2.with_position(lambda t: (-w * (1 - t / 0.5), 0))
        elif direction == 'up':
            clip2 = clip2.with_position(lambda t: (0, h * (1 - t / 0.5)))
        elif direction == 'down':
            clip2 = clip2.with_position(lambda t: (0, -h * (1 - t / 0.5)))
        
        return [clip1, clip2]
    
    @staticmethod
    def zoom_transition(clip: 'VideoFileClip', zoom_in: bool = True) -> 'VideoFileClip':
        """Add zoom effect to clip"""
        if zoom_in:
            return clip.fx(vfx.zoom, factor=1.3, duration=clip.duration)
        else:
            return clip.fx(vfx.zoom, factor=0.7, duration=clip.duration)
    
    @staticmethod
    def speed_up(clip: 'VideoFileClip', factor: float = 1.5) -> 'VideoFileClip':
        """Speed up clip"""
        return clip.fx(vfx.speedx, factor)


class VideoEnhancer:
    """Enhance video quality and add effects"""
    
    @staticmethod
    def adjust_brightness(clip: 'VideoFileClip', factor: float = 1.1) -> 'VideoFileClip':
        """Adjust video brightness"""
        return clip.fx(vfx.colorx, factor)
    
    @staticmethod
    def add_saturation(clip: 'VideoFileClip', factor: float = 1.2) -> 'VideoFileClip':
        """Add saturation effect"""
        return clip.fx(vfx.painting, saturation=factor)
    
    @staticmethod
    def add_blur(clip: 'VideoFileClip', radius: float = 2) -> 'VideoFileClip':
        """Add blur effect"""
        return clip.fx(vfx.blur, radius)
    
    @staticmethod
    def stabilize(clip: 'VideoFileClip') -> 'VideoFileClip':
        """Stabilize video (placeholder)"""
        # Actual stabilization requires additional libraries
        return clip


class MusicMixer:
    """Mix background music with video audio"""
    
    def __init__(self):
        self.output_dir = Path("output/mixed")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def mix_audio(
        self,
        video_path: str,
        music_path: str,
        video_volume: float = 1.0,
        music_volume: float = 0.3,
        fade_duration: float = 2.0
    ) -> str:
        """Mix video audio with background music"""
        if not MOVIEPY_AVAILABLE:
            return video_path
        
        try:
            video = VideoFileClip(video_path)
            
            # Load music
            if music_path and os.path.exists(music_path):
                music = AudioFileClip(music_path)
                
                # Loop music if shorter than video
                if music.duration < video.duration:
                    loops_needed = int(video.duration / music.duration) + 1
                    music = concataudio([music] * loops_needed)
                
                # Trim to video length
                music = music.subclipped(0, video.duration)
                
                # Fade in/out
                music = music.with_effects([
                    afx.AudioFadeIn(fade_duration),
                    afx.AudioFadeOut(fade_duration)
                ])
                
                # Adjust volume
                music = music.volumex(music_volume)
                video_audio = video.audio.volumex(video_volume) if video.audio else None
                
                # Mix
                final_audio = CompositeVideoClip([video]).audio
                if video_audio:
                    final_audio = concataudio([video_audio, music])
                else:
                    final_audio = music
                
                video = video.with_audio(final_audio)
            else:
                # Add just music track (no original audio)
                ambient = self._generate_ambient_music(video.duration)
                ambient = ambient.volumex(music_volume)
                video = video.with_audio(ambient)
            
            # Save
            output_path = video_path.replace('.mp4', '_mixed.mp4')
            video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            return output_path
            
        except Exception as e:
            print(f"Mix audio error: {e}")
            return video_path
    
    def _generate_ambient_music(self, duration: float) -> 'AudioFileClip':
        """Generate simple ambient music"""
        try:
            import numpy as np
            from scipy.io import wavfile
            import tempfile
            
            sample_rate = 22050
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Simple ambient tone
            freq1, freq2 = 220, 330
            audio = 0.2 * np.sin(2 * np.pi * freq1 * t)
            audio += 0.15 * np.sin(2 * np.pi * freq2 * t)
            
            # Fade
            fade_samples = int(sample_rate * 1)
            audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
            audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Normalize
            audio = (audio * 32767 / max(np.max(np.abs(audio)), 0.001)).astype(np.int16)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                wavfile.write(f.name, sample_rate, audio)
                temp_path = f.name
            
            return AudioFileClip(temp_path)
            
        except Exception as e:
            print(f"Ambient music error: {e}")
            return None


class VideoProcessor:
    """Main video processing pipeline"""
    
    def __init__(self):
        self.caption_gen = CaptionGenerator()
        self.transitions = TransitionEffects()
        self.enhancer = VideoEnhancer()
        self.music_mixer = MusicMixer()
        self.output_dir = Path("output/processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def process_video(
        self,
        video_path: str,
        captions: List[Dict] = None,
        music_path: str = None,
        enhance: bool = True,
        caption_style: str = 'default'
    ) -> Dict:
        """Process video with all configured options"""
        result = {
            'status': 'processing',
            'input': video_path,
            'output': video_path,
            'steps': []
        }
        
        current_path = video_path
        
        try:
            # 1. Enhance video quality
            if enhance and MOVIEPY_AVAILABLE:
                clip = VideoFileClip(current_path)
                clip = self.enhancer.adjust_brightness(clip, 1.05)
                clip = self.enhancer.add_saturation(clip, 1.1)
                
                temp_path = current_path.replace('.mp4', '_enhanced.mp4')
                clip.write_videofile(temp_path, fps=30, codec='libx264', verbose=False, logger=None)
                current_path = temp_path
                result['steps'].append({'step': 'enhance', 'status': 'success'})
            
            # 2. Add captions
            if captions and MOVIEPY_AVAILABLE:
                current_path = self.caption_gen.add_captions_to_video(current_path, captions, caption_style)
                result['steps'].append({'step': 'captions', 'status': 'success'})
            
            # 3. Mix with music
            if music_path and MOVIEPY_AVAILABLE:
                current_path = self.music_mixer.mix_audio(current_path, music_path)
                result['steps'].append({'step': 'music', 'status': 'success'})
            
            result['status'] = 'success'
            result['output'] = current_path
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            result['steps'].append({'step': 'error', 'status': 'failed', 'error': str(e)})
        
        return result
    
    def create_compilation(
        self,
        video_paths: List[str],
        captions_per_video: List[List[Dict]] = None,
        transition: str = 'crossfade'
    ) -> str:
        """Create compilation from multiple videos"""
        if not MOVIEPY_AVAILABLE or not video_paths:
            return video_paths[0] if video_paths else None
        
        try:
            clips = []
            
            for i, path in enumerate(video_paths):
                if not os.path.exists(path):
                    continue
                
                clip = VideoFileClip(path)
                
                # Apply transition effects
                if transition == 'zoom' and i > 0:
                    clip = self.transitions.zoom_transition(clip, zoom_in=True)
                
                clips.append(clip)
            
            if not clips:
                return None
            
            # Concatenate
            if transition == 'crossfade':
                final = concatenate_videoclips(clips, method='compose')
            else:
                final = concatenate_videoclips(clips)
            
            output_path = str(self.output_dir / f"compilation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
            final.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            return output_path
            
        except Exception as e:
            print(f"Compilation error: {e}")
            return video_paths[0] if video_paths else None
    
    def add_intro_outro(
        self,
        video_path: str,
        intro_text: str = None,
        outro_text: str = "LIKE | COMMENT | SUBSCRIBE"
    ) -> str:
        """Add intro and outro to video"""
        if not MOVIEPY_AVAILABLE:
            return video_path
        
        try:
            video = VideoFileClip(video_path)
            
            # Create intro
            intro = None
            if intro_text:
                intro = self._create_text_clip(intro_text, duration=2, color=(0, 0, 0))
            
            # Create outro
            outro = self._create_text_clip(outro_text, duration=3, color=(30, 30, 30))
            
            # Combine
            parts = []
            if intro:
                parts.append(intro)
            parts.append(video)
            if outro:
                parts.append(outro)
            
            final = concatenate_videoclips(parts)
            
            output_path = video_path.replace('.mp4', '_with_io.mp4')
            final.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            return output_path
            
        except Exception as e:
            print(f"Intro/outro error: {e}")
            return video_path
    
    def _create_text_clip(self, text: str, duration: float, color: Tuple) -> 'VideoFileClip':
        """Create text overlay clip"""
        bg = ColorClip(size=(1080, 1920), color=color).with_duration(duration)
        
        txt = TextClip(
            text=text,
            font_size=50,
            color='white',
            font='Helvetica-Bold',
            method='center'
        ).with_duration(duration).with_position('center')
        
        return CompositeVideoClip([bg, txt])


def auto_process_video(
    video_path: str,
    script: Dict,
    music_volume: float = 0.3,
    add_captions: bool = True
) -> Dict:
    """Automatically process video with AI-generated content"""
    processor = VideoProcessor()
    
    # Generate captions from script
    captions = []
    current_time = 2  # Start after intro
    for seg in script.get('segments', []):
        captions.append({
            'text': seg.get('text', ''),
            'start': current_time,
            'duration': seg.get('duration', 15)
        })
        current_time += seg.get('duration', 15)
    
    # Process video
    result = processor.process_video(
        video_path=video_path,
        captions=captions if add_captions else None,
        music_path=None,  # Will generate ambient
        enhance=True,
        caption_style='highlight'
    )
    
    # Add intro/outro
    if result['status'] == 'success':
        output = processor.add_intro_outro(
            result['output'],
            intro_text=script.get('title', '')[:50],
            outro_text="👍 LIKE | 💬 COMMENT | 🔔 SUBSCRIBE"
        )
        result['output'] = output
    
    return result


if __name__ == "__main__":
    # Test the module
    print("Video Editor module loaded successfully")
    print(f"Available caption styles: {list(CaptionGenerator().styles.keys())}")