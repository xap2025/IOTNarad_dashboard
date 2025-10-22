#!/bin/bash
set -e

echo "🔹 STEP 1: Updating system packages..."
sudo apt update -y

echo "🔹 STEP 2: Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

echo "🔹 STEP 3: Installing Docker Compose plugin..."
sudo apt-get install -y docker-compose-plugin

echo "🔹 STEP 4: Adding current user to Docker group..."
sudo usermod -aG docker $USER
echo "⚠️  Please log out and log back in after this script completes to apply Docker group permissions."

echo "🔹 STEP 5: Installing Git..."
sudo apt install -y git

echo "🔹 STEP 6: Creating project folder..."
mkdir -p ~/IOTNarad_dashboard
cd ~/IOTNarad_dashboard

echo "🔹 STEP 7: Cloning project from GitHub..."
if git clone git@github.com:xap2025/IOTNarad_dashboard.git .; then
    echo "✅ Repository cloned successfully via SSH."
else
    echo "⚠️ SSH key not found or not configured."
    echo "Generating SSH key..."
    ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519 -N ""
    echo "🔑 Copy the below SSH key and add it to GitHub → Settings → SSH Keys:"
    cat ~/.ssh/id_ed25519.pub
    echo "Then re-run this script after adding your SSH key."
    exit 1
fi

echo "🔹 STEP 8: Copying environment file..."
cp .env.example .env

echo "🔹 STEP 9: Edit your environment variables if needed..."
echo "You can edit manually later with: nano .env"

echo "🔹 STEP 10: Building and starting Docker containers..."
docker compose up -d --build || true

# Fix port issues if any
echo "🔹 STEP 11: Checking port 8086 conflicts..."
if sudo lsof -i :8086 >/dev/null 2>&1; then
    echo "⚠️ Port 8086 in use. Stopping local InfluxDB/Mosquitto services..."
    sudo systemctl stop influxdb || true
    sudo systemctl disable influxdb || true
    sudo systemctl stop mosquitto || true
    sudo systemctl disable mosquitto || true
    echo "🔁 Restarting containers..."
    docker compose up -d
fi

echo "🔹 STEP 12: Checking running containers..."
docker ps

echo "🔹 STEP 13: Showing app logs (Press Ctrl+C to exit)..."
docker compose logs -f app &

echo "🔹 STEP 14: Setting up firewall for port 8050..."
sudo ufw allow 8050/tcp
sudo ufw status

echo "✅ Deployment completed successfully!"
echo "🌐 Access your app at: http://<your-server-ip>:8050"
