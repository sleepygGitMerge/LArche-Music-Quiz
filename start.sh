#!/bin/bash
echo "=========================================="
echo "Starting Music Quiz App Setup..."
echo "=========================================="

# Check if Python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found."
    echo "Please install it using your package manager:"
    echo "Ubuntu/Debian: sudo apt install python3 python3-venv"
    echo "MacOS: brew install python"
    exit 1
fi

# Check if Virtual Environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate environment and install dependencies
echo "Activating virtual environment..."
source venv/bin/activate
echo "Installing requirements..."
pip install -r requirements.txt

# Start the app
echo "Starting the Flask server..."
# Open browser depending on OS
if which xdg-open > /dev/null
then
  xdg-open http://127.0.0.1:5000 &
elif which open > /dev/null
then
  open http://127.0.0.1:5000 &
fi

python3 app.py