#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from datetime import datetime

# Store last received time for each topic
last_seen = {}

# Generic callback factory for all topics
def make_callback(topic_name):
    def callback(msg):
        global last_seen
        last_seen[topic_name] = datetime.now().strftime("%H:%M:%S")
        rospy.loginfo(f"[MONITOR] {topic_name}: {msg.data}")
    return callback

def main():
    rospy.init_node('system_monitor_node')

    # Subscribers to ALL main topics
    rospy.Subscriber('/camera_frames', String, make_callback('/camera_frames'))
    rospy.Subscriber('/detected_objects', String, make_callback('/detected_objects'))
    rospy.Subscriber('/object_depth', String, make_callback('/object_depth'))
    rospy.Subscriber('/scene_analysis', String, make_callback('/scene_analysis'))
    rospy.Subscriber('/security_event', String, make_callback('/security_event'))
    rospy.Subscriber('/security_alert', String, make_callback('/security_alert'))

    rospy.loginfo("System Monitor Started")

    rate = rospy.Rate(1)  # 1 Hz status update

    while not rospy.is_shutdown():
        rospy.loginfo("====== SYSTEM STATUS ======")

        topics = [
            '/camera_frames',
            '/detected_objects',
            '/object_depth',
            '/scene_analysis',
            '/security_event',
            '/security_alert'
        ]

        for topic in topics:
            if topic in last_seen:
                rospy.loginfo(f"{topic} ACTIVE | Last seen at {last_seen[topic]}")
            else:
                rospy.loginfo(f"{topic} INACTIVE | No data received yet")

        rospy.loginfo("===========================")
        rate.sleep()

if __name__ == '__main__':
    main()
