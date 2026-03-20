#!/bin/bash
# Local Deployment Script for Nice Trading Platform
# Usage: ./deploy.sh [LIGHTSAIL_IP] [SSH_KEY_PATH]

IP=$1
KEY=$2
USER="bitnami" # Default for Lightsail Docker blueprints or ubuntu

if [ -z "$IP" ] || [ -z "$KEY" ]; then
    echo "Usage: ./deploy.sh [LIGHTSAIL_IP] [SSH_KEY_PATH]"
    exit 1
fi

echo "🚀 Packaging codebase..."
tar -czf project.tar.gz \
    --exclude='venv' \
    --exclude='.git' \
    --exclude='logs/*' \
    --exclude='trading_bot.db' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    .

echo "📤 Uploading to Lightsail ($IP)..."
scp -i "$KEY" project.tar.gz "$USER@$IP:/home/$USER/"

echo "🏗️  Deploying on remote..."
ssh -i "$KEY" "$USER@$IP" << 'EOF'
    mkdir -p nice-trading
    tar -xzf project.tar.gz -C nice-trading
    cd nice-trading
    # Restart the fleet
    docker-compose down
    docker-compose up --build -d
    echo "✅ Deployment complete!"
EOF

rm project.tar.gz
echo "🎉 Done! Dashboard should be at http://$IP"
