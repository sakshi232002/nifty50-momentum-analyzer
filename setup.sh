#!/bin/bash

# NIFTY 50 Momentum Analyzer Setup Script

echo "======================================"
echo "NIFTY 50 Momentum Analyzer Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "======================================"
echo "Setup completed successfully!"
echo "======================================"
echo ""
echo "To run the analyzer:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Fetch NIFTY 50 stocks: python scrape_nifty50.py"
echo "3. Run momentum analysis: python momentum_analyzer.py"
echo ""
echo "To deactivate: deactivate"
echo ""