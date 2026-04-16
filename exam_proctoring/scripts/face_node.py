#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2

class FaceDetectionNode:
    def __init__(self):
        rospy.init_node('face_node', anonymous=True)
        self.bridge = CvBridge()

        self.scale_factor  = rospy.get_param('~scale_factor',  1.3)
        self.min_neighbors = rospy.get_param('~min_neighbors', 5)

        rospy.Subscriber('/camera_frames', Image, self.image_callback)
        self.pub         = rospy.Publisher('/face_data',    String, queue_size=10)
        self.display_pub = rospy.Publisher('/face_display', Image,  queue_size=10)  # ← display topic

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        rospy.loginfo("Face Detection Node Started")

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, self.scale_factor, self.min_neighbors)

        # ── Behavior state ──────────────────────────
        if len(faces) > 0:
            self.pub.publish("face_detected")
        else:
            self.pub.publish("no_face")

        # ── Draw bounding boxes for display ─────────
        display_frame = frame.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(display_frame, "Face", (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Publish annotated frame
        self.display_pub.publish(
            self.bridge.cv2_to_imgmsg(display_frame, encoding='bgr8'))

if __name__ == '__main__':
    try:
        node = FaceDetectionNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
