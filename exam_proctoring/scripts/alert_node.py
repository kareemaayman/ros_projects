#!/usr/bin/env python3
from roscpp import msg
import rospy
from std_msgs.msg import String
import actionlib
from exam_proctoring.msg import AlertAction, AlertFeedback, AlertResult

class AlertNode:
    def __init__(self):
        rospy.init_node('alert_node')

        self.server = actionlib.SimpleActionServer(
            '/alert_action', AlertAction, self.execute_alert, False)
        self.server.start()

        rospy.Subscriber('/violation_event', String, self.callback)
        self.pub = rospy.Publisher('/alert_status', String, queue_size=10)
        rospy.loginfo("Alert Node Started 🚨")
    def get_alert_level(self, violation_msg):
        if "severity_1" in violation_msg:
            return "LOW"
        elif "severity_2" in violation_msg:
            return "MEDIUM"
        elif "severity_3" in violation_msg:
            return "HIGH"
        else:
            return "UNKNOWN"
    def execute_alert(self, goal):
        # Send feedback
        feedback = AlertFeedback()
        feedback.status = f"Processing: {goal.violation_type}"
        self.server.publish_feedback(feedback)

        level = self.get_alert_level(goal.violation_type)

        rospy.loginfo(f"🚨 ACTION ALERT: {goal.violation_type} | Level: {level}")

        alert_msg = String()
        alert_msg.data = f"🚨 ALERT: {goal.violation_type} | Level: {level}"
        self.pub.publish(alert_msg)

        rospy.sleep(0.5)  # simulate processing

        result = AlertResult()
        result.success = True
        result.message = f"Alert sent for {goal.violation_type}"
        self.server.set_succeeded(result)

    def callback(self, msg):
        # This handles no_violation passthrough for the monitor
        if msg.data != "no_violation":
            level = self.get_alert_level(msg.data)
            alert_text = f"🚨 ALERT: {msg.data} | Level: {level}"
            rospy.loginfo(alert_text)
            self.pub.publish(alert_text)

if __name__ == '__main__':
    node = AlertNode()
    rospy.spin()
