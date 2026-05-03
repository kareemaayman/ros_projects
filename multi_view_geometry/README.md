# Multi-View Geometry Reasoning System

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

The **Multi-View Geometry Reasoning System** is a distributed ROS-based system for analyzing and understanding 3D scenes from multiple camera viewpoints. It processes camera inputs, extracts keypoints and descriptors, performs feature matching, validates geometric constraints, and provides comprehensive scene analysis through epipolar geometry reasoning.

This system is ideal for applications requiring 3D reconstruction, depth estimation, structure-from-motion, and multi-view scene understanding.

## ✨ Features <a name="features"></a>

- **Multi-Camera Input**: Processes frames from multiple camera sources
- **Keypoint Detection**: Extracts distinctive keypoints from images
- **Feature Descriptor Extraction**: Computes descriptor arrays for keypoints
- **Feature Matching**: Matches keypoints across multiple views
- **Epipolar Geometry Validation**: Ensures geometric consistency using epipolar constraints
- **Motion Estimation**: Estimates camera motion between views
- **Filtering & Refinement**: Removes outliers and inconsistent matches
- **Geometric Analysis**: Reports inlier ratios and geometric quality metrics
- **Reporting System**: Generates detailed analysis reports with actions

## 🏗️ System Architecture <a name="system-architecture"></a>

```
Multiple Camera Sources
     ↓
┌────────────────────────────────┐
│   Camera Nodes                  │
│   (Frame Capture)               │
└────────────────────────────────┘
     ↓
┌────────────────────────────────┐
│   Keypoint Node                 │
│   (Feature Detection)           │
└────────────────────────────────┘
     ↓
┌────────────────────────────────┐
│   Descriptor Node               │
│   (Feature Description)         │
└────────────────────────────────┘
     ↓
┌────────────────────────────────┐
│   Matching Node                 │
│   (Feature Correspondence)      │
└────────────────────────────────┘
     ↓
┌────────────────────────────────┐
│   Geometry Node                 │
│   (Epipolar Validation)         │
└────────────────────────────────┘
     ↓
┌────────────────────────────────┐
│   Motion Node                   │
│   (Camera Motion Estimation)    │
└────────────────────────────────┘
     ↓
┌────────────────────────────────┐
│   Filtering Node                │
│   (Outlier Removal)             │
└────────────────────────────────┘
     ↓
┌────────────────────────────────┐
│   Decision Node                 │
│   (Analysis & Reporting)        │
└────────────────────────────────┘
```

## 🔧 Nodes <a name="nodes"></a>

### Camera Node (`camera_node.py`)
Captures frames from camera sources and publishes them for processing.

**Publishes:** Camera frames and timestamps

---

### Keypoint Node (`keypoint_node.py`)
Detects and extracts keypoints from camera frames using feature detection algorithms.

**Subscribes to:** Camera frames
**Publishes:** `KeypointArray` messages with detected keypoints

---

### Descriptor Node (`descriptor_node.py`)
Computes feature descriptors for detected keypoints.

**Subscribes to:** Keypoint arrays
**Publishes:** `DescriptorArray` messages with descriptor vectors

---

### Matching Node (`matching_node.py`)
Matches descriptors across multiple views to find correspondences.

**Subscribes to:** Descriptor arrays from multiple cameras
**Publishes:** `MatchArray` messages with correspondence information

---

### Geometry Node (`geometry_node.py`)
Validates geometric consistency using epipolar geometry constraints.

**Provides Services:**
- `CheckGeometry`: Validates point correspondences

**Subscribes to:** Match arrays
**Publishes:** `GeometricInliers` with validation results

---

### Motion Node (`motion_node.py`)
Estimates camera motion between consecutive frames.

**Subscribes to:** Geometric validation results
**Publishes:** `CameraMotion` messages with motion estimates

---

### Filtering Node (`filtering_node.py`)
Removes outliers and refines the analysis results.

**Subscribes to:** All geometry and motion information
**Publishes:** Filtered and refined results

---

### Decision Node (`decision_node.py`)
Performs high-level analysis and generates reports.

**Provides Actions:**
- `Report`: Generates detailed analysis reports

**Subscribes to:** All system topics
**Functions:** Analysis aggregation, report generation

---

## 🏁 Getting Started <a name="getting_started"></a>

### Prerequisites

- ROS Noetic or later
- Python 3.8+
- OpenCV (cv2)
- NumPy
- SciPy
- Catkin workspace setup

### Installation <a name="installation"></a>

1. **Clone the package into your catkin workspace:**

```bash
cd ~/catkin_ws/src
git clone <repository-url> multi_view_geometry
cd ~/catkin_ws
```

2. **Install dependencies:**

```bash
rosdep install --from-paths src --ignore-src -r -y
pip3 install opencv-python numpy scipy
```

3. **Build the package:**

```bash
catkin build multi_view_geometry
# or
catkin_make
```

4. **Source the setup script:**

```bash
source devel/setup.bash
```

## 🎯 Usage <a name="usage"></a>

### Launch All Nodes

```bash
# Start individual nodes
rosrun multi_view_geometry camera_node.py &
rosrun multi_view_geometry keypoint_node.py &
rosrun multi_view_geometry descriptor_node.py &
rosrun multi_view_geometry matching_node.py &
rosrun multi_view_geometry geometry_node.py &
rosrun multi_view_geometry motion_node.py &
rosrun multi_view_geometry filtering_node.py &
rosrun multi_view_geometry decision_node.py
```

### Check Geometry

```bash
rosservice call /check_geometry \
  "query_x: [100.0, 200.0] \
   query_y: [150.0, 250.0] \
   train_x: [105.0, 205.0] \
   train_y: [155.0, 255.0]"
```

### Generate Report

```bash
rosrun actionlib_client.py action_client.py _action_name:=/generate_report
```

## 📨 Messages, Services & Actions <a name="messages-services--actions"></a>

### Messages

#### `KeypointArray.msg`
Array of detected keypoints with their properties.

```
std_msgs/Header header
int32 keypoint_count
float32[] x
float32[] y
float32[] size
float32[] angle
float32[] response
```

---

#### `DescriptorArray.msg`
Array of feature descriptors corresponding to keypoints.

```
std_msgs/Header header
int32 descriptor_count
int32 descriptor_size
uint8[] descriptors
```

---

#### `MatchArray.msg`
Array of feature matches between two images.

```
std_msgs/Header header
int32[] query_indices
int32[] train_indices
float32[] distances
```

---

#### `CameraMotion.msg`
Estimated camera motion between frames.

```
std_msgs/Header header
float32[] rotation_matrix
float32[] translation_vector
float32 confidence
```

---

#### `GeometricInliers.msg`
Geometric validation results.

```
std_msgs/Header header
int32[] inlier_indices
float32 inlier_ratio
bool is_consistent
```

---

#### `SystemState.msg`
Overall system state and statistics.

```
std_msgs/Header header
int32 active_cameras
int32 total_keypoints
int32 total_matches
float32 average_inlier_ratio
string system_status
```

---

### Services

#### `CheckGeometry.srv`
Validates point correspondences using epipolar geometry.

**Request:**
```
float32[] query_x
float32[] query_y
float32[] train_x
float32[] train_y
```

**Response:**
```
bool is_consistent
int32[] inlier_indices
float32 inlier_ratio
```

---

### Actions

#### `Report.action`
Generates comprehensive analysis reports.

**Goal:**
```
string analysis_type
int32 detail_level
```

**Result:**
```
bool success
string report_file
string summary
```

**Feedback:**
```
string status
float32 progress
```

---

## ⚙️ Configuration <a name="configuration"></a>

Configuration via ROS parameter server:

```bash
# Camera configuration
rosparam set /camera_source 0
rosparam set /frame_rate 30

# Feature detection thresholds
rosparam set /keypoint_threshold 0.01
rosparam set /descriptor_threshold 0.7

# Geometry validation
rosparam set /epipolar_threshold 1.0
rosparam set /inlier_ratio_threshold 0.3
```

## 🆘 Troubleshooting <a name="troubleshooting"></a>

### Low inlier ratio
- Adjust epipolar threshold: `rosparam set /epipolar_threshold 2.0`
- Verify camera calibration
- Check lighting conditions
- Increase feature detection sensitivity

### No matches found
- Check keypoint detection is working: `rostopic echo /keypoints`
- Verify descriptor computation: `rostopic echo /descriptors`
- Adjust matcher parameters in matching_node.py
- Ensure sufficient camera baseline

### High CPU usage
- Reduce frame rate
- Lower keypoint detection density
- Disable unused nodes
- Process lower resolution images

## 👥 Contributors <a name="contributors"></a>

- Kareema Ayman
- Bassant Mohammed
- Mariam Saafan
- Yasmeen Ashraf 
- Manar Mahmoud
---

**For more information or support, please refer to the ROS documentation or contact the development team.**
