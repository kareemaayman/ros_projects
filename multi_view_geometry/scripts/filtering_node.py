#!/usr/bin/env python3
'''
Feature Match Filtering Node
it uses 2 filters
1. Absolute threshold Reject matches where: distance > threshold
2. Statistical filtering Reject outliers using: distance > mean + 1.5 * std_d
Final condition:
distance <= min(threshold,mean + 1.5 * std_d)
'''
import rospy
import numpy as np
from multi_view_geometry.msg import MatchArray


class MatchFilteringNode:
    def __init__(self):
        rospy.init_node('filtering_node', anonymous=False)

        self.dist_threshold = rospy.get_param('~ratio_test_threshold', 60.0)
        self.min_matches    = rospy.get_param('~min_matches', 8)

        self.pub = rospy.Publisher('/filtered_matches', MatchArray, queue_size=10)
        rospy.Subscriber('/raw_matches', MatchArray, self.callback, queue_size=5)

        rospy.loginfo("[Filter] Started | dist_threshold=%.1f | min_matches=%d",
                      self.dist_threshold, self.min_matches)
        rospy.spin()

    def callback(self, match_msg):
        # Pass-through empty messages
        if match_msg.count == 0:
            self.pub.publish(match_msg)
            return

        distances = np.array(match_msg.distance, dtype=np.float32)

        # ── Statistical + absolute threshold ─────────────────────────────
        mean_d  = float(np.mean(distances))
        std_d   = float(np.std(distances))
        upper   = min(self.dist_threshold, mean_d + 1.5 * std_d)

        keep    = np.where(distances <= upper)[0]

        # ── Build filtered message ────────────────────────────────────────
        msg        = MatchArray()
        msg.header = match_msg.header

        for i in keep:
            msg.query_idx.append(match_msg.query_idx[i])
            msg.train_idx.append(match_msg.train_idx[i])
            msg.query_x.append(match_msg.query_x[i])
            msg.query_y.append(match_msg.query_y[i])
            msg.train_x.append(match_msg.train_x[i])
            msg.train_y.append(match_msg.train_y[i])
            msg.distance.append(match_msg.distance[i])

        msg.count = len(msg.query_idx)
        removed   = match_msg.count - msg.count

        if msg.count < self.min_matches:
            rospy.logwarn("[Filter] Only %d filtered matches (min=%d). "
                          "Scene may be featureless or blurry.", msg.count, self.min_matches)
        else:
            rospy.loginfo("[Filter] %d → %d matches (%d removed | threshold=%.1f)",
                          match_msg.count, msg.count, removed, upper)

        self.pub.publish(msg)


if __name__ == '__main__':
    MatchFilteringNode()
