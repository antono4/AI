"""
AI Voiceover/TTS Module
Generate voiceover using multiple AI providers
"""

import os
import io
import base64
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

import requests
from gtts import gTTS


class VoiceoverGenerator:
    """Multi-provider AI voice generator"""
    
    def __init__(self, elevenlabs_key: str = None, openai_key: str = None):
        self.elevenlabs_key = elevenlabs_key or os.getenv('ELEVENLABS_API_KEY')
        self.openai_key = openai_key or os.getenv('OPENAI_API_KEY')
        self.output_dir = Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(
        self, 
        text: str, 
        provider: str = 'gtts',
        voice_id: str = None,
        speed: float = 1.0,
        output_format: str = 'mp3'
    ) -> Dict:
        """
        Generate voiceover from text
        
        Args:
            text: Text to convert to speech
            provider: 'gtts', 'elevenlabs', 'openai'
            voice_id: Provider-specific voice ID
            speed: Speech speed (0.5 - 2.0)
            output_format: 'mp3' or 'wav'
        
        Returns:
            Dict with audio data and metadata
        """
        providers = {
            'gtts': self._generate_gtts,
            'elevenlabs': self._generate_elevenlabs,
            'openai': self._generate_openai_tts
        }
        
        generator_func = providers.get(provider, self._generate_gtts)
        
        return generator_func(text, voice_id, speed, output_format)
    
    def _generate_gtts(self, text: str, voice_id: str, speed: float, output_format: str) -> Dict:
        """Generate using Google TTS (free, no API key needed)"""
        try:
            # Map language codes
            lang_map = {
                'id': 'id', 'en': 'en', 'ms': 'ms',
                'zh': 'zh-CN', 'ja': 'ja', 'ko': 'ko',
                'es': 'es', 'fr': 'fr', 'de': 'de'
            }
            lang = lang_map.get(voice_id or 'id', 'id')
            
            tts = gTTS(text=text, lang=lang, slow=(speed < 0.8))
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_{timestamp}.{output_format}"
            filepath = self.output_dir / filename
            tts.save(str(filepath))
            
            # Read audio data
            with open(filepath, 'rb') as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')
            
            return {
                'status': 'success',
                'provider': 'gtts',
                'filepath': str(filepath),
                'audio_data': audio_data,
                'duration': self._estimate_duration(text, speed),
                'language': lang,
                'text_length': len(text)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'provider': 'gtts',
                'error': str(e)
            }
    
    def _generate_elevenlabs(self, text: str, voice_id: str, speed: float, output_format: str) -> Dict:
        """Generate using ElevenLabs (premium AI voices)"""
        if not self.elevenlabs_key:
            return {
                'status': 'no_api_key',
                'provider': 'elevenlabs',
                'error': 'ElevenLabs API key not configured'
            }
        
        try:
            from elevenlabs import ElevenLabs
            
            client = ElevenLabs(api_key=self.elevenlabs_key)
            
            # Default voice (Indonesian female)
            voice = voice_id or 'EXAVITQ4Xr0P9AxTFMoB'
            
            # Adjust stability and similarity based on speed
            stability = min(1.0, max(0.3, 1.0 - (speed - 1.0) * 0.5))
            
            # Generate audio
            audio = client.generate(
                text=text,
                voice=voice,
                model='eleven_multilingual_v2',
                latency='normal'
            )
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_el_{timestamp}.{output_format}"
            filepath = self.output_dir / filename
            
            # Write audio chunks
            with open(filepath, 'wb') as f:
                for chunk in audio:
                    if chunk:
                        f.write(chunk)
            
            # Read audio data
            with open(filepath, 'rb') as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')
            
            return {
                'status': 'success',
                'provider': 'elevenlabs',
                'filepath': str(filepath),
                'audio_data': audio_data,
                'duration': self._estimate_duration(text, speed),
                'voice_id': voice,
                'language': 'multi'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'provider': 'elevenlabs',
                'error': str(e)
            }
    
    def _generate_openai_tts(self, text: str, voice_id: str, speed: float, output_format: str) -> Dict:
        """Generate using OpenAI TTS"""
        if not self.openai_key:
            return {
                'status': 'no_api_key',
                'provider': 'openai_tts',
                'error': 'OpenAI API key not configured'
            }
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_key)
            
            # Map voice IDs
            voice_map = {
                'alloy': 'alloy',
                'echo': 'echo', 
                'fable': 'fable',
                'onyx': 'onyx',
                'nova': 'nova',
                'shimmer': 'shimmer'
            }
            voice = voice_map.get(voice_id or 'nova', 'nova')
            
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=max(0.5, min(2.0, speed))
            )
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = 'mp3' if output_format == 'mp3' else 'wav'
            filename = f"voice_oa_{timestamp}.{ext}"
            filepath = self.output_dir / filename
            
            response.stream_to_file(filepath)
            
            # Read audio data
            with open(filepath, 'rb') as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')
            
            return {
                'status': 'success',
                'provider': 'openai_tts',
                'filepath': str(filepath),
                'audio_data': audio_data,
                'duration': self._estimate_duration(text, speed),
                'voice': voice,
                'model': 'tts-1'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'provider': 'openai_tts',
                'error': str(e)
            }
    
    def _estimate_duration(self, text: str, speed: float) -> float:
        """Estimate audio duration in seconds"""
        # Average speaking rate: ~150 words per minute at 1.0 speed
        word_count = len(text.split())
        base_duration = (word_count / 150) * 60
        return base_duration / speed
    
    def generate_segments(self, segments: List[Dict], provider: str = 'gtts') -> List[Dict]:
        """Generate voiceover for multiple text segments"""
        results = []
        
        for i, segment in enumerate(segments):
            text = segment.get('text', '')
            if not text:
                continue
            
            result = self.generate(
                text=text,
                provider=provider,
                speed=segment.get('speed', 1.0)
            )
            
            result['segment_index'] = i
            result['original_text'] = text
            results.append(result)
        
        return results
    
    def get_available_voices(self, provider: str = 'elevenlabs') -> List[Dict]:
        """Get available voices from provider"""
        if provider == 'elevenlabs' and self.elevenlabs_key:
            try:
                from elevenlabs import ElevenLabs
                
                client = ElevenLabs(api_key=self.elevenlabs_key)
                voices = client.voices.get_all().voices
                
                return [
                    {
                        'id': v.voice_id,
                        'name': v.name,
                        'gender': getattr(v, 'labels', {}).get('gender', 'unknown'),
                        'language': getattr(v, 'labels', {}).get('language', 'multi')
                    }
                    for v in voices[:20]  # Limit to 20 voices
                ]
            except Exception as e:
                return [{'error': str(e)}]
        
        # Return default voices
        return [
            {'id': 'id', 'name': 'Indonesian (gTTS)', 'gender': 'neutral', 'language': 'id'},
            {'id': 'en', 'name': 'English (gTTS)', 'gender': 'neutral', 'language': 'en'},
            {'id': 'ms', 'name': 'Malay (gTTS)', 'gender': 'neutral', 'language': 'ms'},
            {'id': 'alloy', 'name': 'Alloy (OpenAI)', 'gender': 'neutral', 'language': 'multi'},
            {'id': 'nova', 'name': 'Nova (OpenAI)', 'gender': 'female', 'language': 'multi'},
            {'id': 'onyx', 'name': 'Onyx (OpenAI)', 'gender': 'male', 'language': 'multi'}
        ]


class BackgroundMusic:
    """Background music manager"""
    
    def __init__(self):
        self.music_dir = Path("output/music")
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        
    def search_music(self, query: str, mood: str = None) -> List[Dict]:
        """Search background music"""
        # Free music sources
        results = []
        
        # YouTube Audio Library (simulated)
        results.append({
            'id': 'yt_audio_1',
            'title': f'{query} - Upbeat',
            'source': 'youtube_audio',
            'mood': 'upbeat',
            'duration': 60,
            'url': None  # Would need actual API integration
        })
        
        results.append({
            'id': 'pixabay_music_1',
            'title': f'{query} Background',
            'source': 'pixabay',
            'mood': mood or 'calm',
            'duration': 60,
            'url': None
        })
        
        return results
    
    def generate_ambient(self, duration: int = 30) -> str:
        """Generate simple ambient tone"""
        try:
            import numpy as np
            from scipy.io import wavfile
            
            sample_rate = 22050
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Generate ambient drone
            freq1 = 220  # A3
            freq2 = 330  # E4
            audio = 0.3 * np.sin(2 * np.pi * freq1 * t)
            audio += 0.2 * np.sin(2 * np.pi * freq2 * t)
            
            # Add some variation
            audio *= (1 + 0.1 * np.sin(2 * np.pi * 0.5 * t))
            
            # Apply fade in/out
            fade_duration = int(sample_rate * 0.5)
            audio[:fade_duration] *= np.linspace(0, 1, fade_duration)
            audio[-fade_duration:] *= np.linspace(1, 0, fade_duration)
            
            # Normalize
            audio = (audio * 32767 / np.max(np.abs(audio))).astype(np.int16)
            
            # Save
            filepath = self.music_dir / f"ambient_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            wavfile.write(str(filepath), sample_rate, audio)
            
            return str(filepath)
            
        except Exception as e:
            print(f"Ambient generation error: {e}")
            return None


def create_complete_audio(
    script: Dict,
    voice_provider: str = 'gtts',
    add_music: bool = True,
    music_volume: float = 0.3
) -> Dict:
    """Create complete audio track from script"""
    generator = VoiceoverGenerator()
    
    segments = script.get('segments', [])
    if not segments:
        # Create single segment from entire text
        full_text = f"{script.get('title', '')}. {script.get('description', '')}"
        segments = [{'text': full_text, 'duration': 45}]
    
    # Generate voice for each segment
    audio_segments = generator.generate_segments(segments, provider=voice_provider)
    
    # Generate background music
    music_path = None
    if add_music:
        music_gen = BackgroundMusic()
        music_path = music_gen.generate_ambient(
            duration=sum(a.get('duration', 15) for a in audio_segments)
        )
    
    return {
        'status': 'success',
        'segments': audio_segments,
        'background_music': music_path,
        'total_duration': sum(a.get('duration', 15) for a in audio_segments)
    }


if __name__ == "__main__":
    # Test the module
    test_script = {
        'title': 'Test Video',
        'description': 'This is a test',
        'segments': [
            {'text': 'Selamat datang di video fakta menarik hari ini!', 'duration': 15},
            {'text': 'Tahukah kamu bahwa...', 'duration': 10}
        ]
    }
    
    result = create_complete_audio(test_script, voice_provider='gtts')
    print(f"Audio generation: {result['status']}")
    print(f"Total duration: {result.get('total_duration', 0):.1f} seconds")