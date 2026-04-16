#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2

class DepthEstimationNode:
    def __init__(self):
        rospy.init_node('depth_node', anonymous=True)
        self.bridge = CvBridge()

        self.depth_threshold_close = rospy.get_param('~depth_threshold_close', 30)
        self.depth_threshold_far   = rospy.get_param('~depth_threshold_far',   80)

        rospy.Subscriber('/camera_frames', Image, self.image_callback)
        self.pub         = rospy.Publisher('/depth_data',    String, queue_size=10)
        self.display_pub = rospy.Publisher('/depth_display', Image,  queue_size=10)  # ← display topic

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        self.KNOWN_FACE_WIDTH = 14.0
        self.FOCAL_LENGTH     = 600
        rospy.loginfo("Depth Estimation Node Started")

    def estimate_distance(self, face_width_pixels):
        if face_width_pixels == 0:
            return 0
        return (self.KNOWN_FACE_WIDTH * self.FOCAL_LENGTH) / face_width_pixels

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        display_frame = frame.copy()

        if len(faces) == 0:
            self.pub.publish("normal")
            cv2.putText(display_frame, "No face", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (128, 128, 128), 2)
        else:
            x, y, w, h = faces[0]  # use first face only
            distance = self.estimate_distance(w)

            # ── Behavior state ───────────────────────
            if distance < self.depth_threshold_close:
                state = "close"
                color = (0, 0, 255)    # red
            elif distance > self.depth_threshold_far:
                state = "far"
                color = (255, 165, 0)  # orange
            else:
                state = "normal"
                color = (0, 255, 0)    # green

            self.pub.publish(state)

            # ── Draw box + distance label ─────────────
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(display_frame,
                        f"Dist: {distance:.1f}cm ({state})",
                        (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        self.display_pub.publish(
            self.bridge.cv2_to_imgmsg(display_frame, encoding='bgr8'))

if __name__ == '__main__':
    try:
        node = DepthEstimationNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
