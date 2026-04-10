#!/usr/bin/env python3
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

# Initialize ROS node
rospy.init_node('camera_stream')
pub = rospy.Publisher('/camera_frames', Image, queue_size=10)

bridge = CvBridge()
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    rospy.logerr("Cannot open camera")
    exit()

rate = rospy.Rate(10)  # 10 Hz

while not rospy.is_shutdown():
    ret, frame = cap.read()
    if ret:
        # Publish frame to ROS topic
        msg = bridge.cv2_to_imgmsg(frame, "bgr8")
        pub.publish(msg)
        
        # Show the frame in a window
        cv2.imshow("Camera Stream", frame)
        cv2.waitKey(1)  # Needed to refresh the OpenCV window

# Release camera and close window when exiting
cap.release()
cv2.destroyAllWindows()
