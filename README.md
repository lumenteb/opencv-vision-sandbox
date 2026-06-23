OpenCV Vision Sandbox

Small computer vision experiments with Python and OpenCV.

This repository contains my early experiments with webcam-based computer vision: color detection, object tracking, movement visualization, and simple interaction using live camera input.

Current Project: Red Object Tracker

The current script detects a red object through the webcam, finds its center, and tracks its movement on screen.

The goal of this project is to understand the basic computer vision pipeline:

Capture video from a webcam
Convert the image from BGR to HSV color space
Create a mask for red color detection
Find contours of detected objects
Calculate the center of the object
Track its movement between frames
Draw visual feedback on the screen
Features
Webcam input using OpenCV
Red color detection with HSV masks
Contour detection
Object center calculation
Basic object tracking
Movement visualization
Real-time video processing
Tech Stack
Python
OpenCV
NumPy
Project Structure
opencv-vision-sandbox/
│
├── red_object_tracker.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
Installation

Clone the repository:

git clone https://github.com/lumenteb/opencv-vision-sandbox.git

Go into the project folder:

cd opencv-vision-sandbox

Install dependencies:

pip install -r requirements.txt
Run

Run the tracker:

python red_object_tracker.py

A webcam window should open. Show a red object in front of the camera, and the program should detect and track it.

Requirements

The project uses:

opencv-python
numpy

These dependencies are listed in requirements.txt.
