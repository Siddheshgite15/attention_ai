# Deployment Checklist & Quick Start

## Pre-Deployment Checklist

- [ ] All files created and in place:
  - [ ] `app.py` - Flask web server
  - [ ] `attention_detector.py` - Detection engine
  - [ ] `requirements.txt` - Dependencies
  - [ ] `Procfile` - Process file for Render
  - [ ] `render.yaml` - Render configuration
  - [ ] `.gitignore` - Git ignore rules
  - [ ] `API_DOCUMENTATION.md` - API docs
  - [ ] `QUICK_START.md` - This file

- [ ] Git repository initialized and ready
- [ ] GitHub account with SSH keys configured
- [ ] Render account created (free tier available)
- [ ] No API keys or sensitive data in code

## Quick Deployment Steps

### 1. Initialize Git Repository
```bash
cd d:\yo\attention_ai
git init
git add .
git commit -m "Initial: Attention AI API for Render deployment"
```

### 2. Push to GitHub
```bash
# Create a new repository on GitHub (don't initialize with README)
git remote add origin https://github.com/YOUR_USERNAME/attention-ai.git
git branch -M main
git push -u origin main
```

### 3. Deploy on Render

1. **Go to Render.com** → Sign up/Login
2. **Click "New"** → Select **"Web Service"**
3. **Connect GitHub Repository**:
   - Select your `attention-ai` repository
   - Click "Connect"

4. **Configure Service**:
   - **Name:** `attention-ai-api`
   - **Environment:** `Python 3`
   - **Region:** Choose closest to users
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

5. **Set Environment Variables**:
   - `FLASK_ENV=production`
   - `PORT=5000`

6. **Click "Create Web Service"** and wait for deployment (2-3 minutes)

### 4. Verify Deployment

After deployment succeeds, test your API:

```bash
# Health check (replace with your Render URL)
curl https://attention-ai-api.onrender.com/health

# Should return:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:30:45.123456",
#   "active_sessions": 0
# }
```

## Local Testing Before Deployment

### Setup Local Environment
```bash
# Activate virtual environment
.\attention-env\Scripts\activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Run Flask locally
python app.py
```

### Test Endpoints Locally
```bash
# Terminal 1: Start the API
python app.py

# Terminal 2: Test requests
# Start session
curl -X POST http://localhost:5000/api/v1/session/start ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\": \"test-user\"}"

# Get health status
curl http://localhost:5000/health
```

## Integration with Frontend

### Simple HTML/JavaScript Frontend Template

Create `frontend.html` to test:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Attention AI</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial; padding: 20px; }
        button { padding: 10px; margin: 10px; cursor: pointer; }
        #score { font-size: 32px; font-weight: bold; }
        canvas { max-width: 800px; }
    </style>
</head>
<body>
    <h1>Attention Monitoring</h1>
    
    <div>
        <button onclick="startSession()">Start Monitoring</button>
        <button onclick="stopSession()">Stop Monitoring</button>
    </div>
    
    <h2>Attention Score: <span id="score">--</span>%</h2>
    
    <canvas id="attentionChart"></canvas>
    
    <script>
        const API_BASE = 'https://attention-ai-api.onrender.com/api/v1';
        let sessionId = null;
        let snapshotInterval = null;
        
        async function startSession() {
            const response = await fetch(`${API_BASE}/session/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ timeout: 120 })
            });
            const data = await response.json();
            sessionId = data.session_id;
            console.log('Session started:', sessionId);
            
            // Start capturing video (implement your camera capture here)
            startVideo();
        }
        
        function startVideo() {
            // TODO: Implement getUserMedia to capture snapshots
            // Send snapshots every 300ms
        }
        
        async function stopSession() {
            if (!sessionId) return;
            
            clearInterval(snapshotInterval);
            
            const response = await fetch(`${API_BASE}/session/${sessionId}/end`, {
                method: 'POST'
            });
            const data = await response.json();
            
            // Display final results
            console.log('Final Score:', data.final_summary.attention_score);
            displayResults(data.final_summary);
        }
        
        function displayResults(summary) {
            document.getElementById('score').textContent = 
                Math.round(summary.attention_score);
            
            // Plot graph with Chart.js
            const ctx = document.getElementById('attentionChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: summary.time_array.map(t => t.toFixed(1)),
                    datasets: [{
                        label: 'Attention Level',
                        data: summary.attention_array,
                        borderColor: '#4CAF50',
                        fill: false
                    }]
                }
            });
        }
    </script>
</body>
</html>
```

## Troubleshooting Deployment

### Build Fails on Render
1. Check `requirements.txt` for correct package versions
2. Ensure Python 3.10+ is specified in `render.yaml`
3. Check build logs in Render dashboard

### API Returns 500 Errors
1. Check "Logs" tab in Render dashboard
2. Ensure Flask environment variables are set
3. Verify `gunicorn` command is correct

### High Memory Usage
1. Reduce `SESSION_TIMEOUT` to auto-cleanup sessions
2. Implement periodic session cleanup
3. Monitor via Render dashboard

### Snapshots Not Processing
1. Test with a local image first
2. Ensure image format is supported (PNG, JPG, etc.)
3. Check file size doesn't exceed 16MB limit

## Production Optimization

### Enable Caching
Add Redis for session caching (paid tier):
```python
# In app.py
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})
```

### Database Persistence (Optional)
For storing attention records:
```python
# Add PostgreSQL on Render and implement SQLAlchemy models
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
```

### Rate Limiting
Prevent abuse:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)
```

## Monitoring & Maintenance

### Regular Checks
- Monitor active sessions in Render dashboard
- Check error rates and response times
- Review logs weekly for issues

### Updates
- Keep dependencies updated: `pip list --outdated`
- Update MediaPipe quarterly for accuracy improvements
- Monitor Render for security updates

## Cost Estimation (Render Free Tier)

- **Web Service:** Free with limitations
  - 750 free dyno hours/month
  - Auto-spins down after 15 mins inactivity
  - Suitable for low-traffic or demo apps

For production:
- **Starter Plan:** $7/month per dyno
- **Standard Plan:** $12+/month per dyno
- Database: Additional cost for persistence

## Next Steps

1. ✅ Verify local setup works
2. ✅ Push code to GitHub
3. ✅ Deploy on Render
4. ✅ Test API endpoints
5. ✅ Build frontend integration
6. ✅ Monitor performance
7. ✅ (Optional) Configure database for persistence
8. ✅ (Optional) Set up monitoring alerts

---

**Deployed API URL:** `https://attention-ai-api.onrender.com`

**Status Page:** `https://attention-ai-api.onrender.com/health`

**Full Documentation:** See `API_DOCUMENTATION.md`
