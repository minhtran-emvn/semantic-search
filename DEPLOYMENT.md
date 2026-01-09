# DEPLOYMENT

This guide deploys the Semantic Audio Search app to a Hetzner VPS using Docker, Docker Compose, and a host-level Nginx reverse proxy with Let's Encrypt SSL.

## Prerequisites

- Hetzner Cloud account
- Cloudflare account (for DNS management of emvn.co)
- SSH key pair on your local machine (`~/.ssh/id_ed25519` or similar)
- Basic terminal familiarity

## Step 1: Provision a Hetzner VPS

1. Create a new server in Hetzner Cloud.
2. Select a **CX21** instance (2 vCPU, 4GB RAM) or higher.
3. Choose **Ubuntu 22.04 LTS** or **Ubuntu 24.04 LTS**.
4. Add your SSH public key in the Hetzner UI (no password auth).
5. Record the public IP address for DNS configuration.

Estimated cost: ~EUR 5.83/month for CX21.

Optional: create a server via hcloud CLI (if you use it):

```bash
hcloud server create \
  --name semantic-search \
  --type cx21 \
  --image ubuntu-22.04 \
  --location nbg1 \
  --ssh-key <YOUR_SSH_KEY_NAME>
```

## Step 2: Connect to the VPS

```bash
ssh root@<VPS_IP>
```

(Optional but recommended) create a non-root user for deployment:

```bash
adduser deploy
usermod -aG sudo deploy
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

Update SSH settings to disable root login and password auth:

```bash
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

Reconnect as the deploy user:

```bash
ssh deploy@<VPS_IP>
```

## Step 3: Install Docker and Docker Compose

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Log out and back in for docker group changes to apply.

Enable automatic security updates:

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

Verify:

```bash
docker --version
docker compose version
```

## Step 4: Clone the Repository

```bash
git clone <REPO_URL> semantic-search
cd semantic-search
```

## Step 5: Create the .env File

Copy the template and set production values:

```bash
cp .env.example .env
chmod 600 .env
```

Edit `.env` and set the correct domain:

```bash
nano .env
```

Notes:
- `CORS_ORIGINS` must be a JSON array string (example: `["https://semantic-search.emvn.co"]`).
- `CLAP_DEVICE=cpu` is required for VPS deployments.

## Step 6: Copy Audio Files and Embeddings to the VPS

From your local machine, copy files to the VPS:

```bash
scp -r backend/data/audio deploy@<VPS_IP>:/tmp/audio
scp -r backend/data/embeddings deploy@<VPS_IP>:/tmp/embeddings
```

On the VPS, copy them into Docker volumes using the backend container:

```bash
# Start containers once to create volumes
cd semantic-search
docker compose up -d

# Copy data into volumes
sudo docker cp /tmp/audio/. semantic-audio-backend:/data/audio/
sudo docker cp /tmp/embeddings/. semantic-audio-backend:/data/embeddings/
```

Verify volume contents:

```bash
docker compose exec backend ls -lh /data/audio
docker compose exec backend ls -lh /data/embeddings
```

Storage note: current data fits in ~500MB, but 5GB is recommended for growth.

## Step 7: Build and Start Containers

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
```

## Step 8: Configure Host Nginx Reverse Proxy

Install Nginx on the host:

```bash
sudo apt install -y nginx
```

Copy the provided configuration:

```bash
sudo cp deployment/nginx/semantic-search.conf /etc/nginx/sites-available/semantic-search.conf
sudo ln -s /etc/nginx/sites-available/semantic-search.conf /etc/nginx/sites-enabled/semantic-search.conf
```

Test and reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Step 9: Obtain SSL Certificate (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d semantic-search.emvn.co
```

Enable auto-renewal:

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
sudo certbot renew --dry-run
```

## Step 10: Configure DNS in Cloudflare

1. Create an **A record** for `semantic-search.emvn.co` pointing to the VPS IP.
2. Set TTL to 300 seconds.
3. For initial setup, use **DNS only** (grey cloud). You can switch to proxied later.

Verify DNS:

```bash
nslookup semantic-search.emvn.co
```

If you enable Cloudflare proxy (orange cloud), configure Nginx to trust Cloudflare IPs for real client IPs.

## Step 11: Configure Firewall (UFW)

```bash
sudo apt install -y ufw
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable
sudo ufw status
```

## Step 12: Verify Deployment

- Backend health:

```bash
curl https://semantic-search.emvn.co/api/health
```

- Frontend load:

```bash
curl -I https://semantic-search.emvn.co/
```

- Test search:

```bash
curl -X POST https://semantic-search.emvn.co/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "rain", "top_k": 5}'
```

## How to Update

```bash
cd semantic-search
git pull

docker compose build

docker compose up -d --force-recreate
```

Verify:

```bash
curl https://semantic-search.emvn.co/api/health
```

## How to Reindex Audio

1. Copy new audio files to the VPS:

```bash
scp -r backend/data/audio/*.mp3 deploy@<VPS_IP>:/tmp/new-audio/
```

2. Copy files into the volume:

```bash
docker cp /tmp/new-audio/. semantic-audio-backend:/data/audio/
```

3. Regenerate embeddings inside the container:

```bash
docker compose exec backend python scripts/generate_embeddings.py \
  --audio-dir /data/audio \
  --output-dir /data/embeddings
```

4. Restart backend to reload the FAISS index:

```bash
docker compose restart backend
```

5. Verify health:

```bash
curl https://semantic-search.emvn.co/api/health
```

Estimated time: ~2-5 minutes per 100 files on CPU.

## Monitoring and Logs

- Container status: `docker compose ps`
- All logs: `docker compose logs -f`
- Backend logs only: `docker compose logs -f backend`
- Resource usage: `docker stats`
- Debug shell: `docker compose exec backend bash`

## Troubleshooting

- **Connection refused**: Check UFW rules and `docker compose ps`.
- **502 Bad Gateway**: Check Nginx config (`sudo nginx -t`) and backend health.
- **SSL errors**: Re-run Certbot and verify DNS.
- **CLAP model fails to load**: Check backend logs for stack traces and memory usage.
- **Audio files missing**: Verify `/data/audio` volume contents and permissions.

## Backup and Rollback

Backup volumes:

```bash
# Audio
docker run --rm -v audio-data:/data -v $(pwd):/backup ubuntu tar czf /backup/audio-backup.tar.gz /data

# Embeddings
docker run --rm -v embeddings-data:/data -v $(pwd):/backup ubuntu tar czf /backup/embeddings-backup.tar.gz /data
```

Rollback to a previous version:

```bash
cd semantic-search
git checkout <COMMIT_SHA>

docker compose build

docker compose up -d --force-recreate
```

## Known Limitations (Demo Deployment)

- No authentication or user accounts
- No user upload flow
- Single-instance deployment (no load balancing)
- CPU-only inference (500ms-1s per query)
- Limited concurrent users (5-10 recommended)
- No automated backups (use manual backups above)
- Best-effort uptime (not a production SLA)

## Cost Summary

- VPS (CX21): ~EUR 5.83/month
- Traffic: Included (20TB)
- Domain: Existing domain (no extra cost)
- Total: ~EUR 6/month
