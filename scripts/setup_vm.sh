#!/bin/bash

# Update system
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

# Navigate to project directory (assuming script is run from project root or similar)
# We assume the code is in /home/ubuntu/quatrro or similar
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "Setting up in $PROJECT_ROOT"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "ERROR: .env file is missing!"
    echo "Please create a .env file in the project root with your GOOGLE_API_KEY."
    echo "Example: echo 'GOOGLE_API_KEY=your_key' > .env"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
source venv/bin/activate
echo "Installing dependencies..."
pip install -r requirements.txt

# Setup Systemd Service
echo "Configuring systemd service..."
SERVICE_FILE="scripts/quatrro.service"

# Update the service file with the correct path
sed -i "s|/home/ubuntu/quatrro|$PROJECT_ROOT|g" $SERVICE_FILE

# Copy service file
sudo cp $SERVICE_FILE /etc/systemd/system/quatrro.service

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl enable quatrro
sudo systemctl restart quatrro

echo "Deployment complete! Service 'quatrro' is running."
echo "Check status with: sudo systemctl status quatrro"
