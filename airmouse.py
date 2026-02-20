"""
Simon Says - Hand Tracking Mouse Controller (Bare Python MVP)
Maps hand landmarks to mouse movement and pinch-to-click.
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Configure PyAutoGUI for safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01

# Get screen dimensions
screen_width, screen_height = pyautogui.size()

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Smoothing buffer for cursor position (3-frame moving average)
smooth_buffer = []
BUFFER_SIZE = 3

# Click state tracking
click_threshold = 0.05  # Euclidean distance threshold for pinch
is_clicking = False


def get_smoothed_coords(x, y):
    """Apply 3-frame moving average to reduce flicker."""
    smooth_buffer.append((x, y))
    if len(smooth_buffer) > BUFFER_SIZE:
        smooth_buffer.pop(0)
    
    avg_x = sum(p[0] for p in smooth_buffer) / len(smooth_buffer)
    avg_y = sum(p[1] for p in smooth_buffer) / len(smooth_buffer)
    return avg_x, avg_y


def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    print("Simon Says - Hand Tracking Mouse Controller")
    print("===========================================")
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
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks on frame
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Get index finger tip (landmark 8) and thumb tip (landmark 4)
                    index_tip = hand_landmarks.landmark[8]
                    thumb_tip = hand_landmarks.landmark[4]
                    
                    # Convert normalized coordinates to screen coordinates
                    # Mirror x-coordinate for intuitive control
                    cursor_x = (1 - index_tip.x) * screen_width
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
                        
                        global is_clicking
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
        hands.close()
        print("\nSimon Says stopped.")


if __name__ == "__main__":
    main()
