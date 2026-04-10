#!/usr/bin/env python3

import rospy
import numpy as np
import cv2
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
from cv_bridge import CvBridge

bridge = CvBridge()
pub_depth = None
pub_distance = None

def estimate_depth_fast(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Use Laplacian to estimate depth from focus/blur
    blur = cv2.GaussianBlur(gray, (21, 21), 0)
    depth = cv2.Laplacian(blur, cv2.CV_32F)
    depth = np.abs(depth)

    # Also use intensity as a depth cue (darker = farther)
    intensity = gray.astype(np.float32) / 255.0

    # Combine both cues
    depth_map = 0.7 * depth + 0.3 * intensity

    # Normalize to 0-1
    depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min() + 1e-8)

    return depth_map.astype(np.float32)

def estimate_distance(depth_map):
    # Find the closest region — pixels with depth value above 80th percentile
    threshold = np.percentile(depth_map, 80)
    close_region = depth_map[depth_map > threshold]

    # Average depth of that region (0-1 scale)
    avg_depth = float(np.mean(close_region))

    # Convert to estimated meters (1.0 = very close ~0.5m, 0.0 = far ~10m)
    estimated_meters = (1.0 - avg_depth) * 10.0

    return round(estimated_meters, 2)

def frame_callback(msg):
    try:
        frame = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        frame = cv2.resize(frame, (320, 240))

        # Generate depth map
        depth_map = estimate_depth_fast(frame)

        # Estimate distance of closest object
        distance = estimate_distance(depth_map)

        # Publish depth map image
        depth_msg = bridge.cv2_to_imgmsg(depth_map, encoding="32FC1")
        depth_msg.header = msg.header
        pub_depth.publish(depth_msg)

        # Publish distance value
        pub_distance.publish(Float32(distance))

        rospy.loginfo_throttle(5, f"Depth running | Closest object: ~{distance}m")

    except Exception as e:
        rospy.logerr(f"Depth callback error: {e}")

def main():
    global pub_depth, pub_distance

    rospy.init_node('depth_estimation_node')

    pub_depth = rospy.Publisher('/object_depth', Image, queue_size=1)
    pub_distance = rospy.Publisher('/object_distance', Float32, queue_size=1)

    rospy.Subscriber('/camera_frames', Image, frame_callback, queue_size=1)

    rospy.loginfo("Depth estimation node ready!")
    rospy.spin()

if __name__ == '__main__':
    main()
