#!/usr/bin/env python3
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from smart_surveillance.msg import DetectedObject
from ultralytics import YOLO

# Initialize ROS node
rospy.init_node('object_detector')

# Load YOLO model
model = YOLO("yolov8n.pt")  # replace with custom weights if needed

bridge = CvBridge()
pub = rospy.Publisher('/detected_objects', DetectedObject, queue_size=10)

def callback(msg):
    # Convert ROS Image to OpenCV image
    frame = bridge.imgmsg_to_cv2(msg, "bgr8")
    
    # Run YOLO detection
    results = model(frame)

    for r in results:
        for box in r.boxes:
            obj = DetectedObject()

            # Get class, confidence
            cls = int(box.cls[0])
            obj.label = model.names[cls]
            obj.confidence = float(box.conf[0])

            # Bounding box
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            obj.x = x1
            obj.y = y1
            obj.width = x2 - x1
            obj.height = y2 - y1

            # Publish the detected object
            pub.publish(obj)

            # Draw rectangle and label on frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{obj.label} {obj.confidence:.2f}", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, (0, 255, 0), 2)

    # Show the frame with detections
    cv2.imshow("Object Detection", frame)
    cv2.waitKey(1)

# Subscribe to camera frames
rospy.Subscriber('/camera_frames', Image, callback)

# Keep node alive
rospy.spin()

# Cleanup
cv2.destroyAllWindows()
