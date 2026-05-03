# ROS Projects Collection

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![ROS](https://img.shields.io/badge/ROS-Noetic-blue)]()
[![Python](https://img.shields.io/badge/Python-3.8+-green)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

## 📝 Overview

A comprehensive collection of ROS Noetic packages for autonomous systems, surveillance, and intelligent robotics. Each package is independently functional and can be used together for complex robotic applications.

| Package | Description | Documentation |
|---------|-------------|-----------------|
| **Exam Proctoring** | Automated surveillance and behavior monitoring for exam environments | [📖 README](exam_proctoring/README.md) |
| **Grid Fleet** | Multi-vehicle coordination and task management on grid-based environments | [📖 README](grid_fleet/README.md) |
| **Multi-View Geometry** | 3D scene understanding from multiple camera viewpoints | [📖 README](multi_view_geometry/README.md) |
| **Smart Surveillance** | Intelligent security monitoring with threat detection and automated response | [📖 README](smart_surveillance/README.md) |
| **Visual Navigation** | Vision-based autonomous robot navigation and localization | [📖 README](visual_nav_system/README.md) |

## 🚀 Quick Setup

### Prerequisites
- **ROS Noetic** or later
- **Python 3.8+**
- **Ubuntu 20.04 LTS** (recommended)

### Installation

```bash
# Create catkin workspace
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src

# Clone repository
git clone https://github.com/kareemaayman/ros_projects.git

# Install dependencies
cd ~/catkin_ws
rosdep install --from-paths src --ignore-src -r -y
pip3 install opencv-python numpy scipy

# Build all packages
catkin build

# Source setup
source devel/setup.bash
```

## 📦 Packages at a Glance

| Package | Nodes | Nodes | Primary Focus |
|---------|-------|-------|--------------|
| **Exam Proctoring** | 9 | camera, face, object-detection, behavior, alerting | Education |
| **Grid Fleet** | 4 | task-manager, traffic-controller, vehicle, monitor | Logistics |
| **Multi-View Geometry** | 8 | keypoint, descriptor, matching, geometry, motion, filtering | 3D Analysis |
| **Smart Surveillance** | 8 | camera-stream, detector, depth, scene-analysis, response | Security |
| **Visual Navigation** | 8 | camera, detector, depth, motion, VO, navigation | Robotics |

## 💡 Integration Patterns

- **Exam + Surveillance**: Enhanced monitoring with threat detection
- **Fleet + Navigation**: Autonomous robots with visual guidance
- **Multi-View + Navigation**: SLAM and 3D-aware exploration
- **All Packages**: Complete intelligent facility management

## 👥 Contributors

- Kareema Ayman
- Bassant Mohammed
- Mariam Saafan
- Yasmeen Ashraf
- Manar Mahmoud

---

**See individual package READMEs for detailed documentation, node descriptions, API references, and troubleshooting guides.**
