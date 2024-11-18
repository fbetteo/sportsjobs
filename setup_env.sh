#!/bin/bash

# Update the package list
sudo apt-get update
sudo apt-get install -y wget unzip
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt-get -f install -y
# Install required system libraries
sudo apt-get install -y libnss3 libx11-6 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libasound2 libxrandr2 libgtk-3-0
