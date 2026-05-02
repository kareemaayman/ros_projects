#!/usr/bin/env python3
"""
=============================================================
 Node 8 — Reliability Decision Node  (Student 5)
=============================================================
Responsibility:
  Monitor the full pipeline and decide whether the system
  is operating reliably. Publishes a system state on every
  motion update, and serves reliability reports via an
  actionlib action server with live feedback.

Topics Subscribed:
  /camera_motion      (multi_view_geometry/CameraMotion)
  /geometric_inliers  (multi_view_geometry/GeometricInliers)

Topics Published:
  /system_state  (multi_view_geometry/SystemState)
      State values:
        RELIABLE      — pipeline is healthy
        UNRELIABLE    — too many outliers / excessive motion
        LOW_FEATURES  — not enough keypoints to work with

Action Server:
  /report_action  (multi_view_geometry/ReportAction)
      Goal:     request_type  (string)
      Feedback: current_status, processed_frames
      Result:   final_state, total_inliers, reliability_score

Parameters:
  ~min_inliers      : minimum inlier count for RELIABLE   [default: 10]
  ~min_inlier_ratio : minimum inlier ratio for RELIABLE   [default: 0.3]
  ~max_magnitude    : motion magnitude that flags UNRELIABLE [default: 80.0]

=============================================================
"""
import rospy
import actionlib

from multi_view_geometry.msg import (
    CameraMotion, GeometricInliers, SystemState,
    ReportAction, ReportResult, ReportFeedback
)


class ReliabilityDecisionNode:
    def __init__(self):
        rospy.init_node('decision_node', anonymous=False)

        # ── Parameters ────────────────────────────────────────────────────
        self.min_inliers      = rospy.get_param('~min_inliers',      10)
        self.min_inlier_ratio = rospy.get_param('~min_inlier_ratio', 0.30)
        self.max_magnitude    = rospy.get_param('~max_magnitude',    80.0)

        # ── Internal state ────────────────────────────────────────────────
        self.latest_motion   = None
        self.latest_inliers  = None
        self.frame_count     = 0

        # ── Publishers ────────────────────────────────────────────────────
        self.state_pub = rospy.Publisher('/system_state', SystemState, queue_size=10)

        # ── Action Server (/report_action) ────────────────────────────────
        #    The action server allows any client to request a detailed
        #    reliability report, receiving step-by-step feedback while
        #    the report is being assembled.
        self.action_server = actionlib.SimpleActionServer(
            '/report_action',
            ReportAction,
            execute_cb=self._execute_action,
            auto_start=False
        )
        self.action_server.start()

        # ── Subscribers ───────────────────────────────────────────────────
        rospy.Subscriber('/camera_motion',     CameraMotion,     self._motion_cb,  queue_size=5)
        rospy.Subscriber('/geometric_inliers', GeometricInliers, self._inlier_cb,  queue_size=5)

        rospy.loginfo("[Decision] Started | min_inliers=%d | min_ratio=%.2f | max_mag=%.1f",
                      self.min_inliers, self.min_inlier_ratio, self.max_magnitude)
        rospy.spin()

    # =========================================================
    #  Subscriber callbacks
    # =========================================================
    def _inlier_cb(self, msg):
        self.latest_inliers = msg
        self.frame_count   += 1

    def _motion_cb(self, msg):
        self.latest_motion = msg
        self._publish_state()          # re-evaluate on every motion update

    # =========================================================
    #  Core reliability logic
    # =========================================================
    def _evaluate(self):
        """
        Returns (state: str, reason: str, inlier_count: int)

        Decision tree:
          1. No data at all             → UNRELIABLE
          2. Zero feature matches       → LOW_FEATURES
          3. Very few geometric inliers → LOW_FEATURES
          4. Inlier count < min        → UNRELIABLE
          5. Inlier ratio < min        → UNRELIABLE
          6. Motion magnitude too high → UNRELIABLE (blur / dynamic scene)
          7. Everything OK             → RELIABLE
        """
        # Step 1 — no data
        if self.latest_inliers is None:
            return 'UNRELIABLE', 'Waiting for geometric data', 0

        n_inliers = self.latest_inliers.inlier_count
        n_matches = self.latest_inliers.total_matches
        ratio     = self.latest_inliers.inlier_ratio

        # Step 2 — no matches at all
        if n_matches == 0:
            return 'LOW_FEATURES', 'No feature matches in pipeline', 0

        # Step 3 — geometry unstable
        if n_inliers < 4:
            return 'LOW_FEATURES', (
                f'Only {n_inliers} inliers — too few for geometry'), n_inliers

        # Step 4 — absolute inlier count
        if n_inliers < self.min_inliers:
            return 'UNRELIABLE', (
                f'Inlier count {n_inliers} < min {self.min_inliers}'), n_inliers

        # Step 5 — inlier ratio
        if ratio < self.min_inlier_ratio:
            return 'UNRELIABLE', (
                f'Inlier ratio {ratio:.2f} < min {self.min_inlier_ratio:.2f}'), n_inliers

        # Step 6 — excessive motion
        if self.latest_motion is not None:
            mag = self.latest_motion.magnitude
            if mag > self.max_magnitude:
                return 'UNRELIABLE', (
                    f'Motion {mag:.1f}px > {self.max_magnitude}px — blur/dynamic scene'), n_inliers

        return 'RELIABLE', 'Pipeline operating normally', n_inliers

    def _publish_state(self):
        state, reason, n_inliers = self._evaluate()

        msg              = SystemState()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = 'world'
        msg.state        = state
        msg.reason       = reason
        msg.num_inliers  = n_inliers
        msg.num_matches  = (self.latest_inliers.total_matches
                            if self.latest_inliers else 0)

        self.state_pub.publish(msg)
        rospy.loginfo("[Decision] %-12s | inliers=%d | %s", state, n_inliers, reason)

    # =========================================================
    #  Action Server callback — /report_action
    # =========================================================
    def _execute_action(self, goal):
        """
        Called when a client sends a goal to /report_action.
        Sends incremental feedback then returns the result.
        """
        rospy.loginfo("[Decision Action] Goal received: '%s'", goal.request_type)

        fb = ReportFeedback()

        # ── Feedback step 1 ───────────────────────────────────────────────
        fb.current_status   = 'Sampling pipeline state...'
        fb.processed_frames = self.frame_count
        self.action_server.publish_feedback(fb)
        rospy.sleep(0.4)

        # ── Feedback step 2 ───────────────────────────────────────────────
        state, reason, n_inliers = self._evaluate()
        fb.current_status   = f'Evaluating: {state} — {reason}'
        fb.processed_frames = self.frame_count
        self.action_server.publish_feedback(fb)
        rospy.sleep(0.4)

        # ── Feedback step 3 ───────────────────────────────────────────────
        fb.current_status   = 'Computing reliability score...'
        self.action_server.publish_feedback(fb)
        rospy.sleep(0.2)

        # ── Build result ──────────────────────────────────────────────────
        if state == 'RELIABLE' and self.latest_inliers:
            score = min(1.0, float(self.latest_inliers.inlier_ratio))
        elif state == 'LOW_FEATURES':
            score = 0.1
        else:
            score = 0.0

        result                   = ReportResult()
        result.final_state       = state
        result.total_inliers     = n_inliers
        result.reliability_score = score

        self.action_server.set_succeeded(result)
        rospy.loginfo("[Decision Action] Done: state=%s  score=%.2f  inliers=%d",
                      state, score, n_inliers)


if __name__ == '__main__':
    ReliabilityDecisionNode()
