#!/bin/bash
# Lightsail Instance Setup Script (Run once on VM)

echo "🛠️  Installing Docker & Docker Compose..."
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

echo "🐋 Configuring Docker permissions..."
sudo usermod -aG docker $USER

echo "🛡️ Configuring Firewall (UFW)..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

echo "✅ Setup complete. Please log out and back in for Docker permissions to take effect."
