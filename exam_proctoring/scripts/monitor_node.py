#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from exam_proctoring.msg import ObjectData

# Store latest value from each topic
status = {
    "camera"    : "waiting...",
    "face"      : "waiting...",
    "object"    : "waiting...",
    "depth"     : "waiting...",
    "behavior"  : "waiting...",
    "violation" : "waiting...",
    "alert"     : "waiting...",
}

def camera_cb(msg):
    status["camera"] = f"image {msg.width}x{msg.height}"

def face_cb(msg):
    status["face"] = msg.data

def object_cb(msg):
    flags = []
    
    if msg.phone_detected:
        flags.append("📱 Phone")
    if msg.book_detected:
        flags.append("📚 Book")

    if msg.object_detected:
        labels = ", ".join(msg.object_labels)
        status["object"] = f"{labels} | {' '.join(flags)}"
    else:
        status["object"] = "No objects detected"

def depth_cb(msg):
    status["depth"] = msg.data

def behavior_cb(msg):
    status["behavior"] = msg.data

def violation_cb(msg):
    status["violation"] = msg.data

def alert_cb(msg):
    status["alert"] = msg.data

def print_status(event):
    rospy.loginfo("=" * 45)
    rospy.loginfo("       EXAM PROCTORING SYSTEM STATUS")
    rospy.loginfo("=" * 45)
    rospy.loginfo(f"  Camera    : {status['camera']}")
    rospy.loginfo(f"  Face      : {status['face']}")
    rospy.loginfo(f"  Object    : {status['object']}")
    rospy.loginfo(f"  Depth     : {status['depth']}")
    rospy.loginfo(f"  Behavior  : {status['behavior']}")
    rospy.loginfo(f"  Violation : {status['violation']}")
    rospy.loginfo(f"  Alert     : {status['alert']}")
    rospy.loginfo("=" * 45)

def main():
    rospy.init_node('monitor_node', anonymous=False)

    rospy.Subscriber('/camera_frames',   Image, camera_cb)
    rospy.Subscriber('/face_data',       String, face_cb)
    rospy.Subscriber('/object_data', ObjectData, object_cb)
    rospy.Subscriber('/depth_data',      String, depth_cb)
    rospy.Subscriber('/behavior_state',  String, behavior_cb)
    rospy.Subscriber('/violation_event', String, violation_cb)
    rospy.Subscriber('/alert_status',    String, alert_cb)

    # Print status every 2 seconds
    rospy.Timer(rospy.Duration(2), print_status)

    rospy.loginfo("[Monitor Node] Ready and running.")
    rospy.spin()

if __name__ == '__main__':
    main()
