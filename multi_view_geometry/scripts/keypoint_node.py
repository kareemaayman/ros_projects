#!/usr/bin/env python3

import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from multi_view_geometry.msg import KeypointArray


class KeypointDetectionNode:

    def __init__(self):

        rospy.init_node('keypoint_node')

        # parameters
        self.max_kp = rospy.get_param('~max_keypoints', 200)

        # bridge
        self.bridge = CvBridge()

        # publisher
        self.pub = rospy.Publisher('/keypoints', KeypointArray, queue_size=10)

        # subscriber
        rospy.Subscriber('/camera_frames', Image, self.callback)

        # ORB detector
        self.orb = cv2.ORB_create(nfeatures=self.max_kp)

        rospy.loginfo("[Keypoint Node] Started")

    def callback(self, msg):

        # convert ROS image → OpenCV
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect keypoints
        keypoints = self.orb.detect(gray, None)

        # prepare lists
        x_list = []
        y_list = []
        size_list = []
        angle_list = []
        response_list = []

        # fill data
        for kp in keypoints:
            x, y = kp.pt

            x_list.append(float(x))
            y_list.append(float(y))
            size_list.append(float(kp.size))
            angle_list.append(float(kp.angle))
            response_list.append(float(kp.response))

        # create message
        out = KeypointArray()
        out.header = msg.header

        out.x = x_list
        out.y = y_list
        out.size = size_list
        out.angle = angle_list
        out.response = response_list
        out.count = len(x_list)

        # publish
        self.pub.publish(out)

        rospy.loginfo("[Keypoints] detected = %d", len(x_list))


if __name__ == "__main__":
    KeypointDetectionNode()
    rospy.spin()
