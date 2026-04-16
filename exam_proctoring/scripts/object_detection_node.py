#!/home/ka/yolo_env/bin/python3

import rospy
import cv2
from sensor_msgs.msg import Image
from exam_proctoring.msg import ObjectData
from cv_bridge import CvBridge
from ultralytics import YOLO

# Only what you care about
TARGET_CLASSES = {"cell phone", "book"}

class SimpleDetectionNode:
    def __init__(self):
        rospy.init_node("simple_detection_node")

        self.bridge = CvBridge()
        self.model = YOLO("yolov8n.pt")

        self.pub = rospy.Publisher("/object_data", ObjectData, queue_size=10)
        rospy.Subscriber("/camera_frames", Image, self.callback)

        self.conf_thr = 0.5

        rospy.loginfo("Simple Detection Node Started")

    def callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        frame = cv2.resize(frame, (640, 480))

        results = self.model(frame)

        out = ObjectData()
        out.header.stamp = rospy.Time.now()

        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                if conf < self.conf_thr:
                    continue

                cls = int(box.cls[0])
                label = self.model.names[cls]

                # Filter only phone & book
                if label not in TARGET_CLASSES:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Fill message
                out.object_detected = True
                out.object_labels.append(label)
                out.confidences.append(conf)
                out.bbox_x.append(x1)
                out.bbox_y.append(y1)
                out.bbox_w.append(x2 - x1)
                out.bbox_h.append(y2 - y1)

                if label == "cell phone":
                    out.phone_detected = True
                if label == "book":
                    out.book_detected = True

                # Draw box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f"{label} {conf:.2f}",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 255), 2)

        self.pub.publish(out)

        cv2.imshow("Detection", frame)
        cv2.waitKey(1)


if __name__ == "__main__":
    try:
        node = SimpleDetectionNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
