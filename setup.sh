#!/bin/bash
# Setup script for Portuguese pronunciation trainer

set -e

echo "Setting up Portuguese Pronunciation Trainer..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "To use the pronunciation trainer:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the trainer:"
echo "     python3 pronunciation_trainer.py"
echo ""
echo "To deactivate the virtual environment:"
echo "  deactivate"
