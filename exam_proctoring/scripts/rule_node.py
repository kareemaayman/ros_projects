#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from exam_proctoring.srv import CheckViolation, CheckViolationResponse
import actionlib
from exam_proctoring.msg import AlertAction, AlertGoal

violation_pub = None
alert_client = None  # ← must be global

def evaluate_behavior(behavior):
    if behavior == "looking_away":
        return True, "looking_away", 1
    elif behavior == "using_phone":
        return True, "prohibited_object", 3
    elif behavior == "too_far":
        return True, "unusual_distance", 1
    else:
        return False, "none", 0

def behavior_callback(msg):
    behavior = msg.data
    rospy.loginfo(f"[Rule Node] Received behavior: {behavior}")
    detected, v_type, severity = evaluate_behavior(behavior)

    if detected:
        # Trigger action server
        goal = AlertGoal()
        goal.violation_type = v_type
        goal.severity = severity
        alert_client.send_goal(goal)  # ✅ now accessible

        out = String()
        out.data = f"VIOLATION:{v_type}:severity_{severity}"
        violation_pub.publish(out)
        rospy.loginfo(f"[Rule Node] Violation published: {out.data}")
    else:
        out = String()
        out.data = "no_violation"
        violation_pub.publish(out)
        rospy.loginfo("[Rule Node] No violation.")

def handle_check_violation(req):
    detected, v_type, severity = evaluate_behavior(req.behavior)
    return CheckViolationResponse(
        violation_detected=detected,
        violation_type=v_type,
        severity=severity
    )

def main():
    global violation_pub, alert_client  # ← declare both global
    rospy.init_node('rule_node', anonymous=False)

    violation_pub = rospy.Publisher('/violation_event', String, queue_size=10)
    rospy.Subscriber('/behavior_state', String, behavior_callback)
    rospy.Service('/check_violation', CheckViolation, handle_check_violation)

    alert_client = actionlib.SimpleActionClient('/alert_action', AlertAction)
    alert_client.wait_for_server()

    rospy.loginfo("[Rule Node] Ready and running.")
    rospy.spin()

if __name__ == '__main__':
    main()
