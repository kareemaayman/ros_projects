#!/usr/bin/env python3

import rospy
from visual_nav_system.msg import MotionData
from visual_nav_system.msg import CameraMotion


class VisualOdometryNode:

    def __init__(self):

        rospy.init_node("vo_node")

        # ---------------- PARAMETERS ----------------
        self.motion_threshold = rospy.get_param("~motion_threshold", 0.5)  # minimum motion magnitude to be considered valid
        self.confidence_scale = rospy.get_param("~confidence_scale", 5.0)

        # ---------------- PUBLISHER ----------------
        self.pub = rospy.Publisher(
            "/camera_motion",
            CameraMotion,
            queue_size=10
        )

        # ---------------- SUBSCRIBER ----------------
        rospy.Subscriber("/motion_data", MotionData, self.callback)

        rospy.loginfo("Visual Odometry Node Started")

    # =================================================
    # CORE LOGIC
    # =================================================

    def callback(self, msg):

        vo_msg = CameraMotion()

        # ---------------- VALIDATION ----------------
        if not msg.reliable or msg.magnitude < self.motion_threshold:
            vo_msg.valid = False
            vo_msg.movement = "stop"
            vo_msg.confidence = 0.0

            self.pub.publish(vo_msg)
            rospy.logwarn("[VO] Unreliable motion → STOP")
            return

        # ---------------- DIRECTION ESTIMATION ----------------
        dx = msg.dx
        dy = msg.dy

        if abs(dx) > abs(dy):
            if dx > 0:
                movement = "left"   # image right → camera left
            else:
                movement = "right"
        else:
            if dy > 0:
                movement = "backward"
            else:
                movement = "forward"

        # ---------------- CONFIDENCE ----------------
        confidence = min(1.0, msg.magnitude / self.confidence_scale)

        # ---------------- OUTPUT ----------------
        vo_msg.valid = True
        vo_msg.movement = movement
        vo_msg.confidence = confidence

        self.pub.publish(vo_msg)

        rospy.loginfo(
            f"[VO] movement={movement}, confidence={confidence:.2f}"
        )


# =================================================
# MAIN
# =================================================

if __name__ == "__main__":
    VisualOdometryNode()
    rospy.spin()