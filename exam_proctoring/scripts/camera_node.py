#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraNode:
    def __init__(self):
        rospy.init_node('camera_node')

        # Parameters
        self.source = rospy.get_param('~camera_source', 1)
        self.frame_rate = rospy.get_param('~frame_rate', 10)

        # Video Capture
        self.cap = cv2.VideoCapture(self.source)

        # Publisher
        self.pub = rospy.Publisher('/camera_frames', Image, queue_size=10)

        self.bridge = CvBridge()

        self.rate = rospy.Rate(self.frame_rate)

        rospy.loginfo("Camera Node Started ✅")

    def run(self):
        while not rospy.is_shutdown():
            ret, frame = self.cap.read()

            if not ret:
                rospy.logwarn("⚠️ Failed to read frame")
                continue

            msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            self.pub.publish(msg)

            self.rate.sleep()

if __name__ == '__main__':
    node = CameraNode()
    node.run()
