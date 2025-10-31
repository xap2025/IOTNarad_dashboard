# 🚀 Complete Development to Deployment Workflow

## 📚 Table of Contents
1. [Overview - What We're Doing](#overview)
2. [Your Current Setup](#current-setup)
3. [Complete Workflow Step-by-Step](#workflow)
4. [Docker Hub - Do You Need It?](#docker-hub)
5. [Key Concepts Explained](#concepts)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview - What We're Doing

**Your Goal:** 
- Develop code on laptop → Test locally → Push to GitHub → Deploy on GCP VM

**Your Method:**
- ✅ **GitHub** = Code storage (like Google Drive for code)
- ✅ **Docker Compose** = Run app locally & on server (like a package manager)
- ✅ **GCP VM** = Your server (like a rented computer)

**You DON'T Need:**
- ❌ **Docker Hub** = NOT required (explained below)
- ❌ **Cloud Run** = NOT required (you're using VM)

---

## 🏗️ Your Current Setup

### **Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR LAPTOP (Windows)                   │
│                                                             │
│  1. Code Editor (VS Code)                                  │
│  2. Git (version control)                                  │
│  3. Docker Desktop (local testing)                         │
│                                                             │
│  Workflow:                                                  │
│  Code → docker-compose up -d → Test → Git push            │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Git Push
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    GITHUB (Code Storage)                    │
│                                                             │
│  • Your code repository                                     │
│  • Version history                                          │
│  • Backup                                                   │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Git Pull
                          ▼
┌─────────────────────────────────────────────────────────────┐
│               GCP VM (Linux Server - Production)             │
│                                                             │
│  • Docker Compose installed                                 │
│  • Git installed                                            │
│  • Pulls code from GitHub                                   │
│  • Runs: docker compose up -d                               │
│  • Serves app at http://34.131.43.114:8050                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Workflow Step-by-Step

### **PHASE 1: Local Development (Your Laptop)**

#### **Step 1.1: Write/Edit Code**
```bash
# Open VS Code or your editor
# Edit files in: app/pages/dashboard.py, etc.
# Make your changes
```

#### **Step 1.2: Test Locally with Docker**
```bash
# Navigate to project folder
cd C:\Users\ridhi\IOTNarad_dashboard

# Start Docker containers
docker-compose up -d

# Check if running
docker ps

# Test in browser
http://localhost:8050/dashboard
```

**What happens here:**
- Docker Compose reads `docker-compose.yml`
- Builds your app using `Dockerfile`
- Starts 3 containers: `app`, `mqtt`, `influxdb`
- Your code runs in Docker containers
- You test if everything works

#### **Step 1.3: Stop Containers (if needed)**
```bash
docker-compose down
```

---

### **PHASE 2: Push to GitHub (Your Laptop)**

#### **Step 2.1: Check What Changed**
```bash
git status
# Shows modified files
```

#### **Step 2.2: Stage Changes**
```bash
git add .
# OR specific files: git add app/pages/dashboard.py
```

#### **Step 2.3: Commit Changes**
```bash
git commit -m "Added new dashboard feature"
```

#### **Step 2.4: Push to GitHub**
```bash
git push origin main
```

**What happens:**
- Your code is uploaded to GitHub
- Now anyone (including your GCP VM) can pull it
- It's like saving a file to Google Drive

---

### **PHASE 3: Deploy on GCP VM (Production Server)**

#### **Step 3.1: Connect to GCP VM**
```bash
# Option A: Using gcloud (from your laptop)
gcloud compute ssh iot-narad-4-0 --project iot-narad-dashboard-v2 --zone asia-south2-a

# Option B: Browser SSH (Google Cloud Console)
# Go to: https://console.cloud.google.com
# Click VM instance → SSH button
```

#### **Step 3.2: Go to Project Folder**
```bash
cd /home/xaptronicsindia/IOTNarad_dashboard
# OR: cd ~/IOTNarad_dashboard
```

#### **Step 3.3: Pull Latest Code from GitHub**
```bash
git fetch origin
git pull origin main
```

**What happens:**
- Downloads your latest code from GitHub
- Replaces old files with new ones
- Like downloading latest version from Google Drive

#### **Step 3.4: Stop Old Containers**
```bash
docker compose down
```

**Why:** 
- Stops running containers
- Frees up ports (1883, 8050)
- Prepares for fresh start

#### **Step 3.5: Rebuild Containers with New Code**
```bash
docker compose build
```

**What happens:**
- Reads `Dockerfile`
- Installs dependencies from `requirements.txt`
- Copies your NEW code into Docker image
- Creates new container image with updated code

**IMPORTANT:** 
- This is where your code gets "baked into" the container
- If code changed, this rebuilds it

#### **Step 3.6: Start Containers**
```bash
docker compose up -d
```

**What happens:**
- Starts all 3 containers (app, mqtt, influxdb)
- App runs on port 8050
- MQTT runs on port 1883
- InfluxDB runs on port 8086

#### **Step 3.7: Verify Deployment**
```bash
# Check containers are running
docker ps

# Check app logs
docker logs iotnarad_app

# Test from VM
curl http://localhost:8050

# Test from browser (your laptop)
http://34.131.43.114:8050
```

---

## 🐳 Docker Hub - Do You Need It?

### **Short Answer: NO, You DON'T Need Docker Hub!**

**Why?**

Your setup uses **Docker Compose with volume mounts**. This means:

1. **Local Development:**
   ```yaml
   # docker-compose.yml
   volumes:
     - ./app:/app/app  # Your code folder mapped directly
   ```
   - Code changes reflect **immediately** (no rebuild needed)
   - Docker just runs your local code

2. **GCP VM Deployment:**
   - You **pull code from GitHub** (git pull)
   - You **build container on VM** (docker compose build)
   - No need to push to Docker Hub

### **When Would You Need Docker Hub?**

**Docker Hub is useful if:**
- ❌ You want to share images with team (but you're using GitHub for code)
- ❌ You want to deploy to Cloud Run (but you're using VM)
- ❌ You want to deploy to multiple servers (but you have 1 VM)

**For your use case:**
- ✅ Code on GitHub (already done)
- ✅ Build on VM (docker compose build)
- ✅ No Docker Hub needed!

### **Docker Hub Analogy:**

```
GitHub = Code Storage (your source code)
Docker Hub = Container Storage (pre-built containers)

You: Store code in GitHub → Build containers on VM
NOT: Build on laptop → Push to Docker Hub → Pull on VM
```

---

## 📖 Key Concepts Explained

### **1. Docker Compose vs Docker Hub**

| **Docker Compose** | **Docker Hub** |
|-------------------|----------------|
| Runs containers locally | Stores container images online |
| Builds from Dockerfile | Pre-built images |
| Used on YOUR machine/VM | Cloud service |
| Like running an app | Like app store |

**Example:**
- **Docker Compose** = Like running `python app.py` (but in container)
- **Docker Hub** = Like npm registry (stores packages, not your code)

### **2. Why Volume Mounts?**

```yaml
volumes:
  - ./app:/app/app
```

**This means:**
- `./app` (your laptop folder) = `/app/app` (container folder)
- Change code on laptop → Container sees it immediately
- No rebuild needed during development

**But on GCP VM:**
- You still rebuild after `git pull` (to ensure dependencies are installed)

### **3. Build vs Run**

```bash
docker compose build  # Creates container image (bakes code into it)
docker compose up -d  # Runs container (starts the app)
```

**Analogy:**
- **Build** = Cooking the meal (preparing)
- **Up** = Serving the meal (running)

### **4. Git vs Docker**

| **Git** | **Docker** |
|---------|------------|
| Code version control | Code execution environment |
| Stores code changes | Runs code in containers |
| Push/Pull code | Build/Run containers |
| Like Google Drive | Like a package manager |

---

## 🎯 Your Complete Workflow (Simplified)

### **Every Time You Make Changes:**

```bash
# ┌─────────────────────────────────────────┐
# │   LAPTOP (Development)                  │
# └─────────────────────────────────────────┘

# 1. Edit code
# 2. Test locally
docker-compose up -d

# 3. Push to GitHub
git add .
git commit -m "Your changes"
git push origin main

# ┌─────────────────────────────────────────┐
# │   GCP VM (Production)                   │
# └─────────────────────────────────────────┘

# 4. SSH to VM
gcloud compute ssh iot-narad-4-0 --project iot-narad-dashboard-v2 --zone asia-south2-a

# 5. Pull latest code
cd ~/IOTNarad_dashboard
git pull origin main

# 6. Rebuild & Restart
docker compose down
docker compose build
docker compose up -d

# 7. Verify
docker ps
curl http://localhost:8050
```

---

## 🚨 Troubleshooting

### **Problem: Port Already in Use (1883, 8050)**

**Solution:**
```bash
# Find what's using the port
sudo lsof -i :1883
sudo lsof -i :8050

# Stop old containers
docker compose down

# Remove old containers
docker ps -a | grep iotnarad | awk '{print $1}' | xargs docker rm -f

# Try again
docker compose up -d
```

### **Problem: Code Changes Not Reflecting**

**Solution:**
```bash
# On VM, after git pull:
docker compose down
docker compose build --no-cache  # Force rebuild
docker compose up -d
```

### **Problem: Git Pull Fails**

**Solution:**
```bash
# Check if you have uncommitted changes
git status

# If yes, stash them
git stash

# Pull again
git pull origin main

# Restore stashed changes (if needed)
git stash pop
```

---

## ✅ Quick Reference Commands

### **Local (Laptop):**
```bash
docker-compose up -d          # Start
docker-compose down           # Stop
docker-compose logs -f        # View logs
docker ps                     # Check containers
git add .                     # Stage changes
git commit -m "message"       # Commit
git push origin main          # Push to GitHub
```

### **Production (GCP VM):**
```bash
cd ~/IOTNarad_dashboard       # Go to project
git pull origin main          # Get latest code
docker compose down          # Stop old
docker compose build          # Rebuild
docker compose up -d         # Start new
docker ps                     # Verify
docker logs iotnarad_app      # Check logs
```

---

## 📝 Summary

**Your Workflow:**
1. ✅ Code on laptop
2. ✅ Test with `docker-compose up -d`
3. ✅ Push to GitHub (`git push`)
4. ✅ Pull on VM (`git pull`)
5. ✅ Rebuild on VM (`docker compose build`)
6. ✅ Run on VM (`docker compose up -d`)

**You DON'T Need:**
- ❌ Docker Hub (code is in GitHub)
- ❌ Cloud Run (using VM)
- ❌ Complex deployment tools

**Simple = Better!** 🎉

---

**Last Updated:** 2025-10-30  
**Your Setup:** GCP VM + Docker Compose + GitHub = Perfect! ✅

