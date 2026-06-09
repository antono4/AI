#!/bin/bash

# AI Video Shorts Generator - Startup Script

echo "🎬 AI Video Shorts Generator"
echo "============================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Create directories
mkdir -p output/videos output/thumbnails output/audio output/music logs

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# Run the app
echo ""
echo "🚀 Starting AI Video Shorts Generator..."
echo "🌐 Dashboard: http://localhost:5000"
echo ""

python3 app/main.py