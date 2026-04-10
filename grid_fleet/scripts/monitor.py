#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
import time

vehicle_states = {}
vehicle_positions = {}
last_move_time = {}

def state_callback(msg):
    parts = msg.data.split()
    if len(parts) >= 2:
        vid = parts[0]
        state = parts[1]
        vehicle_states[vid] = state

def position_callback(msg):
    parts = msg.data.split()
    if len(parts) >= 3:
        vid = parts[0]
        x = int(parts[1])
        y = int(parts[2])
        vehicle_positions[vid] = (x, y)
        last_move_time[vid] = time.time()

if __name__ == "__main__":
    rospy.init_node("monitor")

    # Subscribe to all vehicle topics
    rospy.Subscriber("/vehicle1/state", String, state_callback)
    rospy.Subscriber("/vehicle2/state", String, state_callback)
    rospy.Subscriber("/vehicle3/state", String, state_callback)

    rospy.Subscriber("/vehicle1/position", String, position_callback)
    rospy.Subscriber("/vehicle2/position", String, position_callback)
    rospy.Subscriber("/vehicle3/position", String, position_callback)

    rate = rospy.Rate(0.5)

    while not rospy.is_shutdown():
        print("\n--- SYSTEM STATUS ---")
        for vid in vehicle_states:
            pos = vehicle_positions.get(vid, ("?", "?"))
            print(f"{vid}: {vehicle_states[vid]} at {pos}")

            if vid in last_move_time and time.time() - last_move_time[vid] > 10:
                print(f"WARNING: {vid} might be stuck!")

        rate.sleep()
