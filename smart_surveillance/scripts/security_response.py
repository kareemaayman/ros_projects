#!/usr/bin/env python3

import rospy
import actionlib
from std_msgs.msg import String
from surveillance_system.msg import SecurityActionAction, SecurityActionFeedback, SecurityActionResult, SecurityActionGoal

# Global variables accessible by all functions
pub_alert = None       # publisher for /security_alert topic
alert_level = 1        # default alert level, configurable via ROS parameter
action_server = None   # ROS action server instance

def execute_cb(goal):
    # This function runs every time a new action goal is received
    # It simulates a long-running security response (like sounding an alarm)
    rospy.loginfo(f"Security action triggered! Event: {goal.event_type}, Level: {goal.alert_level}")

    # Feedback is sent back to the client while the action is running
    feedback = SecurityActionFeedback()

    # Result is sent back to the client when the action finishes
    result = SecurityActionResult()

    # Simulate a 10 second security response
    duration = 10
    rate = rospy.Rate(1)  # 1 Hz = once per second

    for i in range(duration):
        # Check if someone requested to cancel the action
        if action_server.is_preempt_requested():
            rospy.loginfo("Security action preempted!")
            action_server.set_preempted()
            return

        # Send progress feedback every second
        feedback.status = f"Response active for event: {goal.event_type}"
        feedback.elapsed_seconds = i + 1
        action_server.publish_feedback(feedback)
        rospy.loginfo(f"Action running... {i+1}/{duration}s")
        rate.sleep()

    # Action finished successfully — send result
    result.success = True
    result.message = f"Security response completed for: {goal.event_type}"
    action_server.set_succeeded(result)
    rospy.loginfo("Security action completed!")

def event_callback(msg):
    # This function runs every time a message arrives on /security_event
    # It publishes an alert and triggers the long-running action
    global alert_level
    rospy.loginfo(f"Security event received: {msg.data}")

    # Publish an alert message to /security_alert topic
    # This is read by the Event Logger and System Monitor nodes
    alert_msg = String()
    alert_msg.data = f"ALERT level {alert_level}: {msg.data}"
    pub_alert.publish(alert_msg)
    rospy.loginfo(f"Alert published: {alert_msg.data}")

    # Create an action client to send a goal to the action server
    # The action server is in this same node (self-contained)
    client = actionlib.SimpleActionClient('/security_action', SecurityActionAction)

    # Wait up to 2 seconds for the action server to be ready
    client.wait_for_server(timeout=rospy.Duration(2.0))

    # Build the goal — what type of event and what alert level
    goal = SecurityActionGoal()
    goal.event_type = msg.data
    goal.alert_level = alert_level

    # Send the goal — this triggers execute_cb to run
    client.send_goal(goal)
    rospy.loginfo("Security action goal sent!")

def main():
    global pub_alert, alert_level, action_server

    # Initialize the ROS node
    rospy.init_node('security_response_node')

    # Read alert_level from ROS parameter server
    # Can be changed at launch: rosrun ... _alert_level:=2
    alert_level = rospy.get_param('~alert_level', 1)
    rospy.loginfo(f"Alert level set to: {alert_level}")

    # Publisher — sends alerts to /security_alert
    pub_alert = rospy.Publisher('/security_alert', String, queue_size=10)

    # Subscriber — listens for security events from Event Manager node
    rospy.Subscriber('/security_event', String, event_callback)

    # Create the action server — listens for goals on /security_action
    # execute_cb is called every time a new goal arrives
    # auto_start=False means we start it manually below
    action_server = actionlib.SimpleActionServer(
        '/security_action',
        SecurityActionAction,
        execute_cb=execute_cb,
        auto_start=False
    )
    action_server.start()

    rospy.loginfo("Security response node ready!")

    # Keep the node alive and waiting for messages
    rospy.spin()

if __name__ == '__main__':
    main()