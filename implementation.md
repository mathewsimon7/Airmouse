# IMPLEMENTATION_PLAN.md: Simon Says (Local Python)

**Project:** Simon Says  
**Tech Stack:** Python 3.11, MediaPipe, OpenCV, PyAutoGUI  
**Architecture:** Purely Local Single-Process Execution  
**Timeline:** 12 Days  

---

## Phase 1: Environment & Camera Foundation
**Duration:** 2 Days  
**Goal:** Establish a stable local Python environment and verify raw camera input.

### Step 1.1: Virtual Environment Setup
1. Create a project directory and an isolated virtual environment to prevent dependency conflicts.
2. Install core libraries using exact version pinning.
```bash
mkdir simon-says && cd simon-says
python -m venv venv

# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate

pip install mediapipe==0.10.13 opencv-python==4.9.0.80 pyautogui==0.9.54