# 🚀 Complete Guide: Deploy Attention AI to Render

## Overview

This guide will walk you through deploying your Attention AI Flask application to **Render** in less than 15 minutes.

---

## Prerequisites

Before you start, make sure you have:

- ✅ A [Render account](https://render.com) (free tier available)
- ✅ A [GitHub account](https://github.com)
- ✅ Your code pushed to a GitHub repository
- ✅ All files ready (app.py, attention_detector.py, requirements.txt, etc.)

---

## Step-by-Step Deployment

### 1️⃣ Prepare Your Git Repository

First, initialize Git and push your code to GitHub.

#### 1.1 Initialize Git (if not already done)
```bash
cd d:\yo\attention_ai
git init
git add .
git commit -m "Attention AI - Ready for Render deployment"
```

#### 1.2 Create GitHub Repository
1. Go to [github.com/new](https://github.com/new)
2. Repository name: `attention-ai`
3. Description: `Real-time attention monitoring system with face detection`
4. Choose **Public** (easier for deployment)
5. Don't initialize with README
6. Click "Create repository"

#### 1.3 Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/attention-ai.git
git branch -M main
git push -u origin main
```

**Result**: Your code is now on GitHub ✓

---

### 2️⃣ Create Render Account

1. Go to [render.com](https://render.com)
2. Click **Sign Up** (top right)
3. Create account with GitHub:
   - Click "Sign up with GitHub"
   - Authorize Render to access your GitHub
   - Select your repositories (choose `attention-ai`)
4. Complete account setup

**Result**: Render account created and authorized with GitHub ✓

---

### 3️⃣ Deploy on Render

#### 3.1 Create Web Service
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **New +** button (top right)
3. Select **Web Service**

#### 3.2 Configure Repository
1. **GitHub Accounts**: Select your GitHub account (already connected)
2. **Repository**: Search and select `attention-ai`
3. Click **Connect**

#### 3.3 Configure Service Details

Fill in the following fields:

| Field | Value | Notes |
|-------|-------|-------|
| **Name** | `attention-ai-api` | This becomes part of your URL |
| **Runtime** | `Python 3` | Auto-detected from requirements.txt |
| **Region** | Pick closest to users | (e.g., USA, EU) |
| **Branch** | `main` | Default branch |
| **Build Command** | `pip install -r requirements.txt` | Pre-filled |
| **Start Command** | `gunicorn app:app` | IMPORTANT: Don't skip this |

**Build Command** should be:
```
pip install -r requirements.txt
```

**Start Command** should be:
```
gunicorn app:app
```

#### 3.4 Set Environment Variables

1. Scroll down to **Environment**
2. Click **Add Environment Variable**
3. Add these two variables:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `PORT` | `5000` |

#### 3.5 Choose Plan

Scroll to **Plan**:
- **Free Plan** ✅ (Great for testing)
  - 750 free dyno hours/month
  - Spins down after 15 min inactivity
  - Single instance
  
- **Starter Plan** ($7/month)
  - Always on
  - Recommended for production

For testing, keep **Free Plan** selected.

#### 3.6 Deploy

Click **Create Web Service** button at the bottom.

**⏳ Wait 2-3 minutes for deployment...**

---

### 4️⃣ Monitor Deployment

#### 4.1 Watch Deployment Progress
1. You'll see a page with deployment logs
2. Look for these messages (in order):
   ```
   Setting up build...
   Building dependencies...
   Successfully installed all dependencies
   Starting service...
   Service is live!
   ```

#### 4.2 Deployment Complete
When you see:
```
Service is live at https://attention-ai-api.onrender.com
```

Your API is now **LIVE**! 🎉

---

## 5️⃣ Test Your Deployment

### 5.1 Test Health Endpoint

Open in browser or cURL:
```bash
curl https://attention-ai-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-15T12:30:45.123456",
  "active_sessions": 0
}
```

### 5.2 Test API with Your Frontend

Update your frontend to use the Render URL:

In `frontend.html`, change:
```javascript
// OLD (local development)
const API_BASE = 'http://localhost:5000/api/v1';

// NEW (production on Render)
const API_BASE = 'https://attention-ai-api.onrender.com/api/v1';
```

Then open `frontend.html` in your browser and test:
- Click "Start Monitoring"
- Allow camera access
- Watch the real-time score update
- Stop and see the graph

---

## 🔧 Troubleshooting

### Build Failed

**Error**: `pip failed to resolve dependencies`

**Solution**:
1. Check `requirements.txt` for typos
2. Verify all package versions are valid
3. Push fix to GitHub
4. Render auto-redeploys

### 404 Not Found

**Problem**: Getting 404 errors on all endpoints

**Solution**:
1. Check if service is "Live" (green status)
2. Verify correct URL in frontend
3. Wait 30 seconds for service to fully start
4. Check Render logs for errors

### API Returns 500 Errors

**Error**: `/snapshot` endpoint returns 500

**Solution**:
1. View Logs in Render dashboard
2. Look for error messages
3. Check that `gunicorn app:app` is the start command
4. Verify all imports in `app.py` and `attention_detector.py`

### Service Spins Down on Free Plan

Free Tier Behavior: Service goes to sleep after 15 minutes of no requests.

**Workaround**:
1. Add periodic health check pings
2. Upgrade to Starter Plan ($7/month)
3. Use external monitoring service

---

## 📊 View Logs

To troubleshoot, check the logs:

1. Go to your service dashboard
2. Click **Logs** tab
3. View real-time logs
4. Search for errors or issues

Common useful log commands in Render logs viewer:
- Search "Error" for failures
- Search "INFO" for information
- Search "WARNING" for warnings

---

## 🔄 Continuous Deployment

Good news! Every time you push to GitHub, Render auto-deploys:

```bash
# Make a change locally
echo "# Updated" >> README.md

# Push to GitHub
git add .
git commit -m "Update documentation"
git push origin main

# Render automatically redeploys! ✓
```

You'll see a new deployment in the Render dashboard automatically.

---

## 📈 Monitor Performance

### Real-time Metrics
In Render dashboard, click **Metrics** tab:
- CPU usage
- Memory usage
- Request count
- Error rate

### Health Check
Render automatically monitors `/health` endpoint every 30 seconds.

---

## 🚢 Update Your Frontend

### For Web Applications

If hosting frontend separately, update API base URL:

```javascript
// Production deployment on Render
const API_BASE = 'https://attention-ai-api.onrender.com/api/v1';
```

### For Mobile Apps

Same update applies:
```swift
// iOS
let apiBase = "https://attention-ai-api.onrender.com/api/v1"

// Android
String apiBase = "https://attention-ai-api.onrender.com/api/v1";
```

---

## 💾 Your Deployment Info

Once deployed, save these details:

```
Service Name: attention-ai-api
API Base URL: https://attention-ai-api.onrender.com
Health Check: https://attention-ai-api.onrender.com/health

API Endpoints:
- POST   https://attention-ai-api.onrender.com/api/v1/session/start
- POST   https://attention-ai-api.onrender.com/api/v1/session/{id}/snapshot
- GET    https://attention-ai-api.onrender.com/api/v1/session/{id}/summary
- POST   https://attention-ai-api.onrender.com/api/v1/session/{id}/end
```

---

## 🎯 Next Steps After Deployment

1. ✅ Test all API endpoints
2. ✅ Deploy your frontend (HTML/React/Vue/etc.)
3. ✅ Test full workflow (start → snapshots → results)
4. ✅ Monitor performance in Render dashboard
5. ✅ Share your deployed API with others
6. ✅ (Optional) Add database for persistence
7. ✅ (Optional) Upgrade to paid plan for production

---

## 📞 Getting Help

### Render Support
- **Documentation**: [docs.render.com](https://docs.render.com)
- **Status Page**: [status.render.com](https://status.render.com)
- **Support**: [support.render.com](https://support.render.com)

### Your API Issues
Check:
1. Render Logs (Logs tab in dashboard)
2. GitHub Actions (if configured)
3. requirements.txt validity
4. Start command correctness

---

## 🎉 You're Done!

Your Attention AI application is now **live on Render**!

### Summary of What You Deployed:
- ✅ Flask REST API
- ✅ MediaPipe face detection
- ✅ Real-time attention scoring
- ✅ Session management
- ✅ Multi-user support
- ✅ Production WSGI server (Gunicorn)

### What You Can Do Now:
- 📱 Build a mobile app that connects to your API
- 💻 Build a web frontend that uses your API
- 📊 Add a database to store attention records
- 🔐 Add authentication and API keys
- 📈 Monitor performance and scale

---

## Important Files Reference

Your deployment consists of:

| File | Purpose |
|------|---------|
| `app.py` | Flask web server with REST API |
| `attention_detector.py` | Core detection engine |
| `requirements.txt` | Python dependencies |
| `Procfile` | Process definition |
| `render.yaml` | Render configuration |

All these are automatically used by Render. No manual setup needed!

---

## URL Patterns After Deployment

Your deployed API will be at:
```
https://attention-ai-api.onrender.com
```

All endpoints:
```
Health:    GET  /health
Session:   POST /api/v1/session/start
Snapshot:  POST /api/v1/session/{id}/snapshot
Summary:   GET  /api/v1/session/{id}/summary
End:       POST /api/v1/session/{id}/end
Status:    GET  /api/v1/session/{id}/status
List:      GET  /api/v1/sessions
```

---

**Congratulations!** 🎊 Your Attention AI is now deployed to the cloud!
