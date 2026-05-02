#!/usr/bin/env python3
"""
=============================================================
 Node 6 — Geometric Consistency Node  ★ STUDENT 1 ★
=============================================================
Responsibility:
  Verify that feature matches are geometrically consistent
  with the epipolar constraint (multi-view geometry).

  The Fundamental Matrix F satisfies:
      p2.T @ F @ p1 ≈ 0   for all true correspondences
  where p1, p2 are homogeneous image coordinates.

  RANSAC is used to robustly estimate F and simultaneously
  classify each match as an inlier or outlier.

Topics Subscribed:
  /filtered_matches   (multi_view_geometry/MatchArray)

Topics Published:
  /geometric_inliers  (multi_view_geometry/GeometricInliers)

Services Provided:
  /check_geometry     (multi_view_geometry/CheckGeometry)
      → Validate an arbitrary set of correspondences on demand.

Parameters:
  ~inlier_threshold : RANSAC reprojection threshold in pixels
                      [default: 3.0]

Internal Logic:
  1. Build Nx2 point arrays from the filtered match message
  2. Call cv2.findFundamentalMat(pts1, pts2, FM_RANSAC)
  3. The returned mask flags inliers / outliers
  4. Extract inlier point pairs and publish GeometricInliers

Epipolar Geometry — brief explanation:
  For two views of the same static scene, every pair of
  corresponding points (p1, p2) must satisfy:
      p2^T F p1 = 0
  This is the epipolar constraint. RANSAC finds the F that
  maximises the number of matches satisfying it within
  `inlier_threshold` pixels — those matches are inliers.

ROS1 vs ROS2 differences:
  ROS1 Service: rospy.Service(name, SrvType, handler)
  ROS2 Service: node.create_service(SrvType, name, handler)
  
  ROS1 spin:    rospy.spin()
  ROS2 spin:    rclpy.spin(node)
=============================================================
"""
import rospy
import cv2
import numpy as np

from multi_view_geometry.msg import MatchArray, GeometricInliers
from multi_view_geometry.srv import CheckGeometry, CheckGeometryResponse


class GeometricConsistencyNode:

    # Minimum points needed to estimate a Fundamental Matrix
    MIN_PTS_FOR_F = 8

    def __init__(self):
        rospy.init_node('geometry_node', anonymous=False)

        # ── Parameters ────────────────────────────────────────────────────
        self.inlier_threshold = rospy.get_param('~inlier_threshold', 3.0)

        # State shared with the service handler
        self.latest_inliers = None

        # ── ROS Communication ─────────────────────────────────────────────
        self.pub = rospy.Publisher('/geometric_inliers', GeometricInliers, queue_size=10)

        rospy.Subscriber('/filtered_matches', MatchArray,
                         self.callback, queue_size=5)

        rospy.Service('/check_geometry', CheckGeometry,
                      self.handle_check_geometry)

        rospy.loginfo("[Geometry] Started | RANSAC threshold=%.1f px",
                      self.inlier_threshold)
        rospy.spin()

    # =========================================================
    #  Core: Fundamental Matrix estimation
    # =========================================================
    def estimate_F_with_ransac(self, pts1, pts2):
        """
        Estimate the Fundamental Matrix using OpenCV's RANSAC.

        Args:
            pts1: Nx2 float32 array — points in frame t-1
            pts2: Nx2 float32 array — points in frame t

        Returns:
            F    : 3x3 Fundamental Matrix (or None on failure)
            mask : Nx1 uint8 array where 1=inlier, 0=outlier
        """
        # Validate inputs before any processing
        if pts1 is None or pts2 is None:
            return None, None
        if len(pts1) == 0 or len(pts2) == 0:
            return None, None
        if len(pts1) != len(pts2):
            rospy.logwarn("[Geometry] Point count mismatch: %d vs %d",
                          len(pts1), len(pts2))
            return None, None
        if len(pts1) < self.MIN_PTS_FOR_F:
            return None, None

        # Ensure arrays are contiguous and have correct dtype
        pts1 = np.ascontiguousarray(pts1, dtype=np.float32)
        pts2 = np.ascontiguousarray(pts2, dtype=np.float32)

        # OpenCV requires shape (N, 1, 2) for findFundamentalMat
        p1 = pts1.reshape(-1, 1, 2)
        p2 = pts2.reshape(-1, 1, 2)

        try:
            F, mask = cv2.findFundamentalMat(
                p1, p2,
                method=cv2.FM_RANSAC,
                ransacReprojThreshold=self.inlier_threshold,
                confidence=0.99,
                maxIters=2000
            )
        except cv2.error as e:
            rospy.logwarn("[Geometry] findFundamentalMat OpenCV error: %s", str(e))
            return None, None

        # findFundamentalMat can return None F when all points are colinear
        if F is None or mask is None:
            return None, None

        return F, mask

    # =========================================================
    #  Subscriber callback — runs on every /filtered_matches msg
    # =========================================================
    def callback(self, match_msg):
        msg               = GeometricInliers()
        msg.header        = match_msg.header
        msg.total_matches = match_msg.count

        # ── Edge case: not enough matches ─────────────────────────────────
        if match_msg.count < self.MIN_PTS_FOR_F:
            msg.inlier_count = 0
            msg.inlier_ratio = 0.0
            rospy.logwarn("[Geometry] Only %d matches — need ≥%d for F estimation",
                          match_msg.count, self.MIN_PTS_FOR_F)
            self._publish(msg)
            return

        # ── Build point arrays safely ─────────────────────────────────────
        pts1 = np.array(list(zip(match_msg.query_x, match_msg.query_y)),
                        dtype=np.float32)
        pts2 = np.array(list(zip(match_msg.train_x,  match_msg.train_y)),
                        dtype=np.float32)

        # Guard: drop any rows that contain NaN or Inf
        valid = (np.isfinite(pts1).all(axis=1) & np.isfinite(pts2).all(axis=1))
        pts1, pts2 = pts1[valid], pts2[valid]

        if len(pts1) < self.MIN_PTS_FOR_F:
            rospy.logwarn("[Geometry] Only %d finite point pairs after NaN filter",
                          len(pts1))
            msg.inlier_count = 0
            msg.inlier_ratio = 0.0
            self._publish(msg)
            return

        # ── RANSAC Fundamental Matrix ─────────────────────────────────────
        F, mask = self.estimate_F_with_ransac(pts1, pts2)

        if mask is None:
            rospy.logwarn("[Geometry] F estimation failed (degenerate configuration?)")
            msg.inlier_count = 0
            msg.inlier_ratio = 0.0
            self._publish(msg)
            return

        # ── Classify inliers ──────────────────────────────────────────────
        mask_flat      = mask.ravel().astype(bool)
        inlier_pts1    = pts1[mask_flat]
        inlier_pts2    = pts2[mask_flat]
        num_inliers    = int(np.sum(mask_flat))

        msg.query_x     = inlier_pts1[:, 0].tolist()
        msg.query_y     = inlier_pts1[:, 1].tolist()
        msg.train_x     = inlier_pts2[:, 0].tolist()
        msg.train_y     = inlier_pts2[:, 1].tolist()
        msg.inlier_count = num_inliers
        msg.inlier_ratio = (float(num_inliers) / match_msg.count
                            if match_msg.count > 0 else 0.0)

        rospy.loginfo("[Geometry] Inliers: %d / %d  (%.1f%%)  | F rank=%s",
                      num_inliers, match_msg.count,
                      msg.inlier_ratio * 100,
                      str(np.linalg.matrix_rank(F)) if F is not None else 'N/A')

        self._publish(msg)

    def _publish(self, msg):
        self.latest_inliers = msg
        self.pub.publish(msg)

    # =========================================================
    #  Service handler — /check_geometry
    # =========================================================
    def handle_check_geometry(self, req):
        """
        On-demand geometric validation service.
        Clients can send any set of correspondences to verify.
        """
        resp = CheckGeometryResponse()

        if len(req.query_x) < self.MIN_PTS_FOR_F:
            resp.is_consistent   = False
            resp.inlier_ratio    = 0.0
            resp.inlier_indices  = []
            rospy.logwarn("[Geometry /check_geometry] Too few points: %d", len(req.query_x))
            return resp

        pts1 = np.array(list(zip(req.query_x, req.query_y)), dtype=np.float32)
        pts2 = np.array(list(zip(req.train_x,  req.train_y)), dtype=np.float32)

        valid = (np.isfinite(pts1).all(axis=1) & np.isfinite(pts2).all(axis=1))
        pts1, pts2 = pts1[valid], pts2[valid]

        if len(pts1) < self.MIN_PTS_FOR_F:
            resp.is_consistent  = False
            resp.inlier_ratio   = 0.0
            resp.inlier_indices = []
            return resp

        F, mask = self.estimate_F_with_ransac(pts1, pts2)

        if mask is None:
            resp.is_consistent  = False
            resp.inlier_ratio   = 0.0
            resp.inlier_indices = []
            return resp

        mask_flat       = mask.ravel().astype(bool)
        inlier_indices  = [int(i) for i, v in enumerate(mask_flat) if v]
        inlier_ratio    = float(np.sum(mask_flat)) / len(pts1)

        resp.is_consistent   = inlier_ratio > 0.30   # 30% threshold
        resp.inlier_indices  = inlier_indices
        resp.inlier_ratio    = inlier_ratio

        rospy.loginfo("[Geometry /check_geometry] consistent=%s  ratio=%.2f  inliers=%d/%d",
                      resp.is_consistent, resp.inlier_ratio,
                      len(inlier_indices), len(pts1))
        return resp


if __name__ == '__main__':
    GeometricConsistencyNode()
