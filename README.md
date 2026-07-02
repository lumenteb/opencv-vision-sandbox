# Real-Time Red Object Tracker

A webcam-based computer vision application that detects, tracks, and predicts the movement of red objects in real time.

## Overview

This portfolio project demonstrates practical Python automation and computer vision skills. It processes live webcam frames, isolates red pixels in HSV color space, tracks the largest matching object, and overlays diagnostics such as position, direction, speed, trajectory, and tracking state.

The project is intentionally compact: the tracking pipeline is contained in one readable script and uses only OpenCV and NumPy.

## Features

- Real-time webcam capture and processing
- Red-object segmentation using two HSV ranges
- Noise reduction with Gaussian blur and morphological filtering
- Largest-contour selection with a minimum area threshold
- Bounding box and center-point visualization
- Direction and speed estimation
- Short-term position prediction
- Recent movement trajectory
- Smoothed aim indicator and horizontal control guidance
- Tracking states: searching, tracking, holding, and lost
- Live FPS, contour area, and object-status diagnostics

## Tech Stack

- Python 3.10+
- OpenCV
- NumPy

## How It Works

1. OpenCV reads frames from the default webcam.
2. Each frame is blurred and converted from BGR to HSV.
3. Two HSV ranges are combined to cover red at both ends of the hue scale.
4. Morphological opening and closing reduce noise in the binary mask.
5. The largest contour above the area threshold is treated as the target.
6. The program calculates its center, movement, speed, and predicted position.
7. Tracking data and visual guides are drawn on the live video.
8. If detection briefly drops, the tracker holds the last known position before marking the target as lost.

## Example Output

The application opens two windows:

- **Vision Sandbox** — live camera output with the bounding box, trajectory, aim marker, predicted position, and diagnostics
- **Mask** — the binary image used to isolate red pixels

Portfolio screenshots or a short demo GIF can be placed in [`examples/media`](examples/media). See [`examples/README.md`](examples/README.md) for safe capture guidance.

## How to Run

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd red-object-tracker
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start the tracker

```bash
python main.py
```

Hold a red object in view of the default webcam. Press **Q** while an application window is active to exit.

### Troubleshooting

- Confirm that a webcam is connected and not being used by another application.
- Allow camera access when requested by the operating system.
- Use even lighting and a clearly red target for more reliable detection.
- Adjust the HSV limits or `min_area` only when adapting the tracker to a different environment.

## Project Structure

```text
red-object-tracker/
├── examples/
│   ├── media/
│   │   └── .gitkeep
│   └── README.md
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

## What I Learned

- Applying HSV color segmentation to a live camera stream
- Reducing false detections with blur and morphological operations
- Using contours to locate and measure objects
- Estimating motion from changes between video frames
- Designing simple tracking states for temporary detection loss
- Presenting live diagnostic information for testing and debugging
- Keeping a small Python project reproducible and portfolio-ready

From a QA and automation perspective, this project also reinforced the value of observable state, repeatable setup steps, clear failure messages, and testing small calculations separately from hardware-dependent behavior.

## Future Improvements

- Add command-line options for camera index, minimum area, and HSV thresholds
- Add unit tests for calculation and state-transition helpers
- Support recorded video input for repeatable regression testing
- Save optional annotated recordings or screenshots
- Add configurable tracking profiles for other colors
- Compare detection results across different lighting conditions

## Project Status

**Working prototype.** Core real-time detection and tracking features are implemented. A webcam is required for the full interactive demo.
