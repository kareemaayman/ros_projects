# Exam Proctoring System

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![ROS](https://img.shields.io/badge/ROS-Noetic-blue)]()
[![Python](https://img.shields.io/badge/Python-3.8+-green)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

## 📝 Table of Contents

- [About](#about)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Nodes](#nodes)
- [Getting Started](#getting_started)
- [Installation](#installation)
- [Usage](#usage)
- [Messages, Services & Actions](#messages-services--actions)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributors](#contributors)

## 🧐 About <a name="about"></a>

The **Exam Proctoring System** is a ROS-based automated surveillance and behavior monitoring system designed for exam environments. It uses computer vision to monitor exam rooms, detect suspicious behaviors and unauthorized objects, and trigger alerts when violations occur.

The system integrates multiple computer vision components including face detection, object detection, depth estimation, and behavior analysis to create a comprehensive proctoring solution that can operate in real-time.

## ✨ Features <a name="features"></a>

- **Real-time Camera Monitoring**: Continuous video feed processing from camera sources
- **Face Detection & Recognition**: Identifies and tracks student faces during exams
- **Object Detection**: Detects unauthorized objects (phones, books, etc.) in the exam environment
- **Depth Estimation**: Provides 3D spatial information for enhanced scene understanding
- **Behavior Analysis**: Analyzes student behavior patterns to detect suspicious activities
- **Rule Engine**: Flexible rule-based violation detection system
- **Alert System**: Generates alerts with configurable severity levels
- **Real-time Visualization**: Combined viewer for multi-stream monitoring
- **System Monitoring**: Tracks system health and resource usage

## 🏗️ System Architecture <a name="system-architecture"></a>

```
Camera Source
     ↓
┌─────────────────────────────────────┐
│    Camera Node                       │
│    (Video Capture & Preprocessing)   │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  Face Node    │ Object Node         │
│  (Detection)  │ (Detection)         │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│    Depth Node                        │
│    (3D Information)                  │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│    Behavior Node                     │
│    (Pattern Analysis)                │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│    Rule Node                         │
│    (Violation Detection)             │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│    Alert Node                        │
│    (Alert Generation)                │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│    Monitor Node                      │
│    (System Monitoring & Logging)     │
└─────────────────────────────────────┘
```

## 🔧 Nodes <a name="nodes"></a>

### Camera Node (`camera_node.py`)
Captures video from the specified camera source and publishes frames for processing.

**Parameters:**
- `camera_source`: Camera device index (default: 0)
- `frame_rate`: FPS for capturing frames (default: 10)

**Publishes:** Camera frames for downstream processing

---

### Face Node (`face_node.py`)
Detects and tracks faces in the exam environment using computer vision techniques.

**Subscribes to:** Camera frames
**Publishes:** Face detection results

---

### Object Detection Node (`object_detection_node.py`)
Detects unauthorized objects in the exam room using pre-trained models.

**Subscribes to:** Camera frames
**Publishes:** `ObjectData` messages with detected objects

---

### Depth Node (`depth_node.py`)
Estimates depth information from camera frames to provide 3D spatial awareness.

**Subscribes to:** Camera frames
**Publishes:** Depth map information

---

### Behavior Node (`behavior_node.py`)
Analyzes student behavior patterns from detections to identify suspicious activities.

**Subscribes to:** Face and object detection results
**Publishes:** Behavior analysis results

---

### Rule Node (`rule_node.py`)
Implements a rule engine to detect violations based on combined data from all sensors.

**Subscribes to:** Behavior analysis, detections, and depth information
**Publishes:** Violation detection results

---

### Alert Node (`alert_node.py`)
Generates alerts when violations are detected with configurable severity levels.

**Parameters:**
- `alert_level`: Alert severity (default: HIGH)

**Services:** `CheckViolation` service
**Actions:** `Alert` action for alert generation
**Publishes:** Alert notifications

---

### Monitor Node (`monitor_node.py`)
Monitors system health, logs events, and maintains statistics.

**Subscribes to:** All system topics
**Functions:** Event logging, performance monitoring, statistics collection

---

### Combined Viewer Node (`combined_viewer_node.py`)
Provides real-time visualization of multiple data streams.

**Subscribes to:** All detection and analysis results
**Functions:** Unified visualization interface

---

## 🏁 Getting Started <a name="getting_started"></a>

### Prerequisites

- ROS Noetic or later
- Python 3.8+
- OpenCV (cv2)
- NumPy
- Catkin workspace setup

### Installation <a name="installation"></a>

1. **Clone the package into your catkin workspace:**

```bash
cd ~/catkin_ws/src
git clone https://github.com/kareemaayman/ros_projects.git exam_proctoring
cd ~/catkin_ws
```

2. **Install dependencies:**

```bash
rosdep install --from-paths src --ignore-src -r -y
```

3. **Build the package:**

```bash
catkin build exam_proctoring
# or
catkin_make
```

4. **Source the setup script:**

```bash
source devel/setup.bash
```

## 🎯 Usage <a name="usage"></a>

### Launch the Full System

To start the complete exam proctoring system:

```bash
roslaunch exam_proctoring full_system.launch
```

This will start all nodes including:
- Camera capture
- Face detection
- Object detection
- Depth estimation
- Behavior analysis
- Rule engine
- Alert system
- System monitor
- Real-time visualization

### Run Individual Nodes

You can also run specific nodes individually:

```bash
# Camera node only
rosrun exam_proctoring camera_node.py

# Face detection
rosrun exam_proctoring face_node.py

# Object detection
rosrun exam_proctoring object_detection_node.py

# Viewer
rosrun exam_proctoring combined_viewer_node.py
```

## 📨 Messages, Services & Actions <a name="messages-services--actions"></a>

### Messages

#### `ObjectData.msg`
Represents detected objects in the exam environment.

```
std_msgs/Header header
bool object_detected
string[] object_labels
float32[] confidences
int32[] bbox_x
int32[] bbox_y
int32[] bbox_w
int32[] bbox_h
bool phone_detected
bool book_detected
```

---

### Services

#### `CheckViolation.srv`
Checks if a specific behavior constitutes a violation.

**Request:**
```
string behavior
```

**Response:**
```
bool violation_detected
string violation_type
int32 severity
```

---

### Actions

#### `Alert.action`
Handles alert generation and tracking with status updates.

**Goal:**
```
string violation_type
int32 severity
```

**Result:**
```
bool success
string message
```

**Feedback:**
```
string status
```

---

## ⚙️ Configuration <a name="configuration"></a>

Configuration parameters can be set in the launch file or via ROS parameter server:

```bash
# Set camera source
rosparam set /camera_node/camera_source 0

# Set frame rate
rosparam set /camera_node/frame_rate 10

# Set alert level
rosparam set /alert_node/alert_level HIGH
```

## 🆘 Troubleshooting <a name="troubleshooting"></a>

### No video input detected
- Verify camera is properly connected: `ls /dev/video*`
- Check camera permissions: `sudo usermod -a -G video $USER`
- Try different camera source index in parameters

### Nodes not starting
- Ensure ROS core is running: `roscore`
- Check for missing dependencies: `rosdep check exam_proctoring`
- View node logs: `rosnode info <node_name>`

### High CPU usage
- Reduce frame rate in camera_node parameters
- Disable unused nodes in launch file
- Check system resources: `top`, `nvidia-smi` (for GPU)

### No detections
- Verify lighting conditions in exam environment
- Adjust detection thresholds in respective nodes
- Check model files are properly loaded

## 👥 Contributors <a name="contributors"></a>

- Kareema Ayman
- Bassant Mohammed
- Mariam Saafan
- Yasmeen Ashraf 
- Manar Mahmoud

---

**For more information or support, please refer to the ROS documentation or contact the development team.**
