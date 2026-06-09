"""
YouTube OAuth Server
Simple Flask server for handling YouTube OAuth flow
"""

from flask import Flask, redirect, request, session, jsonify
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'ai-video-shorts-secret-key-2024')

# Google OAuth Config
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5000/oauth/callback')

YOUTUBE_SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly'
]

YOUTUBE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
YOUTUBE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
YOUTUBE_API_SCOPES = ' '.join(YOUTUBE_SCOPES)


def get_auth_url():
    """Generate YouTube OAuth URL"""
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': YOUTUBE_API_SCOPES,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    return f"{YOUTUBE_AUTH_URL}?{query}"


def exchange_code_for_tokens(code):
    """Exchange authorization code for tokens"""
    import requests
    
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(YOUTUBE_TOKEN_URL, data=data)
    return response.json()


def refresh_access_token(refresh_token):
    """Refresh access token"""
    import requests
    
    data = {
        'refresh_token': refresh_token,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'grant_type': 'refresh_token'
    }
    
    response = requests.post(YOUTUBE_TOKEN_URL, data=data)
    return response.json()


@app.route('/oauth/youtube')
def youtube_oauth():
    """Start YouTube OAuth flow"""
    if not GOOGLE_CLIENT_ID:
        return jsonify({
            'error': 'Google OAuth not configured',
            'message': 'Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET'
        }), 400
    
    auth_url = get_auth_url()
    return jsonify({
        'auth_url': auth_url,
        'message': 'Redirect user to auth_url for OAuth consent'
    })


@app.route('/oauth/callback')
def oauth_callback():
    """Handle OAuth callback"""
    error = request.args.get('error')
    if error:
        return jsonify({'error': error}), 400
    
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code'}), 400
    
    # Exchange code for tokens
    tokens = exchange_code_for_tokens(code)
    
    if 'access_token' in tokens:
        session['youtube_access_token'] = tokens['access_token']
        session['youtube_refresh_token'] = tokens.get('refresh_token')
        session['youtube_token_expiry'] = tokens.get('expires_in')
        
        return jsonify({
            'status': 'success',
            'message': 'YouTube connected successfully!',
            'channel': 'https://www.youtube.com/@antonockr7618'
        })
    
    return jsonify({'error': 'Failed to get tokens', 'details': tokens}), 400


@app.route('/oauth/status')
def oauth_status():
    """Check OAuth status"""
    if 'youtube_access_token' in session:
        return jsonify({
            'connected': True,
            'channel': '@antonockr7618',
            'channel_url': 'https://www.youtube.com/@antonockr7618'
        })
    
    return jsonify({
        'connected': False,
        'channel': '@antonockr7618'
    })


@app.route('/oauth/disconnect')
def oauth_disconnect():
    """Disconnect YouTube"""
    session.pop('youtube_access_token', None)
    session.pop('youtube_refresh_token', None)
    session.pop('youtube_token_expiry', None)
    
    return jsonify({
        'status': 'success',
        'message': 'YouTube disconnected'
    })


@app.route('/oauth/refresh')
def oauth_refresh():
    """Refresh access token"""
    refresh_token = session.get('youtube_refresh_token')
    
    if not refresh_token:
        return jsonify({'error': 'No refresh token'}), 400
    
    tokens = refresh_access_token(refresh_token)
    
    if 'access_token' in tokens:
        session['youtube_access_token'] = tokens['access_token']
        return jsonify({'status': 'success', 'message': 'Token refreshed'})
    
    return jsonify({'error': 'Failed to refresh', 'details': tokens}), 400


if __name__ == '__main__':
    print("🚀 YouTube OAuth Server")
    print(f"   Redirect URI: {REDIRECT_URI}")
    print(f"   Target Channel: @antonockr7618")
    app.run(debug=True, port=5001)