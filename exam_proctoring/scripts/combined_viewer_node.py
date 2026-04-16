#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CombinedViewer:
    def __init__(self):
        rospy.init_node("combined_viewer")

        self.bridge = CvBridge()

        rospy.Subscriber("/face_display", Image, self.face_cb)
        rospy.Subscriber("/depth_display", Image, self.depth_cb)

        self.face_img = None
        self.depth_img = None

    def face_cb(self, msg):
        self.face_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def depth_cb(self, msg):
        self.depth_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def run(self):
        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            if self.face_img is not None and self.depth_img is not None:

                face = cv2.resize(self.face_img, (320, 240))
                depth = cv2.resize(self.depth_img, (320, 240))

                combined = cv2.hconcat([face, depth])

                cv2.imshow("Face + Depth", combined)
                cv2.waitKey(1)

            rate.sleep()

if __name__ == "__main__":
    node = CombinedViewer()
    node.run()
