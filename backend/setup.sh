#!/bin/bash

# ScoutPulse Backend Setup Script

echo "🚀 Setting up ScoutPulse Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p static/videos
mkdir -p static/thumbnails
mkdir -p logs

# Copy environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cp env.example .env
    echo "✅ Environment file created. Please update .env with your configuration."
fi

# Initialize database
echo "🗄️ Initializing database..."
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

# Seed database
echo "🌱 Seeding database with initial data..."
python seed_data.py

echo "✅ ScoutPulse Backend setup complete!"
echo ""
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or with uvicorn:"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
