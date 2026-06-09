"""
YouTube Uploader Module
Upload videos to YouTube with metadata, thumbnails, and scheduling
"""

import os
import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import httpx

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Import config
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    YOUTUBE_CLIENT_SECRET,
    YOUTUBE_TOKEN_PICKLE,
    DEFAULT_VIDEO_CATEGORY,
    DEFAULT_PRIVACY_STATUS,
    AUTO_GENERATE_THUMBNAIL
)


class YouTubeAuth:
    """YouTube OAuth authentication handler"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, client_secret_file: str = None):
        self.client_secret_file = client_secret_file or YOUTUBE_CLIENT_SECRET
        self.token_file = YOUTUBE_TOKEN_PICKLE
        self.credentials = None
    
    def get_authenticated_service(self):
        """Get authenticated YouTube service"""
        credentials = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as f:
                credentials = pickle.load(f)
        
        # Check if credentials are valid
        if credentials and credentials.valid:
            return build('youtube', 'v3', credentials=credentials)
        
        # Refresh if expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            # Run OAuth flow
            if os.path.exists(self.client_secret_file):
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secret_file,
                    self.SCOPES
                )
                credentials = flow.run_local_server(port=0)
            else:
                raise FileNotFoundError(f"Client secret file not found: {self.client_secret_file}")
        
        # Save token
        with open(self.token_file, 'wb') as f:
            pickle.dump(credentials, f)
        
        return build('youtube', 'v3', credentials=credentials)
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        if not os.path.exists(self.token_file):
            return False
        
        try:
            credentials = None
            with open(self.token_file, 'rb') as f:
                credentials = pickle.load(f)
            
            return credentials and credentials.valid
        except:
            return False
    
    def revoke(self):
        """Revoke authentication"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
            return True
        return False


class ThumbnailGenerator:
    """Generate thumbnails for videos"""
    
    def __init__(self):
        self.output_dir = Path("output/thumbnails")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_thumbnail(
        self,
        title: str,
        style: str = 'default',
        output_format: str = 'png'
    ) -> Optional[str]:
        """Create thumbnail image"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create image
            width, height = 1280, 720
            img = Image.new('RGB', (width, height), color=self._get_style_color(style))
            
            draw = ImageDraw.Draw(img)
            
            # Add gradient overlay
            for i in range(height // 2):
                alpha = int(255 * (1 - i / (height // 2)) * 0.3)
                draw.rectangle([(0, i), (width, i + 1)], fill=(0, 0, 0))
            
            # Add title text
            self._draw_centered_text(
                draw, title[:60], 
                (width // 2, height // 2),
                font_size=48,
                color='white'
            )
            
            # Add decoration
            draw.text((width // 2, height - 80), "🎬 AI Generated", anchor='mm', fill='yellow')
            
            # Save
            filename = f"thumb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
            filepath = self.output_dir / filename
            img.save(str(filepath), quality=95)
            
            return str(filepath)
            
        except Exception as e:
            print(f"Thumbnail creation error: {e}")
            return None
    
    def _get_style_color(self, style: str) -> tuple:
        """Get background color based on style"""
        colors = {
            'default': (30, 30, 60),
            'dark': (20, 20, 30),
            'vibrant': (50, 30, 80),
            'minimal': (40, 40, 45),
            'golden': (60, 50, 20)
        }
        return colors.get(style, (30, 30, 60))
    
    def _draw_centered_text(
        self, 
        draw, 
        text: str, 
        position: tuple, 
        font_size: int = 48, 
        color: str = 'white'
    ):
        """Draw centered text"""
        try:
            # Use default font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = position[0] - text_width // 2
        y = position[1] - text_height // 2
        
        # Draw with shadow
        draw.text((x + 2, y + 2), text, font=font, fill='black')
        draw.text((x, y), text, font=font, fill=color)


class YouTubeUploader:
    """Main YouTube upload handler"""
    
    def __init__(self, auth: YouTubeAuth = None):
        self.auth = auth or YouTubeAuth()
        self.youtube = None
        self.thumbnail_gen = ThumbnailGenerator()
    
    def connect(self) -> bool:
        """Connect to YouTube API"""
        try:
            self.youtube = self.auth.get_authenticated_service()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str] = None,
        category: str = DEFAULT_VIDEO_CATEGORY,
        privacy: str = DEFAULT_PRIVACY_STATUS,
        thumbnail_path: str = None,
        scheduled_time: datetime = None
    ) -> Dict:
        """Upload video to YouTube"""
        
        if not self.youtube:
            if not self.connect():
                return {'status': 'error', 'message': 'Failed to connect to YouTube'}
        
        if not os.path.exists(video_path):
            return {'status': 'error', 'message': f'Video file not found: {video_path}'}
        
        try:
            # Generate thumbnail if not provided
            if not thumbnail_path and AUTO_GENERATE_THUMBNAIL:
                thumbnail_path = self.thumbnail_gen.create_thumbnail(title)
            
            # Build snippet
            snippet = {
                'title': title[:100],  # YouTube limit
                'description': description[:5000],  # YouTube limit
                'tags': (tags or [])[:500],  # YouTube limit
                'categoryId': category,
                'defaultLanguage': 'id'
            }
            
            # Build status
            status = {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': False
            }
            
            # Add scheduling
            if scheduled_time:
                status['publishAt'] = scheduled_time.isoformat()
            
            # Build body
            body = {
                'snippet': snippet,
                'status': status
            }
            
            # Upload
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True
            )
            
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            # Execute upload
            response = request.execute()
            
            # Upload thumbnail if available
            if thumbnail_path and os.path.exists(thumbnail_path):
                self._upload_thumbnail(response['id'], thumbnail_path)
            
            return {
                'status': 'success',
                'video_id': response['id'],
                'video_url': f"https://youtu.be/{response['id']}",
                'title': response['snippet']['title'],
                'uploaded_at': response.get('snippet', {}).get('publishedAt', datetime.now().isoformat())
            }
            
        except HttpError as e:
            return {
                'status': 'error',
                'message': f"YouTube API error: {str(e)}",
                'error_code': e.resp.status
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _upload_thumbnail(self, video_id: str, thumbnail_path: str):
        """Upload custom thumbnail"""
        try:
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            )
            request.execute()
        except Exception as e:
            print(f"Thumbnail upload error: {e}")
    
    def get_video_info(self, video_id: str) -> Dict:
        """Get video information"""
        if not self.youtube:
            return {'status': 'error', 'message': 'Not connected'}
        
        try:
            response = self.youtube.videos().list(
                part='snippet,statistics,status',
                id=video_id
            ).execute()
            
            if response['items']:
                return {
                    'status': 'success',
                    'video': response['items'][0]
                }
            return {'status': 'not_found'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def update_video(
        self,
        video_id: str,
        title: str = None,
        description: str = None,
        tags: List[str] = None
    ) -> Dict:
        """Update video metadata"""
        if not self.youtube:
            return {'status': 'error', 'message': 'Not connected'}
        
        try:
            # Get current video
            current = self.youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not current['items']:
                return {'status': 'not_found'}
            
            snippet = current['items'][0]['snippet']
            
            # Update fields
            if title:
                snippet['title'] = title[:100]
            if description:
                snippet['description'] = description[:5000]
            if tags:
                snippet['tags'] = tags[:500]
            
            # Update
            self.youtube.videos().update(
                part='snippet',
                body={'snippet': snippet, 'id': video_id}
            ).execute()
            
            return {'status': 'success', 'message': 'Video updated'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def delete_video(self, video_id: str) -> Dict:
        """Delete video"""
        if not self.youtube:
            return {'status': 'error', 'message': 'Not connected'}
        
        try:
            self.youtube.videos().delete(id=video_id).execute()
            return {'status': 'success', 'message': 'Video deleted'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_channel_info(self) -> Dict:
        """Get channel information"""
        if not self.youtube:
            return {'status': 'error', 'message': 'Not connected'}
        
        try:
            response = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                mine=True
            ).execute()
            
            if response['items']:
                channel = response['items'][0]
                return {
                    'status': 'success',
                    'channel': {
                        'id': channel['id'],
                        'title': channel['snippet']['title'],
                        'subscribers': channel['statistics']['subscriberCount'],
                        'videos': channel['statistics']['videoCount'],
                        'views': channel['statistics']['viewCount']
                    }
                }
            return {'status': 'not_found'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


class BatchUploader:
    """Handle batch video uploads"""
    
    def __init__(self):
        self.uploader = YouTubeUploader()
        self.upload_history = []
    
    def upload_playlist(
        self,
        videos: List[Dict],
        schedule_interval: int = 24  # hours
    ) -> Dict:
        """Upload multiple videos with scheduling"""
        results = []
        
        for i, video_info in enumerate(videos):
            # Calculate schedule time
            scheduled_time = datetime.now() + timedelta(hours=schedule_interval * i)
            
            result = self.uploader.upload_video(
                video_path=video_info['video_path'],
                title=video_info['title'],
                description=video_info['description'],
                tags=video_info.get('tags', []),
                privacy='private',  # Start private for review
                scheduled_time=scheduled_time
            )
            
            result['index'] = i
            results.append(result)
            
            if result['status'] == 'success':
                self.upload_history.append(result)
        
        return {
            'status': 'completed',
            'total': len(videos),
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] != 'success']),
            'results': results
        }
    
    def get_history(self) -> List[Dict]:
        """Get upload history"""
        return self.upload_history


def quick_upload(
    video_path: str,
    title: str,
    description: str = "",
    tags: List[str] = None,
    privacy: str = 'private'
) -> Dict:
    """Quick upload without scheduling"""
    uploader = YouTubeUploader()
    
    return uploader.upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        privacy=privacy
    )


if __name__ == "__main__":
    # Test the module
    auth = YouTubeAuth()
    print(f"Authenticated: {auth.is_authenticated()}")
    print("YouTube Uploader module loaded successfully")