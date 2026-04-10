#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from std_srvs.srv import Trigger
from grid_fleet.srv import RequestMove
import time

class VehicleNode:

    def __init__(self, vehicle_name):
        # Initialize ROS node with a unique name
        rospy.init_node(vehicle_name)

        # Store vehicle name
        self.name = vehicle_name

        # Vehicle position
        self.x = 0
        self.y = 0

        # Task info
        self.pickup_x = None
        self.pickup_y = None
        self.dropoff_x = None
        self.dropoff_y = None

        # Initial state
        self.state = "IDLE"

        # Publishers
        self.position_pub = rospy.Publisher(
            f'/{self.name}/position', String, queue_size=10)
        self.state_pub = rospy.Publisher(
            f'/{self.name}/state', String, queue_size=10)

        # Wait for the task service
        rospy.wait_for_service('/request_task')
        self.task_service = rospy.ServiceProxy('/request_task', Trigger)

        # Wait for the move service
        rospy.wait_for_service('/request_move')
        self.move_service = rospy.ServiceProxy('/request_move', RequestMove)

        rospy.loginfo(f"{self.name} started")

    # Publish position and state
    def publish_status(self):
        pos_msg = f"{self.name} {self.x} {self.y}"
        state_msg = f"{self.name} {self.state}"
        self.position_pub.publish(pos_msg)
        self.state_pub.publish(state_msg)

    # Request a new task
    def request_task(self):
        try:
            response = self.task_service()
            if response.success:
                rospy.loginfo(f"{self.name} received task: {response.message}")
                # Parse pickup and dropoff coordinates
                parts = response.message.split()
                self.pickup_x = int(parts[0])
                self.pickup_y = int(parts[1])
                self.dropoff_x = int(parts[2])
                self.dropoff_y = int(parts[3])
                # Start moving to pickup
                self.state = "MOVING_TO_PICKUP"
            else:
                rospy.loginfo(f"{self.name}: No more tasks")
        except rospy.ServiceException as e:
            rospy.loginfo(f"Task request failed: {e}")

    # Move one step toward target
    # Move one step toward target (only one cell per move)
    def move_step(self, target_x, target_y):

        # Start with current position
        next_x = self.x
        next_y = self.y

        # Move only ONE axis per step (no diagonal movement)

        # First resolve X movement
        if self.x < target_x:
            next_x = self.x + 1      # Move RIGHT
        elif self.x > target_x:
            next_x = self.x - 1      # Move LEFT

        # If X is already correct, move in Y direction
        elif self.y < target_y:
            next_y = self.y + 1      # Move UP
        elif self.y > target_y:
            next_y = self.y - 1      # Move DOWN

        # Ask Traffic Controller for permission before moving
        try:
            response = self.move_service(
                vehicle_id=self.name,
                current_x=self.x,
                current_y=self.y,
                target_x=next_x,
                target_y=next_y
            )

            # If approved → perform the move
            if response.approved:
                self.x = next_x
                self.y = next_y
                rospy.loginfo(f"{self.name} moved to ({self.x},{self.y})")

            # If not approved → wait
            else:
                self.state = "WAITING"
                rospy.loginfo(f"{self.name} waiting: {response.reason}")

        except rospy.ServiceException as e:
            rospy.logwarn(f"Move request failed: {e}")

        # Check if target reached
        return self.x == target_x and self.y == target_y

    # Main loop
    def run(self):
        rate = rospy.Rate(1)  # 1 Hz
        while not rospy.is_shutdown():
            # Request task if idle
            if self.state == "IDLE":
                self.state = "REQUEST_TASK"
                self.request_task()

            # Move to pickup
            elif self.state == "MOVING_TO_PICKUP":
                arrived = self.move_step(self.pickup_x, self.pickup_y)
                if arrived:
                    self.state = "MOVING_TO_DROPOFF"
                    rospy.loginfo(f"{self.name} reached pickup at ({self.pickup_x},{self.pickup_y})")

            # Move to dropoff
            elif self.state == "MOVING_TO_DROPOFF":
                arrived = self.move_step(self.dropoff_x, self.dropoff_y)
                if arrived:
                    self.state = "FINISHED"
                    rospy.loginfo(f"{self.name} reached dropoff at ({self.dropoff_x},{self.dropoff_y})")

            # Finished task, request new one
            elif self.state == "FINISHED":
                self.state = "IDLE"
                rospy.sleep(1)  # optional pause before requesting new task

            # Vehicle is waiting for clearance from Traffic Controller
            elif self.state == "WAITING":
                rospy.loginfo(f"{self.name} is waiting for clearance...")
                rospy.sleep(1)
                # Retry the move — go back to the correct moving state
                if self.pickup_x is not None:
                    if self.x == self.pickup_x and self.y == self.pickup_y:
                        self.state = "MOVING_TO_DROPOFF"
                    else:
                        self.state = "MOVING_TO_PICKUP"

            # Publish status every loop
            self.publish_status()
            rate.sleep()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: vehicle_node.py <vehicle_name>")
        sys.exit(1)

    vehicle_name = sys.argv[1]
    vehicle = VehicleNode(vehicle_name)
    vehicle.run()
