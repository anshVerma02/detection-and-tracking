# Detection and Tracking System
## Overview
This project involves object detection and tracking using computer vision techniques. The goal is to identify and follow objects in a video stream with high accuracy.

## Components Required
### Hardware
- ESP-32 CAM
- Serial to USB convertor
- 2 Servos(SG90)
- Pan and tilt bracket
- Jumper Wires and batteries
- Step Down (9V to 5V)
Once all components are ready then we cann move on to and connect everything as mentioned on the `block_diagram.pdf`
### Prerequisites
Before running the project, ensure you have connected everything and installed the following:
- VS Code
- Arduino IDE

## Features
- Object Detection: Utilizes advanced algorithms to detect objects in video frames.
- Object Tracking: Continuously tracks the detected objects across frames.
- Real-Time Processing: Processes video input in real-time for live detection and tracking.
## Prerequisites
Before running the project, ensure you have the following installed:
- libraries specified in requirements.txt
  
  And the following ESP-32 CAM Library
  
- WebServer 
- WiFi 
- ESP-32 CAM 
- ESP-32 Servo 

## Installation
- Clone the repository:

`git clone https://github.com/anshVerma02/detection-and-tracking.git`

- Navigate to the project directory:

`cd detection-and-tracking`

- Install the required dependencies:

`pip install -r requirements.txt`

- Usage
  
Run the object detection and tracking script:

`python main.py`

## Contributing
Feel free to contribute by submitting issues or pull requests. Your contributions and feedback are welcome!

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
