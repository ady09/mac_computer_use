#!/bin/bash

echo "🔧 Installing OCR dependencies for test automation..."

# Check if we're in the right directory
if [ ! -f "api_server.py" ]; then
    echo "❌ Please run this from the mac_computer_use directory"
    exit 1
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Install tesseract via homebrew if not installed
if ! command -v tesseract &> /dev/null; then
    echo "📦 Installing tesseract via Homebrew..."
    brew install tesseract
else
    echo "✅ Tesseract already installed"
fi

# Install Python OCR packages
echo "📦 Installing Python OCR packages..."
pip install pytesseract Pillow opencv-python

echo "✅ OCR dependencies installed successfully!"
echo ""
echo "🧪 Testing OCR installation..."
python -c "import pytesseract; print('✅ pytesseract imported successfully')"
python -c "import PIL; print('✅ PIL imported successfully')"
python -c "import cv2; print('✅ OpenCV imported successfully')"

echo ""
echo "🎉 OCR setup complete! The test framework can now use real OCR."