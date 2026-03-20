# AWS Lightsail Deployment Readiness Audit: Nice Trading Platform

Deploying to **AWS Lightsail** is an excellent choice for this platform due to its fixed pricing and simplicity. Here is a readiness audit and step-by-step guide for a production-grade setup.

## 1. Instance Recommendation 🖥️
*   **Minimum**: $10/month (2GB RAM, 1 vCPU).
    *   *Note*: QuestDB and Redis are memory-efficient but run best with at least 2GB of headroom.
*   **Recommended**: $20/month (4GB RAM, 2 vCPUs).
    *   *Why*: Provides stability during high-frequency volatility where QuestDB ingestion and Bot processes spike.

## 2. Readiness Check-list ✅

| Category | Status | Recommendation |
| :--- | :--- | :--- |
| **Orchestration** | 🟢 Ready | `docker-compose` is already implemented and handles restarts. |
| **Networking** | 🟡 Partial | Need an **Nginx** reverse proxy for SSL (HTTPS) and to hide QuestDB ports. |
| **Storage** | 🟢 Ready | Volumes are mapped in `docker-compose.yml` for persistence. |
| **Security** | 🟡 Partial | Need to configure Lightsail firewall to ONLY allow ports 22 (SSH) and 443 (HTTPS). |
| **Secrets** | 🟡 Partial | Use a real `.env` file on the server. Never commit the real keys. |

## 3. Production Hardening Steps 🛡️

### Step 1: Reverse Proxy (Nginx + SSL)
Do not expose port 8000 directly. Use Nginx with Let's Encrypt.
*   **Internal**: `localhost:8000`
*   **External**: `https://your-trading-domain.com`

### Step 2: Resource Constraints
Add memory limits to the `docker-compose.yml` to prevent QuestDB from consuming all system RAM and crashing the VM.
```yaml
questdb:
  deploy:
    resources:
      limits:
        memory: 1G
```

### Step 3: Firewall Rules (Lightsail Console)
*   **ALLOW 22**: Restricted to your Home IP.
*   **ALLOW 80/443**: Public for API Access.
*   **BLOCK ALL OTHERS**: QuestDB (9000), Redis (6379), and API (8000) should NOT be public.

### Step 4: Time Sync (PTP/NTP)
Ensure the Lightsail instance is synced with AWS Time Sync Service. High-frequency trading requires accurate timestamps for QuestDB.

## 4. Deployment Workflow 🚀
1.  **Clone**: `git clone your-repo` on the VM.
2.  **Config**: `cp .env.example .env` and populate keys.
3.  **Launch**: `docker-compose up -d`.
4.  **SSL**: Run `certbot` for HTTPS.

---
**Verdict**: The app is **90% Ready** for Lightsail. The main remaining task is the **Nginx Configuration** for security and SSL. 
