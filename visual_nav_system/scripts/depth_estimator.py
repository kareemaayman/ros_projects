#!/usr/bin/env python3

import rospy
import numpy as np
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from visual_nav_system.msg import DepthData

bridge = CvBridge()

class DepthEstimationNode:
    def __init__(self):
        rospy.init_node('depth_estimator')

        # ---------------- PARAMETERS ----------------
        self.depth_threshold = rospy.get_param('~depth_threshold', 1.5)  # meters

        # ---------------- PUBLISHERS ----------------
        self.pub_depth_img = rospy.Publisher('/object_depth', Image, queue_size=1)
        self.pub_depth_data = rospy.Publisher('/depth_data', DepthData, queue_size=1)

        # ---------------- SUBSCRIBER ----------------
        rospy.Subscriber('/camera_frames', Image, self.callback, queue_size=1)

        rospy.loginfo("Depth Estimation Node Started")

    # =========================================================
    # DEPTH ESTIMATION (RELATIVE, STABLE)
    # =========================================================
    def estimate_depth(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0

        # ---- Cue 1: Intensity (dark = far, bright = near)
        intensity = gray

        # ---- Cue 2: Blur (blurrier = farther)
        lap = cv2.Laplacian(gray, cv2.CV_32F)
        blur_measure = cv2.GaussianBlur(np.abs(lap), (9, 9), 0)

        # ---- Cue 3: Vertical prior (bottom = closer)
        h, w = gray.shape
        vertical_prior = np.linspace(1.0, 0.0, h).reshape(h, 1)
        vertical_prior = np.repeat(vertical_prior, w, axis=1)

        # ---- Combine cues
        depth = (
            0.5 * intensity +
            0.3 * blur_measure +
            0.2 * vertical_prior
        )

        # ---- Normalize safely
        d_min, d_max = depth.min(), depth.max()
        if (d_max - d_min) < 1e-6:
            depth_norm = np.zeros_like(depth)
        else:
            depth_norm = (depth - d_min) / (d_max - d_min)

        return depth_norm.astype(np.float32)

    # =========================================================
    # DEPTH → METERS (PSEUDO, CONTROLLED)
    # =========================================================
    def to_meters(self, depth_norm):
        # 0 → far (5m), 1 → near (0.5m)
        return 0.5 + (1.0 - depth_norm) * 4.5

    # =========================================================
    # MAIN CALLBACK
    # =========================================================
    def callback(self, msg):
        try:
            frame = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            frame = cv2.resize(frame, (320, 240))

            depth_norm = self.estimate_depth(frame)
            depth_m = self.to_meters(depth_norm)

            # ---- Stats
            avg_depth = float(np.mean(depth_m))
            min_depth = float(np.min(depth_m))
            max_depth = float(np.max(depth_m))

            # ---- Obstacle detection (robust)
            close_pixels = depth_m < self.depth_threshold
            obstacle = bool(np.sum(close_pixels) > 0.05 * close_pixels.size)

            # ---- Publish depth image
            depth_img_msg = bridge.cv2_to_imgmsg(depth_norm, encoding="32FC1")
            depth_img_msg.header = msg.header
            self.pub_depth_img.publish(depth_img_msg)

            # ---- Publish structured data
            depth_data = DepthData()
            depth_data.average_depth = avg_depth
            depth_data.min_depth = min_depth
            depth_data.max_depth = max_depth
            depth_data.obstacle_detected = obstacle

            self.pub_depth_data.publish(depth_data)

            rospy.loginfo_throttle(
                2,
                f"[DEPTH] avg={avg_depth:.2f}m min={min_depth:.2f}m obstacle={obstacle}"
            )

        except Exception as e:
            rospy.logerr(f"Depth error: {e}")


if __name__ == '__main__':
    try:
        node = DepthEstimationNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass