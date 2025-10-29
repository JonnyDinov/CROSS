#!/bin/bash

# Medieval RPG Bot - Quick Start Script

echo "=============================================="
echo "🏰 Medieval RPG Telegram Bot"
echo "=============================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created!"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/installed.flag" ]; then
    echo "📥 Installing dependencies..."
    pip install -q -r requirements.txt
    touch venv/installed.flag
    echo "✅ Dependencies installed!"
    echo ""
fi

# Initialize database
if [ ! -f "medieval_rpg.db" ]; then
    echo "🗄️ Initializing database..."
    python test_db.py
    echo ""
fi

# Run the bot
echo "🚀 Starting bot..."
echo ""
python run.py
