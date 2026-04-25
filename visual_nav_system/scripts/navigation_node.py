#!/usr/bin/env python3

import rospy
from visual_nav_system.msg import NavigationCommand
from visual_nav_system.msg import CameraMotion
from visual_nav_system.msg import ObjectData
from visual_nav_system.msg import DepthData


class NavigationNode:
    def __init__(self):
        rospy.init_node("navigation_node")

        # ---------------- PARAMETERS ----------------
        self.safety_distance = rospy.get_param("~safety_distance", 0.5)

        # ---------------- STATE STORAGE ----------------
        self.latest_camera = None
        self.latest_object = None
        self.latest_depth  = None

        # ---------------- SUBSCRIBERS (exactly as spec) ----------------
        rospy.Subscriber("/camera_motion", CameraMotion, self.camera_cb)
        rospy.Subscriber("/object_data",   ObjectData,   self.object_cb)
        rospy.Subscriber("/depth_data",    DepthData,    self.depth_cb)

        # ---------------- PUBLISHER ----------------
        self.pub = rospy.Publisher(
            "/navigation_command",
            NavigationCommand,
            queue_size=10
        )

        rospy.Timer(rospy.Duration(0.2), self.decision_loop)  # 5 FPS
        rospy.loginfo("Navigation Decision Node Started")

    # =================================================
    # CALLBACKS
    # =================================================
    def camera_cb(self, msg):
        self.latest_camera = msg

    def object_cb(self, msg):
        self.latest_object = msg

    def depth_cb(self, msg):
        self.latest_depth = msg

    # =================================================
    # HELPERS
    # =================================================
    def publish(self, command, duration=0.0):
        cmd = NavigationCommand()
        cmd.command  = command
        cmd.duration = duration
        self.pub.publish(cmd)
        rospy.loginfo_throttle(1, f"[NAV] -> {command} (duration={duration}s)")

    # =================================================
    # DECISION ENGINE
    # =================================================
    def decision_loop(self, event):

        # ---- RULE 1: Obstacle / depth safety check ----
        if self.latest_depth is not None:
            if (self.latest_depth.obstacle_detected or
                    self.latest_depth.average_depth < self.safety_distance):
                self.publish("STOP")
                return

        # ---- RULE 2: Camera motion (VO) based steering ----
        # The unreliable-motion -> STOP rule is the VO node's responsibility.
        # When motion is unreliable the VO node publishes valid=False,
        # so this block is skipped and we fall through to STOP below.
        if self.latest_camera is not None:
            if self.latest_camera.valid and self.latest_camera.confidence > 0.6:
                movement = self.latest_camera.movement.lower()

                if movement == "left":
                    self.publish("MOVE_LEFT",    1.0)
                elif movement == "right":
                    self.publish("MOVE_RIGHT",   1.0)
                elif movement == "forward":
                    self.publish("MOVE_FORWARD", 1.0)
                else:
                    self.publish("STOP")
                return

        # ---- RULE 3: Object-based avoidance ----
        if self.latest_object is not None:
            image_center    = 320  # assumes 640-wide frame
            # Use bounding box CENTER, not top-left corner
            object_center_x = self.latest_object.x + self.latest_object.width // 2

            if object_center_x < image_center:
                self.publish("MOVE_RIGHT", 0.8)  # object on left -> steer right
            else:
                self.publish("MOVE_LEFT",  0.8)  # object on right -> steer left
            return

        # ---- DEFAULT: nothing detected, stay safe ----
        self.publish("STOP")


if __name__ == "__main__":
    try:
        node = NavigationNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass