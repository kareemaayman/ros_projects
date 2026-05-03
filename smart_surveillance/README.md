# Smart Surveillance System

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

The **Smart Surveillance System** is an intelligent ROS-based security monitoring platform that provides comprehensive scene analysis and threat detection. It combines computer vision techniques for object detection, depth estimation, and scene analysis to create an intelligent security ecosystem that can identify threats, analyze scenes, log events, and trigger appropriate security responses.

The system is designed for real-time deployment in security-critical environments requiring continuous monitoring and rapid response capabilities.

## ✨ Features <a name="features"></a>

- **Real-time Object Detection**: Identifies objects and threats in monitored areas
- **Depth Estimation**: Provides 3D spatial information for accurate threat assessment
- **Scene Analysis**: Analyzes overall scene composition and detects anomalies
- **Security Event Detection**: Identifies suspicious activities and events
- **Alert Management**: Generates and manages security alerts with severity levels
- **Event Logging**: Records all security events with timestamps and details
- **Automated Response**: Triggers appropriate responses based on threat level
- **System Monitoring**: Tracks camera health and system performance
- **Multi-Camera Support**: Manages multiple surveillance cameras

## 🏗️ System Architecture <a name="system-architecture"></a>

```
Security Cameras
     ↓
┌──────────────────────────────┐
│   Camera Stream              │
│   (Video Capture)            │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   Object Detector            │
│   (Threat Detection)         │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   Depth Estimator            │
│   (3D Information)           │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   Scene Analysis             │
│   (Context Understanding)    │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   Event Manager              │
│   (Event Generation)         │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   Event Logger               │
│   (Record Keeping)           │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   Security Response          │
│   (Alert & Action)           │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   System Monitor             │
│   (Health & Statistics)      │
└──────────────────────────────┘
```

## 🔧 Nodes <a name="nodes"></a>

### Camera Stream (`camera_stream.py`)
Captures video streams from security cameras and publishes frames for analysis.

**Parameters:**
- `camera_id`: Identifier for camera source
- `frame_rate`: Frames per second for capture

**Publishes:** Video frames and metadata

---

### Object Detector (`object_detector.py`)
Detects objects and potential threats in video frames using deep learning models.

**Subscribes to:** Camera frames
**Publishes:** `DetectedObject` messages with detection results

---

### Depth Estimator (`depth_estimator.py`)
Estimates depth information to provide 3D understanding of threats.

**Subscribes to:** Camera frames
**Publishes:** Depth maps and 3D coordinates

---

### Scene Analysis (`scene_analysis.py`)
Analyzes the overall scene to detect anomalies and suspicious patterns.

**Subscribes to:** Object detections, depth information
**Publishes:** `SceneAnalysis` messages with analysis results

---

### Event Manager (`event_manager.py`)
Generates security events based on detection and analysis results.

**Subscribes to:** Scene analysis, object detections
**Publishes:** `SecurityEvent` messages

---

### Event Logger (`event_logger.py`)
Records all security events in persistent storage for auditing and review.

**Subscribes to:** Security events
**Functions:** Event logging, database storage, audit trail

---

### Security Response (`security_response.py`)
Triggers appropriate security responses based on threat assessment.

**Provides Actions:**
- `SecurityAction`: Executes security responses

**Subscribes to:** Security events
**Publishes:** Alert notifications and commands

---

### System Monitor (`system_monitor.py`)
Monitors overall system health and performance metrics.

**Subscribes to:** All system topics
**Functions:** Performance tracking, health checks, statistics

---

## 🏁 Getting Started <a name="getting_started"></a>

### Prerequisites

- ROS Noetic or later
- Python 3.8+
- OpenCV (cv2)
- NumPy
- TensorFlow or PyTorch (for object detection models)
- Catkin workspace setup

### Installation <a name="installation"></a>

1. **Clone the package into your catkin workspace:**

```bash
cd ~/catkin_ws/src
git clone <repository-url> smart_surveillance
cd ~/catkin_ws
```

2. **Install dependencies:**

```bash
rosdep install --from-paths src --ignore-src -r -y
pip3 install opencv-python numpy tensorflow
```

3. **Build the package:**

```bash
catkin build smart_surveillance
# or
catkin_make
```

4. **Source the setup script:**

```bash
source devel/setup.bash
```

## 🎯 Usage <a name="usage"></a>

### Launch the Surveillance System

```bash
# Start all nodes
rosrun smart_surveillance camera_stream.py &
rosrun smart_surveillance object_detector.py &
rosrun smart_surveillance depth_estimator.py &
rosrun smart_surveillance scene_analysis.py &
rosrun smart_surveillance event_manager.py &
rosrun smart_surveillance event_logger.py &
rosrun smart_surveillance security_response.py &
rosrun smart_surveillance system_monitor.py
```

### View Detected Objects

```bash
rostopic echo /detected_objects
```

### Check System Status

```bash
rostopic echo /system_status
```

### View Security Events

```bash
rostopic echo /security_events
```

### Trigger Security Response

```bash
rosservice call /security_response \
  "event_type: 'intruder' \
   alert_level: 5"
```

## 📨 Messages, Services & Actions <a name="messages-services--actions"></a>

### Messages

#### `DetectedObject.msg`
Represents a detected object or threat in the scene.

```
string label
float32 confidence
int32 x
int32 y
int32 width
int32 height
```

---

#### `SceneAnalysis.msg`
Contains analysis results for the monitored scene.

```
std_msgs/Header header
string scene_status
int32 threat_level
int32 object_count
string[] detected_categories
float32[] anomaly_scores
```

---

#### `SecurityEvent.msg`
Represents a security-relevant event.

```
std_msgs/Header header
string event_type
int32 severity
string description
geometry_msgs/Point location
```

---

#### `SecurityAlert.msg`
Alert message for security threats.

```
std_msgs/Header header
int32 alert_level
string alert_type
string message
bool requires_response
```

---

### Actions

#### `SecurityAction.action`
Handles security responses with status tracking.

**Goal:**
```
string event_type
int32 alert_level
```

**Result:**
```
bool success
string message
```

**Feedback:**
```
string status
int32 elapsed_seconds
```

---

## ⚙️ Configuration <a name="configuration"></a>

Configuration via ROS parameter server:

```bash
# Camera configuration
rosparam set /camera_frame_rate 30
rosparam set /camera_resolution 1080p

# Detection thresholds
rosparam set /object_confidence_threshold 0.5
rosparam set /threat_threshold 0.7

# Alert configuration
rosparam set /alert_level_high 5
rosparam set /alert_level_medium 3
rosparam set /alert_level_low 1
```

## 🆘 Troubleshooting <a name="troubleshooting"></a>

### No detections reported
- Verify object detector model is loaded: `rosnode info /object_detector`
- Check camera feed: `rostopic echo /camera_stream`
- Adjust confidence threshold: `rosparam set /object_confidence_threshold 0.3`
- Verify lighting conditions

### False positives
- Increase confidence threshold: `rosparam set /object_confidence_threshold 0.7`
- Retrain detection model with more diverse data
- Implement filtering in event_manager.py

### High latency
- Reduce frame resolution
- Lower processing frame rate
- Disable unused analysis modules
- Check system resources: `top`

### Event logging failures
- Verify database connectivity
- Check disk space for logs
- Confirm write permissions to log directory
- Review event_logger.py error messages

## 👥 Contributors <a name="contributors"></a>

- Smart surveillance development team

---

**For more information or support, please refer to the ROS documentation or contact the development team.**
