#!/bin/bash

# Kubernetes AI Copilot - Quick Start Script
# This script helps you get started with the Kubernetes AI Copilot POC

echo "🕹️  Kubernetes AI Copilot - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

echo "✅ pip3 found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies. Please check the error messages above."
    exit 1
fi

echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. You can edit it to add your API keys."
    echo "   Note: The application works in demo mode without API keys."
else
    echo "✅ .env file already exists"
fi

echo ""

# Ask user what they want to do
echo "🚀 What would you like to do next?"
echo ""
echo "1) Run the demo script (recommended for first-time users)"
echo "2) Launch the full Streamlit application"
echo "3) Exit"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🎬 Running demo script..."
        python3 demo.py
        ;;
    2)
        echo ""
        echo "🌐 Launching Streamlit application..."
        echo "   The app will open in your browser at http://localhost:8501"
        echo "   Press Ctrl+C to stop the application"
        echo ""
        streamlit run app.py
        ;;
    3)
        echo ""
        echo "👋 Goodbye! You can run the demo anytime with: python3 demo.py"
        echo "   Or launch the full app with: streamlit run app.py"
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run the script again and select 1, 2, or 3."
        ;;
esac
