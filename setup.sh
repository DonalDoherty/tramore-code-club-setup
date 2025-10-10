#!/bin/bash

# Tramore Code Club Setup Script
echo "===== Tramore Code Club Setup ====="
echo "This script will set up the Tramore Code Club folder manager."
echo

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is not installed. You'll need to install it to use this tool.${NC}"
    echo "On Ubuntu, you can install Git with: sudo apt install git"
    read -p "Do you want to continue anyway? (y/n): " continue_anyway
    if [[ $continue_anyway != "y" ]]; then
        echo "Setup aborted. Please install Git and try again."
        exit 1
    fi
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p ~/Desktop/TramoreCodeClub
mkdir -p ~/Desktop/TramoreCodeClubBackup

# Ask for GitHub details
echo
echo "Please enter your GitHub username (e.g., DonalDoherty):"
read github_username

echo "Please enter your GitHub access token for the private repository:"
read github_token

# Download the main Python script
echo "Downloading Tramore Code Club script..."
curl -s https://raw.githubusercontent.com/DonalDoherty/tramore-code-club-setup/main/tramore_code_club.py > ~/Desktop/tramore_code_club.py

# Check if download was successful
if [ $? -ne 0 ] || [ ! -s ~/Desktop/tramore_code_club.py ]; then
    echo -e "${RED}Failed to download the script.${NC}"
    echo "Please check your internet connection and try again."
    exit 1
fi

# Replace placeholders with actual values
sed -i "s/GITHUB_USERNAME_PLACEHOLDER/$github_username/g" ~/Desktop/tramore_code_club.py
sed -i "s/GITHUB_TOKEN_PLACEHOLDER/$github_token/g" ~/Desktop/tramore_code_club.py

# Make script executable
chmod +x ~/Desktop/tramore_code_club.py

# Create desktop shortcut
echo "Creating desktop shortcut..."
cat > ~/Desktop/TramoreCodeClub.desktop << EOL
[Desktop Entry]
Version=1.0
Name=Tramore Code Club
Comment=Start Tramore Code Club
Exec=python3 ~/Desktop/tramore_code_club.py
Icon=mu-editor
Terminal=true
Type=Application
Categories=Education;Development;
StartupNotify=true
EOL

chmod +x ~/Desktop/TramoreCodeClub.desktop

echo -e "${GREEN}===== Setup Complete! =====${NC}"
echo "You can now start Tramore Code Club by double-clicking the icon on your desktop."
echo "Or run it directly with: python3 ~/Desktop/tramore_code_club.py"
echo

exit 0