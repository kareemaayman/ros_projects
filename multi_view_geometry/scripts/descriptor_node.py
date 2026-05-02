#!/usr/bin/env python3

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

from multi_view_geometry.msg import KeypointArray, DescriptorArray


class DescriptorNode:

    def __init__(self):

        rospy.init_node('descriptor_node')

        self.bridge = CvBridge()

        self.pub = rospy.Publisher('/descriptors', DescriptorArray, queue_size=10)

        rospy.Subscriber('/camera_frames', Image, self.image_callback)
        rospy.Subscriber('/keypoints', KeypointArray, self.kp_callback)

        self.latest_image = None
        self.latest_kp = None

        self.orb = cv2.ORB_create()

        rospy.loginfo("[Descriptor Node] Started")

    # store image
    def image_callback(self, msg):
        self.latest_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    # store keypoints + compute descriptors
    def kp_callback(self, kp_msg):

        if self.latest_image is None:
            return

        gray = cv2.cvtColor(self.latest_image, cv2.COLOR_BGR2GRAY)

        # reconstruct cv2 Keypoints
        keypoints = []
        for i in range(len(kp_msg.x)):
            kp = cv2.KeyPoint(
                x=kp_msg.x[i],
                y=kp_msg.y[i],
                size=kp_msg.size[i]
            )
            keypoints.append(kp)

        # compute descriptors
        keypoints, descriptors = self.orb.compute(gray, keypoints)

        if descriptors is None:
            rospy.logwarn("No descriptors computed")
            return

        # flatten descriptors
        data = descriptors.flatten().astype(np.float32).tolist()

        out = DescriptorArray()
        out.header = kp_msg.header

        out.x = kp_msg.x
        out.y = kp_msg.y

        out.data = data
        out.num_keypoints = len(keypoints)
        out.descriptor_size = descriptors.shape[1]

        self.pub.publish(out)

        rospy.loginfo(f"[Descriptor] computed = {len(keypoints)}")


if __name__ == "__main__":
    DescriptorNode()
    rospy.spin()
