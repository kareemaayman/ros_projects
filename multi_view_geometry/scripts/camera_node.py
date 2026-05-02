#!/usr/bin/env python3

import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class CameraStreamNode:
    def __init__(self):
        rospy.init_node('camera_stream_node')

        # Parameters
        self.camera_source = rospy.get_param('~camera_source', '/home/ka/Videos/sample.mp4')  # 0 = webcam
        self.frame_rate = rospy.get_param('~frame_rate', 10)

        # Publisher
        self.pub = rospy.Publisher('/camera_frames', Image, queue_size=10)

        # OpenCV + Bridge
        self.cap = cv2.VideoCapture(self.camera_source)
        self.bridge = CvBridge()

        self.rate = rospy.Rate(self.frame_rate)

        if not self.cap.isOpened():
            rospy.logerr("Failed to open camera source")
            exit()

    def run(self):
        while not rospy.is_shutdown():
            ret, frame = self.cap.read()

            if not ret:
                rospy.logwarn("Failed to capture frame")
                continue

            # Convert to ROS Image
            ros_image = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")

            # Publish
            self.pub.publish(ros_image)

            self.rate.sleep()

        self.cap.release()


if __name__ == '__main__':
    try:
        node = CameraStreamNode()
        node.run()
    except rospy.ROSInterruptException:
        pass
