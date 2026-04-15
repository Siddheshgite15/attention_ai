# Attention AI - Render Deployment

A web service for real-time attention monitoring using facial analysis. Deploy on Render for easy cloud hosting.

## Features

- ✅ Snapshot-based input (no continuous streaming required)
- ✅ Automatic timeout if snapshots stop coming
- ✅ Real-time attention scoring (%)
- ✅ Time-series data for frontend graphing
- ✅ RESTful API with CORS support
- ✅ Multi-session support
- ✅ Face detection and eye aspect ratio analysis

## Architecture

```
Frontend/Mobile App
        ↓
    HTTP Requests (multipart/form-data)
        ↓
   Render Web Service (Flask API)
        ↓
Attention Detection Engine (MediaPipe)
        ↓
    Session Management
        ↓
    JSON Response
        ↓
Frontend/Mobile App (display score + graph)
```

## API Documentation

### Base URL
```
https://your-app.onrender.com/api/v1
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456",
  "active_sessions": 2
}
```

---

#### 2. Start Session
```http
POST /api/v1/session/start
Content-Type: application/json

{
  "session_id": "user-123",          // optional, auto-generated if omitted
  "timeout": 60                       // optional, seconds before auto-stop
}
```

**Response (201 Created):**
```json
{
  "session_id": "user-123",
  "message": "Session started successfully",
  "timeout_seconds": 60
}
```

**Error Response (409 Conflict):**
```json
{
  "error": "Session already exists"
}
```

---

#### 3. Add Snapshot to Session
```http
POST /api/v1/session/{session_id}/snapshot
Content-Type: multipart/form-data

image: <PNG/JPG file>
```

**OR with base64:**
```http
POST /api/v1/session/{session_id}/snapshot
Content-Type: application/x-www-form-urlencoded

image_base64=iVBORw0KGgoAAAANSUhEUgAAAAUA...
```

**Response (200 OK):**
```json
{
  "session_id": "user-123",
  "elapsed_time": 2.543,
  "frames_processed": 5,
  "attention_score": 87.5,
  "current_status": "ATTENTIVE",
  "eye_ratio": 0.35,
  "face_detected": true,
  "distracted_periods": [
    {
      "start": 0.5,
      "end": 1.2
    }
  ]
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Session not found"
}
```

---

#### 4. Get Session Summary
```http
GET /api/v1/session/{session_id}/summary
```

**Response (200 OK):**
```json
{
  "session_id": "user-123",
  "total_time": 45.3,
  "frames_processed": 150,
  "attention_score": 85.5,
  "time_array": [0, 0.3, 0.6, 0.9, 1.2, ...],
  "attention_array": [0.35, 0.38, 0.32, 0.41, 0.39, ...],
  "status_array": ["ATTENTIVE", "ATTENTIVE", "DISTRACTED", "ATTENTIVE", ...],
  "distracted_periods": [
    {
      "start": 5.2,
      "end": 7.8
    },
    {
      "start": 12.1,
      "end": 14.5
    }
  ]
}
```

---

#### 5. End Session
```http
POST /api/v1/session/{session_id}/end
```

**Response (200 OK):**
```json
{
  "session_id": "user-123",
  "final_summary": {
    "total_time": 45.3,
    "frames_processed": 150,
    "attention_score": 85.5,
    "time_array": [...],
    "attention_array": [...],
    "status_array": [...],
    "distracted_periods": [...]
  },
  "message": "Session ended"
}
```

---

#### 6. Check Session Status
```http
GET /api/v1/session/{session_id}/status
```

**Response (200 OK):**
```json
{
  "session_id": "user-123",
  "is_active": true,
  "frames_processed": 45,
  "elapsed_time": 12.5,
  "last_snapshot_time": "2024-01-15T10:30:55.123456Z",
  "is_expired": false
}
```

---

#### 7. List All Sessions
```http
GET /api/v1/sessions
```

**Response (200 OK):**
```json
{
  "total_sessions": 3,
  "sessions": [
    {
      "session_id": "user-123",
      "frames_processed": 45,
      "elapsed_time": 12.5
    },
    {
      "session_id": "user-456",
      "frames_processed": 23,
      "elapsed_time": 8.2
    }
  ]
}
```

---

## Frontend Usage Example (JavaScript)

### Start a Session
```javascript
async function startSession(userId) {
  const response = await fetch('https://your-app.onrender.com/api/v1/session/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: userId,
      timeout: 60
    })
  });
  
  const data = await response.json();
  return data.session_id;
}
```

### Send Snapshot
```javascript
async function sendSnapshot(sessionId, videoElement) {
  const canvas = document.createElement('canvas');
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(videoElement, 0, 0);
  
  const formData = new FormData();
  canvas.toBlob(blob => {
    formData.append('image', blob, 'snapshot.jpg');
    
    fetch(`https://your-app.onrender.com/api/v1/session/${sessionId}/snapshot`, {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      console.log('Attention Score:', data.attention_score, '%');
      console.log('Status:', data.current_status);
    });
  }, 'image/jpeg');
}

// Send snapshot every 300ms
setInterval(() => sendSnapshot(sessionId, videoElement), 300);
```

### Get Final Summary and Display Graph
```javascript
async function getSessionData(sessionId) {
  const response = await fetch(
    `https://your-app.onrender.com/api/v1/session/${sessionId}/summary`
  );
  const data = await response.json();
  
  // Plot with Chart.js or similar
  plotAttentionGraph(data.time_array, data.attention_array);
  showFinalScore(data.attention_score);
  
  return data;
}

function plotAttentionGraph(timeArray, attentionArray) {
  const ctx = document.getElementById('attentionChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: timeArray,
      datasets: [{
        label: 'Attention Level',
        data: attentionArray,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 1
        }
      }
    }
  });
}
```

---

## Deployment on Render

### Step 1: Prepare Repository
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/attention-ai.git
git push -u origin main
```

### Step 2: Create Render Service
1. Go to [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** `attention-ai-api`
   - **Runtime:** `Python 3.10`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment Variables:**
     - `FLASK_ENV=production`
     - `PORT=5000`

### Step 3: Deploy
Click "Create Web Service" and wait for deployment to complete.

Your API will be available at:
```
https://attention-ai-api.onrender.com
```

---

## Local Development

### Setup
```bash
# Create virtual environment
python -m venv attention-env
source attention-env/bin/activate  # On Windows: attention-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
# API available at http://localhost:5000
```

### Testing API
```bash
# Start session
curl -X POST http://localhost:5000/api/v1/session/start \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-1", "timeout": 60}'

# Send snapshot (replace with actual image file)
curl -X POST http://localhost:5000/api/v1/session/test-1/snapshot \
  -F "image=@snapshot.jpg"

# Get summary
curl http://localhost:5000/api/v1/session/test-1/summary

# End session
curl -X POST http://localhost:5000/api/v1/session/test-1/end
```

---

## Configuration

### Environment Variables
- `FLASK_ENV`: Set to `production` on Render
- `PORT`: Port number (default: 5000)

### Session Settings (in `app.py`)
- `SESSION_TIMEOUT`: Seconds before auto-stopping inactive sessions (default: 60)
- `MAX_CONTENT_LENGTH`: Max file size for uploads (default: 16MB)

### Attention Detection (in `attention_detector.py`)
- `ATTENTION_THRESHOLD`: Eye aspect ratio threshold for attention detection (default: 0.2)
- `LEFT_EYE` / `RIGHT_EYE`: MediaPipe landmark indices for eye detection

---

## How Attention Scoring Works

1. **Face Detection:** Uses MediaPipe Face Mesh to detect facial landmarks
2. **Eye Aspect Ratio:** Calculates the ratio of eye opening
3. **Threshold:** If ratio > 0.2, marked as "ATTENTIVE" else "DISTRACTED"
4. **Overall Score:** Percentage of frames marked as ATTENTIVE

### Eye Landmarks Used
- **LEFT_EYE:** Indices [33, 160, 158, 133, 153, 144]
- **RIGHT_EYE:** Indices [362, 385, 387, 263, 373, 380]

---

## Troubleshooting

### "Face not detected" responses
- Ensure image is clear with good lighting
- Face should be centered and clearly visible
- Resolution should be at least 320x240

### High false positives/negatives
- Adjust `ATTENTION_THRESHOLD` in `attention_detector.py`
- Increase sample size (more snapshots = more accurate)

### Session timeout too quick
- Increase `SESSION_TIMEOUT` in `app.py`
- Ensure frontend sends snapshots at regular intervals

---

## Performance Notes

- Processes single frames (not video streams)
- ~200-400ms per frame on standard CPU
- Suitable for ~3-5 snapshots/second
- Multi-session capable (~100+ concurrent sessions on free tier)

---

## License

MIT License - Free for commercial and personal use.

---

## Support

For issues or questions, create a GitHub issue or contact the development team.
