# TECH_STACK.md: Simon Says

## 1. Core Languages & Runtime
* **Language:** Python 3.11.9
* **Runtime:** Local System Interpreter (Direct Execution)

## 2. Primary Libraries (Exact Versions)
| Library | Version | Purpose |
| :--- | :--- | :--- |
| `mediapipe` | 0.10.13 | Hand landmark detection (21 points) |
| `opencv-python` | 4.9.0.80 | Camera frame capture and UI preview |
| `pyautogui` | 0.9.54 | OS-level mouse movement and click injection |

## 3. System Architecture
1. **Input:** OpenCV `VideoCapture(0)` pulls raw BGR frames.
2. **Process:** MediaPipe Hands converts frames to RGB and extracts 3D coordinates.
3. **Control:** PyAutoGUI maps normalized $x,y$ to `screen_width` and `screen_height`.



## 4. Hardware Requirements
* **Camera:** Standard 720p Integrated or USB Webcam.
* **RAM:** Minimum 2GB available.
* **CPU:** Quad-core 2.0GHz or higher.