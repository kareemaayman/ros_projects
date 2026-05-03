# Grid Fleet Management System

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![ROS](https://img.shields.io/badge/ROS-Noetic-blue)]()
[![Python](https://img.shields.io/badge/Python-3.8+-green)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

## 📝 Table of Contents

- [About](#about)
- [Demo] (#demo)
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

The **Grid Fleet Management System** is a ROS-based fleet management and coordination system designed for autonomous vehicle operations on a grid-based environment. It handles task allocation, route planning, traffic control, and real-time monitoring of multiple vehicles operating in a warehouse or logistics environment.

The system provides centralized coordination for autonomous vehicles, ensuring efficient task execution, collision avoidance, and optimal resource utilization.

## 🎥 Demo <a name="demo"></a>



https://github.com/user-attachments/assets/9d036798-c009-41e6-a0e8-84caadc2207f



## ✨ Features <a name="features"></a>

- **Multi-Vehicle Coordination**: Manages multiple autonomous vehicles simultaneously
- **Task Management**: Dynamic task allocation and scheduling
- **Route Planning**: Optimal path planning for vehicle navigation
- **Movement Approval**: Validates movements and prevents collisions
- **Traffic Control**: Centralized traffic management on grid
- **Real-time Monitoring**: Tracks vehicle status and positions
- **Load Balancing**: Distributes tasks efficiently across fleet
- **Status Reporting**: Detailed vehicle and task status updates

## 🏗️ System Architecture <a name="system-architecture"></a>

```
Task Source / Mission Planner
     ↓
┌──────────────────────────────┐
│   Task Manager               │
│   (Task Allocation)          │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   Traffic Controller         │
│   (Collision Avoidance)      │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   Vehicle Nodes (Multiple)   │
│   (Motion Execution)         │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│   Monitor                    │
│   (System Oversight)         │
└──────────────────────────────┘
```

## 🔧 Nodes <a name="nodes"></a>

### Task Manager (`task_manager.py`)
Handles task creation, allocation, and scheduling for the fleet.

**Provides Services:**
- `RequestTask`: Assigns tasks to available vehicles

**Publishes:** Task status and allocation messages

---

### Traffic Controller (`traffic_controller.py`)
Manages vehicle movements and prevents collisions on the grid.

**Provides Services:**
- `RequestMove`: Validates and approves vehicle movement requests

**Subscribes to:** Vehicle position updates
**Publishes:** Approved movement commands

---

### Vehicle Node (`vehicle_node.py`)
Represents an autonomous vehicle in the fleet.

**Services Used:**
- `RequestMove`: Requests movement approval from traffic controller
- `RequestTask`: Requests task assignment from task manager

**Publishes:** Vehicle position, status, and task progress

---

### Monitor (`monitor.py`)
Monitors fleet health and provides system oversight.

**Subscribes to:** All vehicle and system topics
**Functions:** Fleet monitoring, performance tracking, logging

---

## 🏁 Getting Started <a name="getting_started"></a>

### Prerequisites

- ROS Noetic or later
- Python 3.8+
- NumPy
- Catkin workspace setup

### Installation <a name="installation"></a>

1. **Clone the package into your catkin workspace:**

```bash
cd ~/catkin_ws/src
git clone <repository-url> grid_fleet
cd ~/catkin_ws
```

2. **Install dependencies:**

```bash
rosdep install --from-paths src --ignore-src -r -y
```

3. **Build the package:**

```bash
catkin build grid_fleet
# or
catkin_make
```

4. **Source the setup script:**

```bash
source devel/setup.bash
```

## 🎯 Usage <a name="usage"></a>

### Start the System

```bash
rosrun grid_fleet task_manager.py &
rosrun grid_fleet traffic_controller.py &
rosrun grid_fleet monitor.py &
```

### Run Vehicles

Start one or more vehicle nodes:

```bash
rosrun grid_fleet vehicle_node.py _vehicle_id:=vehicle_1
rosrun grid_fleet vehicle_node.py _vehicle_id:=vehicle_2
rosrun grid_fleet vehicle_node.py _vehicle_id:=vehicle_3
```

### Request a Task

```bash
rosservice call /request_task "vehicle_id: 'vehicle_1'"
```

### Request a Move

```bash
rosservice call /request_move \
  "vehicle_id: 'vehicle_1' \
   current_x: 0 \
   current_y: 0 \
   target_x: 5 \
   target_y: 5"
```

## 📨 Messages, Services & Actions <a name="messages-services--actions"></a>

### Services

#### `RequestMove.srv`
Requests approval for a vehicle to move from one position to another.

**Request:**
```
string vehicle_id
int32 current_x
int32 current_y
int32 target_x
int32 target_y
```

**Response:**
```
bool approved
string reason
```

---

#### `RequestTask.srv`
Requests a new task assignment for a vehicle.

**Request:**
```
string vehicle_id
```

**Response:**
```
bool success
int32 pickup_x
int32 pickup_y
int32 dropoff_x
int32 dropoff_y
int32 task_id
```

---

## ⚙️ Configuration <a name="configuration"></a>

Configuration parameters via ROS parameter server:

```bash
# Set grid dimensions
rosparam set /grid_size 100

# Set traffic controller update rate
rosparam set /traffic_controller/update_rate 10

# Set vehicle speed
rosparam set /vehicle_speed 1.0
```

## 🆘 Troubleshooting <a name="troubleshooting"></a>

### Vehicles not accepting tasks
- Ensure task manager is running: `rosnode list | grep task_manager`
- Check vehicle status: `rostopic echo /vehicle_status`
- Verify network connectivity between nodes

### Movement requests denied
- Check traffic controller is active: `rosnode list | grep traffic_controller`
- Verify target position is valid on grid
- Check for other vehicles blocking the path: `rostopic echo /grid_occupancy`

### Poor task distribution
- Adjust task allocation algorithm in task_manager.py
- Monitor vehicle load: `rostopic echo /vehicle_load`
- Check for stuck vehicles: `rostopic echo /vehicle_position`

## 👥 Contributors <a name="contributors"></a>

- Kareema Ayman
- Bassant Mohammed
- Mariam Saafan
- Yasmeen Ashraf 
- Manar Mahmoud
---

**For more information or support, please refer to the ROS documentation or contact the development team.**
