"""
Attention Detection Module
Handles face detection and attention scoring using MediaPipe
"""
import mediapipe as mp
import numpy as np
from typing import Tuple, List, Dict
import base64
import cv2
from io import BytesIO
from PIL import Image

# ========== MediaPipe Setup ==========
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

ATTENTION_THRESHOLD = 0.2  # Eye aspect ratio threshold for attention

def get_eye_ratio(landmarks, eye_indices, w: int, h: int) -> float:
    """Calculate eye aspect ratio from landmarks"""
    points = []
    for i in eye_indices:
        x = int(landmarks[i].x * w)
        y = int(landmarks[i].y * h)
        points.append((x, y))

    vertical = abs(points[1][1] - points[5][1])
    horizontal = abs(points[0][0] - points[3][0])

    return vertical / horizontal if horizontal != 0 else 0


def process_frame(frame_data) -> Dict:
    """
    Process a single frame and return attention status and score
    
    Args:
        frame_data: numpy array of frame (BGR format), base64 encoded image string, or bytes
        
    Returns:
        Dict with keys:
            - status: "ATTENTIVE" or "DISTRACTED"
            - left_eye_ratio: float
            - right_eye_ratio: float
            - avg_eye_ratio: float
            - face_detected: bool
    """
    try:
        # Handle base64 encoded image (string)
        if isinstance(frame_data, str):
            img_data = base64.b64decode(frame_data)
            img = Image.open(BytesIO(img_data))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Assume it's already a numpy array (BGR format)
        elif isinstance(frame_data, np.ndarray):
            frame = frame_data
        
        else:
            return {"error": f"Unsupported frame data type: {type(frame_data)}", "status": "ERROR"}

        if frame is None or frame.size == 0:
            return {"error": "Empty frame data", "status": "ERROR"}

        h, w = frame.shape[:2] if len(frame.shape) >= 2 else (frame.shape[0], 1)
        
        # Convert to RGB for MediaPipe
        if len(frame.shape) == 2:  # Grayscale
            rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        else:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = face_mesh.process(rgb)

        status = "DISTRACTED"
        face_detected = False
        left_eye_ratio = 0
        right_eye_ratio = 0
        avg_eye_ratio = 0

        if results.multi_face_landmarks:
            face_detected = True
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark

                left_eye_ratio = get_eye_ratio(landmarks, LEFT_EYE, w, h)
                right_eye_ratio = get_eye_ratio(landmarks, RIGHT_EYE, w, h)
                avg_eye_ratio = (left_eye_ratio + right_eye_ratio) / 2

                if avg_eye_ratio > ATTENTION_THRESHOLD:
                    status = "ATTENTIVE"
                else:
                    status = "DISTRACTED"

                break  # Process only first face

        return {
            "status": status,
            "left_eye_ratio": float(left_eye_ratio),
            "right_eye_ratio": float(right_eye_ratio),
            "avg_eye_ratio": float(avg_eye_ratio),
            "face_detected": face_detected
        }
    
    except Exception as e:
        return {"error": f"Frame processing failed: {str(e)}", "status": "ERROR"}


class AttentionSession:
    """Manages a single attention monitoring session"""
    
    def __init__(self, session_id: str, timeout_seconds: int = 30):
        self.session_id = session_id
        self.timeout_seconds = timeout_seconds
        self.start_time = None
        self.last_snapshot_time = None
        self.frames_processed = []
        self.time_data = []
        self.attention_data = []
        self.status_data = []
        self.distracted_periods = []
        self.last_status = "ATTENTIVE"
        self.distraction_start = None
        
    def add_frame(self, frame_data, current_timestamp: float = None) -> Dict:
        """
        Add a frame to the session and compute metrics
        
        Args:
            frame_data: Image data (numpy array or base64 string)
            current_timestamp: Unix timestamp (uses current time if not provided)
            
        Returns:
            Session stats with current attention score
        """
        import time as time_module
        
        if current_timestamp is None:
            current_timestamp = time_module.time()
        
        if self.start_time is None:
            self.start_time = current_timestamp
        
        self.last_snapshot_time = current_timestamp
        
        # Process frame
        result = process_frame(frame_data)
        
        if result.get("error"):
            return {"error": result["error"]}
        
        # Calculate elapsed time
        elapsed = current_timestamp - self.start_time
        status = result["status"]
        
        # Track attention periods
        if status == "ATTENTIVE":
            if self.last_status == "DISTRACTED" and self.distraction_start:
                self.distracted_periods.append({
                    "start": self.distraction_start - self.start_time,
                    "end": current_timestamp - self.start_time
                })
                self.distraction_start = None
        else:
            if self.last_status == "ATTENTIVE":
                self.distraction_start = current_timestamp
        
        self.last_status = status
        
        # Store data
        self.time_data.append(elapsed)
        self.attention_data.append(result["avg_eye_ratio"])
        self.status_data.append(status)
        self.frames_processed.append({
            "time": elapsed,
            "status": status,
            "eye_ratio": result["avg_eye_ratio"]
        })
        
        # Calculate overall attention score (percentage of frames marked ATTENTIVE)
        attentive_count = sum(1 for s in self.status_data if s == "ATTENTIVE")
        attention_score = (attentive_count / len(self.status_data)) * 100 if self.status_data else 0
        
        return {
            "session_id": self.session_id,
            "elapsed_time": elapsed,
            "frames_processed": len(self.frames_processed),
            "attention_score": attention_score,
            "current_status": status,
            "face_detected": result["face_detected"],
            "eye_ratio": result["avg_eye_ratio"],
            "distracted_periods": self.distracted_periods
        }
    
    def get_summary(self) -> Dict:
        """Get complete session summary"""
        if not self.time_data:
            return {"error": "No frames processed"}
        
        total_time = self.time_data[-1] if self.time_data else 0
        attentive_count = sum(1 for s in self.status_data if s == "ATTENTIVE")
        attention_score = (attentive_count / len(self.status_data)) * 100 if self.status_data else 0
        
        return {
            "session_id": self.session_id,
            "total_time": total_time,
            "frames_processed": len(self.frames_processed),
            "attention_score": attention_score,
            "time_array": self.time_data,
            "attention_array": self.attention_data,
            "status_array": self.status_data,
            "distracted_periods": self.distracted_periods
        }
    
    def is_expired(self, current_time: float = None) -> bool:
        """Check if session has expired due to timeout"""
        import time as time_module
        
        if current_time is None:
            current_time = time_module.time()
        
        if self.last_snapshot_time is None:
            return False
        
        return (current_time - self.last_snapshot_time) > self.timeout_seconds
