#!/usr/bin/env python3
"""
=============================================================
 Node 7 — Motion Estimation Node  (Student 2)
=============================================================
Responsibility:
  Estimate the relative camera motion direction from the
  geometric inlier correspondences. Since the camera is
  monocular, only direction — not metric scale — is inferred.

Topics Subscribed:
  /geometric_inliers  (multi_view_geometry/GeometricInliers)

Topics Published:
  /camera_motion  (multi_view_geometry/CameraMotion)

Parameters:
  ~focal_length : approx. focal length in pixels [default: 500]

Internal Logic:
  1. Compute mean optical flow vector (dx, dy) from inliers
  2. Horizontal direction:
       dx >  motion_thr → 'right'
       dx < -motion_thr → 'left'
       else             → 'none'
  3. Depth direction via spread change (divergence analysis):
       spread increases → features moving away from centre
                        → camera moving FORWARD
       spread decreases → features moving toward centre
                        → camera moving BACKWARD
  4. Scale ambiguity is always True for monocular systems.

ROS1 vs ROS2:
  ROS1: rospy.Subscriber, msg.header.stamp with rospy.Time
  ROS2: create_subscription, rclpy.time.Time
=============================================================
"""
import rospy
import numpy as np
from multi_view_geometry.msg import GeometricInliers, CameraMotion


class MotionEstimationNode:
    def __init__(self):
        rospy.init_node('motion_node', anonymous=False)

        self.focal_length    = rospy.get_param('~focal_length', 500.0)
        self.motion_thr      = rospy.get_param('~motion_threshold', 2.0)
        self.spread_thr      = rospy.get_param('~spread_threshold', 1.0)

        self.pub = rospy.Publisher('/camera_motion', CameraMotion, queue_size=10)
        rospy.Subscriber('/geometric_inliers', GeometricInliers,
                         self.callback, queue_size=5)

        rospy.loginfo("[Motion] Started | focal_length=%.1f px", self.focal_length)
        rospy.spin()

    def callback(self, inlier_msg):
        msg        = CameraMotion()
        msg.header = inlier_msg.header

        # ── Not enough inliers to estimate motion ─────────────────────────
        if inlier_msg.inlier_count < 4:
            msg.direction_horizontal = 'unknown'
            msg.direction_depth      = 'unknown'
            msg.translation_x        = 0.0
            msg.translation_y        = 0.0
            msg.magnitude            = 0.0
            msg.scale_ambiguous      = True
            self.pub.publish(msg)
            return

        q_x = np.array(inlier_msg.query_x, dtype=np.float32)
        q_y = np.array(inlier_msg.query_y, dtype=np.float32)
        t_x = np.array(inlier_msg.train_x, dtype=np.float32)
        t_y = np.array(inlier_msg.train_y, dtype=np.float32)

        # ── Mean optical flow ─────────────────────────────────────────────
        dx = float(np.mean(t_x - q_x))
        dy = float(np.mean(t_y - q_y))

        # ── Horizontal direction (left / right) ───────────────────────────
        if abs(dx) > self.motion_thr:
            h_dir = 'right' if dx > 0 else 'left'
        else:
            h_dir = 'none'

        # ── Depth direction (forward / backward) via spread divergence ────
        #    Centroid of previous & current point sets
        q_cx, q_cy = float(np.mean(q_x)), float(np.mean(q_y))
        t_cx, t_cy = float(np.mean(t_x)), float(np.mean(t_y))

        #    Mean distance from centroid (spread)
        q_spread = float(np.mean(np.sqrt((q_x - q_cx)**2 + (q_y - q_cy)**2)))
        t_spread = float(np.mean(np.sqrt((t_x - t_cx)**2 + (t_y - t_cy)**2)))
        d_spread = t_spread - q_spread  # positive → diverging → forward

        if abs(d_spread) > self.spread_thr:
            v_dir = 'forward' if d_spread > 0 else 'backward'
        else:
            v_dir = 'none'

        # ── Magnitude ─────────────────────────────────────────────────────
        magnitude = float(np.sqrt(dx**2 + dy**2))

        msg.direction_horizontal = h_dir
        msg.direction_depth      = v_dir
        msg.translation_x        = dx
        msg.translation_y        = dy
        msg.magnitude            = magnitude
        msg.scale_ambiguous      = True   # always true for monocular

        rospy.loginfo("[Motion] horizontal=%-6s  depth=%-9s  mag=%.2f px  "
                      "spread_delta=%.2f",
                      h_dir, v_dir, magnitude, d_spread)

        self.pub.publish(msg)


if __name__ == '__main__':
    MotionEstimationNode()
