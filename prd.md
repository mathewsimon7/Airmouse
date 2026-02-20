# PRD: Simon Says (Local Python Edition)

**Core Technology:** Google MediaPipe (Hands)  
**Implementation:** Single-process Local Python Script  
**Vision:** A contactless interface that turns a standard webcam into a high-precision mouse replacement.

---

## 1. Problem Statement
Users in sterile (medical), messy (kitchen), or ergonomic-sensitive (RSI) environments need a way to control their computer without touching hardware. Current solutions require specialized depth cameras or heavy web-frameworks. 

**Simon Says** solves this by providing a lightweight, local-only Python script that maps hand landmarks to OS cursor events in real-time.

---

## 2. User Personas
1. **The Kitchen Scholar:** Needs to scroll recipes while hands are covered in flour.
2. **The Ergonomic Specialist:** Needs to reduce wrist strain by switching between traditional mouse and "air-cursor" movement.

---

## 3. SMART Success Metrics
* **Latency:** < 40ms from hand move to cursor update.
* **Accuracy:** 95% "Pinch-to-Click" success rate in standard room lighting (300 lux).
* **Efficiency:** < 10% CPU usage on modern quad-core processors.

---

## 4. Feature Requirements (P0)
* **Real-time Tracking:** Map MediaPipe Landmark 8 (Index Tip) to screen coordinates.
* **Click Logic:** Calculate Euclidean distance between Landmark 8 and Landmark 4 (Thumb) to trigger `pyautogui.click()`.
* **Selfie View:** Display a local OpenCV window with landmark overlays for user feedback.



---

## 5. User Scenarios & Edge Cases
* **Scenario:** User moves hand out of camera view. 
  * **Result:** System freezes cursor at last known coordinate until hand reappears.
* **Edge Case:** Hand "flicker" due to motion blur.
  * **Mitigation:** Use a 3-frame moving average for coordinate smoothing.

---

## 6. Out of Scope
* Multi-hand support (controlling two cursors).
* Browser-based interface (strictly local execution).
* Cloud-based hand processing.