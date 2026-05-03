# Visual Navigation System

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

The **Visual Navigation System** is a comprehensive ROS-based vision-based navigation platform for autonomous robots. It combines visual odometry, object detection, depth estimation, and motion analysis to enable robots to navigate autonomously using visual cues. The system supports goal-based navigation with real-time obstacle detection and path planning.

This system is ideal for indoor robotic navigation, exploration, and autonomous mapping in GPS-denied environments.

## ✨ Features <a name="features"></a>

- **Visual Odometry**: Estimates robot motion from camera frames
- **Object Detection**: Identifies obstacles and landmarks
- **Depth Estimation**: Provides 3D environmental awareness
- **Region of Interest Tracking**: Focuses on important scene regions
- **Motion Estimation**: Calculates precise movement vectors
- **Navigation Commands**: Generates control commands for robot motion
- **Goal-Based Navigation**: Supports mission planning and execution
- **Action Management**: Handles navigation actions with feedback
- **Real-time Processing**: Low-latency visual processing for reactive control

## 🏗️ System Architecture <a name="system-architecture"></a>

```
Robot Camera
     ↓
┌──────────────────────────────┐
│   Camera Node                │
│   (Frame Capture)            │
└──────────────────────────────┘
     ↓
     ├─→ Object Detector        ├─→ ROI Node
     │   (Obstacle Detection)    │   (Region Focus)
     └───→ Depth Estimator ─────┘
         (3D Information)
     ↓
┌──────────────────────────────┐
│   Motion Node                │
│   (Visual Odometry)          │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   VO Node                    │
│   (Odometry Refinement)      │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   Navigation Node            │
│   (Path Planning)            │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   Action Node                │
│   (Goal Execution)           │
└──────────────────────────────┘
```

## 🔧 Nodes <a name="nodes"></a>

### Camera Node (`camera_node.py`)
Captures camera frames and publishes them for processing.

**Parameters:**
- `camera_source`: Camera device index
- `frame_rate`: Capture frame rate

**Publishes:** Camera frames and timestamps

---

### Object Detector (`object_detector.py`)
Detects obstacles and landmarks in the environment.

**Subscribes to:** Camera frames
**Publishes:** `ObjectData` messages with detected objects

---

### Depth Estimator (`depth_estimator.py`)
Estimates depth information for 3D scene understanding.

**Subscribes to:** Camera frames
**Publishes:** `DepthData` messages with depth maps

---

### ROI Node (`roi_node.py`)
Extracts and tracks regions of interest in frames.

**Subscribes to:** Camera frames, object detections
**Publishes:** `RoiFeatures` with extracted features

---

### Motion Node (`motion_node.py`)
Estimates robot motion and velocity.

**Subscribes to:** Camera frames, depth data
**Publishes:** `MotionData` with motion estimates

---

### VO Node (`vo_node.py`)
Performs visual odometry refinement and localization.

**Subscribes to:** Motion data, depth information
**Publishes:** Refined odometry and pose estimates

---

### Navigation Node (`navigation_node.py`)
Generates navigation commands and path planning.

**Subscribes to:** Odometry, obstacles, navigation goals
**Publishes:** `NavigationCommand` messages

---

### Action Node (`action_node.py`)
Handles navigation actions and goal execution.

**Provides Actions:**
- `Navigate`: Executes navigation to a goal

**Subscribes to:** Navigation commands
**Functions:** Goal tracking, action feedback

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
git clone <repository-url> visual_nav_system
cd ~/catkin_ws
```

2. **Install dependencies:**

```bash
rosdep install --from-paths src --ignore-src -r -y
pip3 install opencv-python numpy scipy
```

3. **Build the package:**

```bash
catkin build visual_nav_system
# or
catkin_make
```

4. **Source the setup script:**

```bash
source devel/setup.bash
```

## 🎯 Usage <a name="usage"></a>

### Launch the Navigation System

```bash
# Start all nodes
rosrun visual_nav_system camera_node.py &
rosrun visual_nav_system object_detector.py &
rosrun visual_nav_system depth_estimator.py &
rosrun visual_nav_system roi_node.py &
rosrun visual_nav_system motion_node.py &
rosrun visual_nav_system vo_node.py &
rosrun visual_nav_system navigation_node.py &
rosrun visual_nav_system action_node.py
```

### Send a Navigation Goal

```bash
rostopic pub /navigation_goal geometry_msgs/PoseStamped \
  "header:
    seq: 0
    stamp: now
    frame_id: 'map'
  pose:
    position:
      x: 10.0
      y: 5.0
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: 0.0
      w: 1.0"
```

### Check Navigation Status

```bash
rostopic echo /navigation_status
```

### Estimate Motion

```bash
rosservice call /estimate_motion \
  "dx: 0.1 \
   dy: 0.05"
```

## 📨 Messages, Services & Actions <a name="messages-services--actions"></a>

### Messages

#### `ObjectData.msg`
Detected objects in the environment.

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

#### `DepthData.msg`
Depth information extracted from frames.

```
std_msgs/Header header
int32 width
int32 height
float32[] depth_map
float32 min_depth
float32 max_depth
```

---

#### `MotionData.msg`
Estimated motion information.

```
std_msgs/Header header
float32 linear_x
float32 linear_y
float32 linear_z
float32 angular_x
float32 angular_y
float32 angular_z
float32 confidence
```

---

#### `NavigationCommand.msg`
Generated navigation commands.

```
std_msgs/Header header
float32 linear_velocity
float32 angular_velocity
int32 target_x
int32 target_y
bool obstacle_detected
```

---

#### `RoiFeatures.msg`
Features extracted from regions of interest.

```
std_msgs/Header header
int32 roi_count
int32[] roi_x
int32[] roi_y
int32[] roi_width
int32[] roi_height
float32[] feature_scores
```

---

#### `ActionStatus.msg`
Status of navigation actions.

```
std_msgs/Header header
string action_id
string status
float32 progress
geometry_msgs/Point current_position
geometry_msgs/Point goal_position
```

---

#### `CameraMotion.msg`
Camera motion information for ego-motion compensation.

```
std_msgs/Header header
float32[] rotation_matrix
float32[] translation_vector
float32 confidence
```

---

### Services

#### `EstimateMotion.srv`
Estimates motion from feature correspondences.

**Request:**
```
float32 dx
float32 dy
```

**Response:**
```
string movement
float32 confidence
bool valid
```

---

### Actions

#### `Navigate.action`
Handles navigation to goal locations.

**Goal:**
```
geometry_msgs/PoseStamped goal_pose
float32 max_velocity
```

**Result:**
```
bool success
float32 total_distance
float32 total_time
```

**Feedback:**
```
geometry_msgs/PoseStamped current_pose
float32 distance_remaining
float32 estimated_time_remaining
```

---

## ⚙️ Configuration <a name="configuration"></a>

Configuration via ROS parameter server:

```bash
# Camera parameters
rosparam set /camera_frame_rate 30
rosparam set /camera_width 640
rosparam set /camera_height 480

# Navigation parameters
rosparam set /max_linear_velocity 0.5
rosparam set /max_angular_velocity 1.0
rosparam set /goal_tolerance 0.1

# VO parameters
rosparam set /vo_ransac_threshold 2.0
rosparam set /vo_inlier_ratio_threshold 0.5
```

## 🆘 Troubleshooting <a name="troubleshooting"></a>

### Poor Visual Odometry Estimates
- Ensure sufficient scene texture and features
- Check lighting conditions
- Verify camera calibration parameters
- Increase frame rate for better motion resolution

### Navigation not reaching goal
- Check obstacle detection: `rostopic echo /detected_objects`
- Verify goal is reachable and not in collision
- Adjust navigation parameters
- Review path planning algorithm

### High latency in navigation
- Reduce processing frame rate
- Lower image resolution
- Disable unused detection modules
- Check CPU usage: `top`

### Motion estimation inaccuracy
- Improve feature detection quality
- Verify calibration
- Increase RANSAC iterations
- Check for rapid camera motion

## 👥 Contributors <a name="contributors"></a>

- Visual navigation development team

---

**For more information or support, please refer to the ROS documentation or contact the development team.**
