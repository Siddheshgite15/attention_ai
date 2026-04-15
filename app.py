"""
Attention AI - Render Deployment API
Web service for attention monitoring with snapshot-based input
"""
import os
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from attention_detector import AttentionSession, process_frame
from werkzeug.utils import secure_filename
import base64
import numpy as np
import cv2

# ========== Flask Setup ==========
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
UPLOAD_FOLDER = '/tmp/attention_uploads' if os.name != 'nt' else 'temp_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
SESSION_TIMEOUT = 60  # seconds - auto-stop if no snapshot for 60 seconds

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# ========== Session Management ==========
SESSIONS = {}  # {session_id: AttentionSession}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_expired_sessions():
    """Remove expired sessions (called periodically)"""
    current_time = time.time()
    expired = [sid for sid, session in SESSIONS.items() 
               if session.is_expired(current_time)]
    for sid in expired:
        del SESSIONS[sid]
    return len(expired)

# ========== API Endpoints ==========

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render monitoring"""
    cleanup_expired_sessions()
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_sessions": len(SESSIONS)
    }), 200


@app.route('/api/v1/session/start', methods=['POST'])
def start_session():
    """
    Start a new attention monitoring session
    
    JSON body (optional):
    {
        "session_id": "custom-id",  // optional, auto-generated if not provided
        "timeout": 60  // optional, seconds before auto-stop
    }
    
    Response:
    {
        "session_id": "uuid-or-custom-id",
        "message": "Session started",
        "timeout_seconds": 60
    }
    """
    try:
        data = request.get_json() or {}
        
        # Use provided session_id or generate one
        session_id = data.get('session_id') or f"session_{int(time.time() * 1000)}"
        timeout = data.get('timeout', SESSION_TIMEOUT)
        
        # Prevent duplicate sessions
        if session_id in SESSIONS:
            return jsonify({"error": "Session already exists"}), 409
        
        # Create new session
        SESSIONS[session_id] = AttentionSession(session_id, timeout)
        
        return jsonify({
            "session_id": session_id,
            "message": "Session started successfully",
            "timeout_seconds": timeout
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/v1/session/<session_id>/snapshot', methods=['POST'])
def add_snapshot(session_id):
    """
    Add a snapshot/frame to the session
    
    Multi-form data:
    - image: image file (PNG, JPG, etc.)
    OR
    - image_base64: base64 encoded image string
    
    Response:
    {
        "session_id": "...",
        "elapsed_time": 2.5,
        "frames_processed": 45,
        "attention_score": 87.5,
        "current_status": "ATTENTIVE",
        "eye_ratio": 0.35,
        "face_detected": true
    }
    """
    try:
        # Check if session exists
        if session_id not in SESSIONS:
            return jsonify({"error": "Session not found"}), 404
        
        session = SESSIONS[session_id]
        
        # Get image data
        image_data = None
        
        if 'image' in request.files:
            # File upload
            file = request.files['image']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            if not allowed_file(file.filename):
                return jsonify({"error": "Invalid file type"}), 400
            
            # Read file as bytes and convert to numpy array
            try:
                import io
                file_bytes = file.read()
                nparr = np.frombuffer(file_bytes, np.uint8)
                image_data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if image_data is None:
                    return jsonify({"error": "Failed to decode image"}), 400
            except Exception as e:
                return jsonify({"error": f"Image processing error: {str(e)}"}), 400
            
        elif 'image_base64' in request.form:
            # Base64 encoded
            image_data = request.form['image_base64']
        
        else:
            return jsonify({"error": "No image provided"}), 400
        
        # Add frame to session
        result = session.add_frame(image_data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/session/<session_id>/summary', methods=['GET'])
def get_session_summary(session_id):
    """
    Get session summary with arrays for graphing
    
    Response:
    {
        "session_id": "...",
        "total_time": 45.3,
        "frames_processed": 150,
        "attention_score": 85.5,
        "time_array": [0, 0.3, 0.6, ...],
        "attention_array": [0.35, 0.38, 0.32, ...],
        "status_array": ["ATTENTIVE", "ATTENTIVE", "DISTRACTED", ...],
        "distracted_periods": [
            {"start": 5.2, "end": 7.8},
            ...
        ]
    }
    """
    try:
        if session_id not in SESSIONS:
            return jsonify({"error": "Session not found"}), 404
        
        session = SESSIONS[session_id]
        summary = session.get_summary()
        
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/session/<session_id>/end', methods=['POST'])
def end_session(session_id):
    """
    Manually end a session and get final summary
    
    Response:
    {
        "session_id": "...",
        "final_summary": {...}
    }
    """
    try:
        if session_id not in SESSIONS:
            return jsonify({"error": "Session not found"}), 404
        
        session = SESSIONS[session_id]
        summary = session.get_summary()
        
        # Remove session
        del SESSIONS[session_id]
        
        return jsonify({
            "session_id": session_id,
            "final_summary": summary,
            "message": "Session ended"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/session/<session_id>/status', methods=['GET'])
def get_session_status(session_id):
    """
    Check if session is still active and get current stats
    
    Response:
    {
        "session_id": "...",
        "is_active": true,
        "frames_processed": 45,
        "elapsed_time": 12.5,
        "last_snapshot_time": "2024-01-15T10:30:45Z"
    }
    """
    try:
        if session_id not in SESSIONS:
            return jsonify({"error": "Session not found"}), 404
        
        session = SESSIONS[session_id]
        
        return jsonify({
            "session_id": session_id,
            "is_active": True,
            "frames_processed": len(session.frames_processed),
            "elapsed_time": session.time_data[-1] if session.time_data else 0,
            "last_snapshot_time": datetime.utcfromtimestamp(session.last_snapshot_time).isoformat() if session.last_snapshot_time else None,
            "is_expired": session.is_expired()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/sessions', methods=['GET'])
def list_sessions():
    """
    List all active sessions (useful for monitoring)
    
    Response:
    {
        "total_sessions": 3,
        "sessions": [
            {
                "session_id": "...",
                "frames_processed": 45,
                "elapsed_time": 12.5
            },
            ...
        ]
    }
    """
    cleanup_expired_sessions()
    
    sessions_list = []
    for sid, session in SESSIONS.items():
        sessions_list.append({
            "session_id": sid,
            "frames_processed": len(session.frames_processed),
            "elapsed_time": session.time_data[-1] if session.time_data else 0
        })
    
    return jsonify({
        "total_sessions": len(SESSIONS),
        "sessions": sessions_list
    }), 200


# ========== Error Handlers ==========

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ========== Main ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
