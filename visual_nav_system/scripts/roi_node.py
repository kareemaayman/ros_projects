#!/usr/bin/env python3

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from visual_nav_system.msg import RoiFeatures

bridge = CvBridge()
pub = None

roi_ratio = None # percentage of frame to use as ROI, set via ROS param


def callback(msg):

    frame = bridge.imgmsg_to_cv2(msg, "bgr8")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape

    roi_h = int(h * roi_ratio)
    roi_w = int(w * roi_ratio)

    start_y = h // 2 - roi_h // 2
    start_x = w // 2 - roi_w // 2

    roi = gray[start_y:start_y + roi_h, start_x:start_x + roi_w]

    # ---- REAL FEATURES ----
    mean_intensity = float(np.mean(roi))
    variance = float(np.var(roi))

    # gradient-based centroid proxy (STABLE signal)
    edges = cv2.Canny(roi, 50, 150)
    moments = cv2.moments(edges)
    if moments["m00"] != 0:
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
    else:
        cx, cy = roi_w // 2, roi_h // 2

    msg_out = RoiFeatures()
    msg_out.centroid_x = cx
    msg_out.centroid_y = cy
    msg_out.mean_intensity = mean_intensity
    msg_out.variance = variance
    msg_out.area = roi_w * roi_h

    pub.publish(msg_out)

    rospy.loginfo(f"[ROI] cx={cx}, cy={cy}, mean={mean_intensity:.2f}")


def main():
    global pub, roi_ratio

    rospy.init_node("roi_node")
    roi_ratio = rospy.get_param("~roi_size", 0.4)

    pub = rospy.Publisher("/roi_features", RoiFeatures, queue_size=10)
    rospy.Subscriber("/camera_frames", Image, callback)

    rospy.loginfo("ROI Node Started")

    rospy.spin()


if __name__ == "__main__":
    main()