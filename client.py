"""
Example Python Client for Attention AI API
Demonstrates how to interact with the deployed API
"""
import requests
import cv2
import time
import json
from pathlib import Path
import base64

class AttentionAIClient:
    def __init__(self, base_url="http://localhost:5000"):
        """
        Initialize client
        
        Args:
            base_url: Base URL of the API (default: local)
                     For Render: "https://attention-ai-api.onrender.com"
        """
        self.base_url = base_url
        self.session_id = None
        self.api_base = f"{base_url}/api/v1"
    
    def start_session(self, session_id=None, timeout=60):
        """Start a new attention monitoring session"""
        url = f"{self.api_base}/session/start"
        payload = {}
        if session_id:
            payload['session_id'] = session_id
        if timeout:
            payload['timeout'] = timeout
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        if response.status_code == 201:
            self.session_id = result['session_id']
            print(f"✓ Session started: {self.session_id}")
            return result
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
            return None
    
    def add_snapshot_from_file(self, image_path):
        """Add a snapshot from a file"""
        if not self.session_id:
            print("✗ No active session. Call start_session() first.")
            return None
        
        url = f"{self.api_base}/session/{self.session_id}/snapshot"
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(url, files=files)
        
        result = response.json()
        
        if response.status_code == 200:
            print(f"✓ Snapshot {result['frames_processed']} processed")
            print(f"  Attention Score: {result['attention_score']:.1f}%")
            print(f"  Status: {result['current_status']}")
            return result
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
            return None
    
    def add_snapshot_from_base64(self, image_base64_str):
        """Add a snapshot from base64 encoded image"""
        if not self.session_id:
            print("✗ No active session. Call start_session() first.")
            return None
        
        url = f"{self.api_base}/session/{self.session_id}/snapshot"
        data = {'image_base64': image_base64_str}
        
        response = requests.post(url, data=data)
        result = response.json()
        
        if response.status_code == 200:
            print(f"✓ Snapshot {result['frames_processed']} processed")
            print(f"  Attention Score: {result['attention_score']:.1f}%")
            return result
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
            return None
    
    def add_snapshot_from_camera(self, frame):
        """Add a snapshot from camera frame (numpy array)"""
        if not self.session_id:
            print("✗ No active session. Call start_session() first.")
            return None
        
        url = f"{self.api_base}/session/{self.session_id}/snapshot"
        
        # Convert numpy array to JPEG bytes
        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            print("✗ Failed to encode frame")
            return None
        
        files = {'image': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
        response = requests.post(url, files=files)
        
        result = response.json()
        
        if response.status_code == 200:
            return result
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
            return None
    
    def get_session_status(self):
        """Get current session status"""
        if not self.session_id:
            print("✗ No active session.")
            return None
        
        url = f"{self.api_base}/session/{self.session_id}/status"
        response = requests.get(url)
        result = response.json()
        
        if response.status_code == 200:
            print(f"Session Status:")
            print(f"  Frames: {result['frames_processed']}")
            print(f"  Elapsed: {result['elapsed_time']:.1f}s")
            print(f"  Is Expired: {result['is_expired']}")
            return result
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
            return None
    
    def get_summary(self):
        """Get session summary with arrays for graphing"""
        if not self.session_id:
            print("✗ No active session.")
            return None
        
        url = f"{self.api_base}/session/{self.session_id}/summary"
        response = requests.get(url)
        result = response.json()
        
        if response.status_code == 200:
            print(f"Session Summary:")
            print(f"  Total Time: {result['total_time']:.1f}s")
            print(f"  Frames: {result['frames_processed']}")
            print(f"  Attention Score: {result['attention_score']:.1f}%")
            print(f"  Distracted Periods: {len(result['distracted_periods'])}")
            return result
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
            return None
    
    def end_session(self):
        """End session and get final summary"""
        if not self.session_id:
            print("✗ No active session.")
            return None
        
        url = f"{self.api_base}/session/{self.session_id}/end"
        response = requests.post(url)
        result = response.json()
        
        if response.status_code == 200:
            print(f"✓ Session ended")
            summary = result['final_summary']
            print(f"  Attention Score: {summary['attention_score']:.1f}%")
            print(f"  Total Time: {summary['total_time']:.1f}s")
            self.session_id = None
            return result
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
            return None
    
    def health_check(self):
        """Check API health"""
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url)
            result = response.json()
            print(f"✓ API is {result['status']}")
            print(f"  Active Sessions: {result['active_sessions']}")
            return result
        except:
            print(f"✗ API unreachable at {url}")
            return None


def example_from_files():
    """Example: Process images from files"""
    client = AttentionAIClient(base_url="http://localhost:5000")
    
    # Check API health
    client.health_check()
    
    # Start session
    client.start_session(session_id="example-1", timeout=60)
    
    # Process multiple image files
    image_dir = Path("sample_images")
    if image_dir.exists():
        for image_file in sorted(image_dir.glob("*.jpg"))[:5]:
            print(f"\nProcessing {image_file.name}...")
            result = client.add_snapshot_from_file(str(image_file))
            time.sleep(0.3)  # Simulate time between snapshots
    
    # Get session summary
    print("\n--- Final Summary ---")
    summary = client.get_summary()
    
    # End session
    client.end_session()
    
    # Display results
    if summary:
        print(f"\nResults:")
        print(f"Time array (seconds): {summary['time_array'][:10]}...")
        print(f"Attention array (ratios): {summary['attention_array'][:10]}...")
        print(f"Status array: {summary['status_array'][:10]}...")


def example_from_camera():
    """Example: Capture from webcam and send snapshots"""
    client = AttentionAIClient(base_url="http://localhost:5000")
    
    # Start session
    client.start_session(session_id="camera-demo", timeout=60)
    
    # Open camera
    cap = cv2.VideoCapture(0)
    start_time = time.time()
    frame_count = 0
    
    print("Capturing frames (press 'q' to stop)...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Send frame every 300ms
        if frame_count % 9 == 0:  # Assuming ~30 FPS, send every 300ms
            print(f"\nSending snapshot {frame_count}...")
            result = client.add_snapshot_from_camera(frame)
            if result and result['attention_score'] >= 0:
                print(f"  Score: {result['attention_score']:.1f}%")
        
        # Display frame
        cv2.imshow('Sending frames...', frame)
        
        frame_count += 1
        elapsed = time.time() - start_time
        
        # Stop after 20 seconds or if 'q' pressed
        if elapsed > 20 or cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Get results
    print("\n--- Final Summary ---")
    summary = client.get_summary()
    client.end_session()


def example_batch_processing():
    """Example: Process multiple sessions"""
    client = AttentionAIClient(base_url="http://localhost:5000")
    
    sessions_results = []
    
    # Simulate 3 different user sessions
    for user_num in range(1, 4):
        print(f"\n========== User {user_num} ==========")
        
        # Start session
        client.start_session(
            session_id=f"user-{user_num}",
            timeout=60
        )
        
        # Simulate 5 snapshots
        for snap_num in range(1, 6):
            # In real scenario, capture from camera or file
            # For demo, just wait
            time.sleep(1)
            print(f"Snapshot {snap_num} (simulated)")
        
        # Get results
        summary = client.get_summary()
        result = client.end_session()
        
        if summary:
            sessions_results.append({
                "user_id": f"user-{user_num}",
                "attention_score": summary['attention_score'],
                "total_time": summary['total_time']
            })
    
    # Summary of all users
    print("\n========== All Users Summary ==========")
    for result in sessions_results:
        print(f"{result['user_id']}: {result['attention_score']:.1f}% attention")


if __name__ == "__main__":
    import sys
    
    print("Attention AI Client Examples")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "camera":
            example_from_camera()
        elif sys.argv[1] == "batch":
            example_batch_processing()
        else:
            example_from_files()
    else:
        # Interactive mode
        print("\nUsage:")
        print("  python client.py              # Process from files")
        print("  python client.py camera       # Capture from webcam")
        print("  python client.py batch        # Multiple sessions demo")
        print("\nOr import AttentionAIClient in your own code:")
        print("  from client import AttentionAIClient")
        print("  client = AttentionAIClient('https://your-api.onrender.com')")
        print("  client.start_session()")
        print("  client.add_snapshot_from_file('image.jpg')")
        print("  summary = client.get_summary()")
        print("  client.end_session()")
