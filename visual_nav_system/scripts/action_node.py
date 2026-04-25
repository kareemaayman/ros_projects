#!/usr/bin/env python3

import rospy
from visual_nav_system.msg import NavigationCommand, ActionStatus 

class ActionExecutionNode:
    def __init__(self):
        rospy.init_node('action_execution_node')

        # Parameters
        self.action_duration = rospy.get_param('~action_duration', 2.0)

        # Subscriber
        rospy.Subscriber('/navigation_command', NavigationCommand, self.command_callback)

        # Publisher
        self.pub = rospy.Publisher('/action_status', ActionStatus, queue_size=10)

        rospy.loginfo("Action Execution Node Started")

    def command_callback(self, msg):
        command = msg.command.upper()
        duration = msg.duration if msg.duration > 0 else self.action_duration

        if command == "MOVE_LEFT":
            self.execute_action("Moving Left", duration)
        elif command == "MOVE_RIGHT":
            self.execute_action("Moving Right", duration)
        elif command == "MOVE_FORWARD":
            self.execute_action("Moving Forward", duration)
        elif command == "STOP":
            self.execute_action("Stopping", 0)

    def execute_action(self, action_name, duration):
        rospy.loginfo(f"Executing: {action_name} for {duration}s")

        if duration > 0:
            rospy.sleep(duration)

        status_msg = ActionStatus()
        status_msg.status = f"{action_name} Done"
        status_msg.success = True
        self.pub.publish(status_msg)


if __name__ == '__main__':
    try:
        node = ActionExecutionNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
