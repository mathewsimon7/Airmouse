"""
Simon Says - Hand Tracking Mouse Controller (Tasks API Edition)
Maps hand landmarks to mouse movement and pinch-to-click.
Uses MediaPipe Tasks API for compatibility with Python 3.14.
"""

import ctypes
try:
    # Explicitly load msvcrt to resolve potential 'free' symbol issues in some environments
    ctypes.CDLL('msvcrt')
except:
    pass

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import numpy as np
import time

# Configure PyAutoGUI for safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01

# Get screen dimensions
screen_width, screen_height = pyautogui.size()

# Initialize MediaPipe Hand Landmarker
MODEL_PATH = 'hand_landmarker.task'

base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)

# Smoothing buffer for cursor position (3-frame moving average)
smooth_buffer = []
BUFFER_SIZE = 3

# Click state tracking
click_threshold = 0.05  # Euclidean distance threshold for pinch
is_clicking = False

# Landmark connections for drawing
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4), # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8), # Index
    (0, 9), (9, 10), (10, 11), (11, 12), # Middle
    (0, 13), (13, 14), (14, 15), (15, 16), # Ring
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17) # Palm
]

def get_smoothed_coords(x, y):
    """Apply 3-frame moving average to reduce flicker."""
    smooth_buffer.append((x, y))
    if len(smooth_buffer) > BUFFER_SIZE:
        smooth_buffer.pop(0)
    
    avg_x = sum(p[0] for p in smooth_buffer) / len(smooth_buffer)
    avg_y = sum(p[1] for p in smooth_buffer) / len(smooth_buffer)
    return avg_x, avg_y


def draw_landmarks(frame, hand_landmarks):
    """Manually draw hand landmarks and connections."""
    h, w, _ = frame.shape
    # Draw connections
    for connection in HAND_CONNECTIONS:
        start_idx, end_idx = connection
        start_lm = hand_landmarks[start_idx]
        end_lm = hand_landmarks[end_idx]
        
        start_pt = (int(start_lm.x * w), int(start_lm.y * h))
        end_pt = (int(end_lm.x * w), int(end_lm.y * h))
        cv2.line(frame, start_pt, end_pt, (255, 255, 255), 2)
    
    # Draw joints
    for lm in hand_landmarks:
        pt = (int(lm.x * w), int(lm.y * h))
        cv2.circle(frame, pt, 5, (0, 255, 0), -1)


def main():
    global is_clicking
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    print("Simon Says - Hand Tracking Mouse Controller (Tasks API)")
    print("======================================================")
    print("Instructions:")
    print("- Move your index finger to control the cursor")
    print("- Pinch thumb and index finger to click")
    print("- Press 'q' to quit")
    print("- Move cursor to top-left corner for emergency stop")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # Convert to RGB and MediaPipe Image format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Process frame
            results = detector.detect(mp_image)
            
            if results.hand_landmarks:
                # Get the first hand detected
                hand_landmarks = results.hand_landmarks[0]
                
                # Draw landmarks
                draw_landmarks(frame, hand_landmarks)
                
                # Get index finger tip (landmark 8) and thumb tip (landmark 4)
                index_tip = hand_landmarks[8]
                thumb_tip = hand_landmarks[4]
                
                # Convert normalized coordinates to screen coordinates
                # Mirror x-coordinate for intuitive control (frame is already flipped)
                cursor_x = index_tip.x * screen_width
                cursor_y = index_tip.y * screen_height
                
                # Apply smoothing
                smooth_x, smooth_y = get_smoothed_coords(cursor_x, cursor_y)
                
                # Move cursor (with bounds checking)
                smooth_x = max(0, min(screen_width - 1, smooth_x))
                smooth_y = max(0, min(screen_height - 1, smooth_y))
                pyautogui.moveTo(smooth_x, smooth_y)
                
                # Calculate pinch distance (Euclidean)
                dx = index_tip.x - thumb_tip.x
                dy = index_tip.y - thumb_tip.y
                pinch_distance = np.sqrt(dx * dx + dy * dy)
                
                # Draw pinch line
                index_px = (int(index_tip.x * w), int(index_tip.y * h))
                thumb_px = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                
                # Determine pinch state
                is_pinched = pinch_distance < click_threshold
                
                if is_pinched:
                    # Draw red line when pinched
                    cv2.line(frame, index_px, thumb_px, (0, 0, 255), 2)
                    cv2.circle(frame, index_px, 8, (0, 0, 255), -1)
                    cv2.circle(frame, thumb_px, 8, (0, 0, 255), -1)
                    
                    if not is_clicking:
                        pyautogui.click()
                        is_clicking = True
                else:
                    # Draw green line when not pinched
                    cv2.line(frame, index_px, thumb_px, (0, 255, 0), 2)
                    cv2.circle(frame, index_px, 8, (0, 255, 0), -1)
                    cv2.circle(frame, thumb_px, 8, (0, 255, 0), -1)
                    is_clicking = False
                
                # Display status
                status = "CLICKING" if is_pinched else "MOVING"
                color = (0, 0, 255) if is_pinched else (0, 255, 0)
                cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    
            else:
                # No hand detected - cursor stays at last position
                cv2.putText(frame, "No hand detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            
            # Show preview window
            cv2.imshow("Simon Says - Hand Tracking", frame)
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        print("\nSimon Says stopped.")


if __name__ == "__main__":
    main()
