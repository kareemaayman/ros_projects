#!/usr/bin/env python3
import rospy
from surveillance_system.msg import SceneAnalysis, SecurityEvent
import datetime

class EventManagerNode:
    def __init__(self):
        rospy.init_node('event_manager_node')

        # Parameters
        self.restricted_objects = rospy.get_param('~restricted_objects', ['person'])
        self.danger_distance = rospy.get_param('~danger_distance', 2.0)

        # Publisher
        self.pub_event = rospy.Publisher('/security_event', SecurityEvent, queue_size=10)

        # Subscriber
        rospy.Subscriber('/scene_analysis', SceneAnalysis, self.scene_callback)

        rospy.loginfo("Event Manager Node Started")

    def scene_callback(self, data):
        # Loop over detected objects
        for obj in data.objects:
            event_type = None

            # Condition 1: Restricted object
            if obj.type in self.restricted_objects:
                event_type = "Restricted Area Breach"

            # Condition 2: Too close object
            elif obj.distance <= self.danger_distance:
                event_type = "Dangerously Close Object"

            # If event detected
            if event_type:
                event_msg = SecurityEvent()
                event_msg.event_type = event_type
                event_msg.object_type = obj.type
                event_msg.distance = obj.distance
                event_msg.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.pub_event.publish(event_msg)

                rospy.loginfo(f"[EVENT] {event_type} -> {obj.type} ({obj.distance:.2f} m)")

if __name__ == "__main__":
    try:
        node = EventManagerNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
