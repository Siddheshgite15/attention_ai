"""
Simple test script for the API snapshot endpoint
"""
import requests
import cv2
import numpy as np

API_BASE = 'http://localhost:5000/api/v1'

# 1. Start a session
print("1. Starting session...")
response = requests.post(f'{API_BASE}/session/start', json={
    'session_id': 'test-session-123',
    'timeout': 60
})
print(response.json())
session_id = response.json()['session_id']

# 2. Create a test image (blank image)
print(f"\n2. Creating test image...")
test_image = np.zeros((480, 640, 3), dtype=np.uint8)
# Add some white rectangle so it's not completely blank
cv2.rectangle(test_image, (100, 100), (300, 300), (255, 255, 255), -1)
# Save and send
cv2.imwrite('test_image.jpg', test_image)

# 3. Send snapshot
print(f"\n3. Sending snapshot to session {session_id}...")
with open('test_image.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post(
        f'{API_BASE}/session/{session_id}/snapshot',
        files=files
    )
    print(f"Status Code: {response.status_code}")
    print(response.json())

# 4. Get summary
print(f"\n4. Getting session summary...")
response = requests.get(f'{API_BASE}/session/{session_id}/summary')
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Attention Score: {data.get('attention_score')}%")
    print(f"Frames Processed: {data.get('frames_processed')}")
    print(f"Total Time: {data.get('total_time')}s")
else:
    print(response.json())

# 5. End session
print(f"\n5. Ending session...")
response = requests.post(f'{API_BASE}/session/{session_id}/end')
print(f"Status Code: {response.status_code}")
print(response.json())

print("\n✓ Test completed!")
