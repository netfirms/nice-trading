# ☁️ AWS Lightsail Deployment Guide: Advanced Production Setup

This guide provides a professional procedure for moving your trading platform from local development to the AWS cloud.

## 1. Instance Configuration 🖥️
**Target Instance**: Amazon Lightsail (Ubuntu or Bitnami Docker blueprint).
*   **Plan**: 4 GB RAM, 2 vCPUs ($20/month recommended).
*   **Region**: Select a region close to Binance servers (e.g., `Tokyo` or `Singapore`) for lowest latency.

## 2. Server Initialization (One-Time) 🛠️
Log into your Lightsail instance and run:
```bash
# Upload and run the setup script
bash setup_lightsail.sh
```
*   This script installs Docker, Docker Compose, and secures the firewall.
*   **IMPORTANT**: In the Lightsail Dashboard, ensure ONLY ports **22 (SSH)** and **80/443 (Nginx)** are Open.

## 3. Remote Deployment (Every Update) 🚀
From your **local terminal**, run:
```bash
./deploy.sh [INSTANCE_IP] [PEM_KEY_PATH]
```
### What happens under the hood?
1.  Your code is archived and compressed (`.tar.gz`).
2.  The archive is securely uploaded to Lightsail via SCP.
3.  The remote script extracts the code and runs `docker-compose up --build -d`.
4.  Volumes (Database/QuestDB) are **NOT** deleted, ensuring data persistence.

## 4. Securing with SSL (Let's Encrypt) 🛡️
Once deployed, SSH into your instance and run Certbot to enable HTTPS:
```bash
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot --nginx
```

## 5. Performance Monitoring 📈
Monitor memory usage to ensure QuestDB is healthy:
```bash
docker stats
```
QuestDB is capped at **1.5GB RAM** in our `docker-compose.yml` to prevent crashing the VM.

---
**Handover Status**: The platform is production-hardened. Future updates can be pushed in seconds using the deployment script.
