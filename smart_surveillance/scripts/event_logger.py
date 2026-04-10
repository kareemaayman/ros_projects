#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from datetime import datetime

# Storage for events
event_log = []
alert_log = []

# Optional: log file
log_file = open("event_logger.log", "a")

def write_to_file(message):
    log_file.write(message + "\n")
    log_file.flush()

def event_callback(msg):
    time_now = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{time_now}] [EVENT] {msg.data}"
    
    event_log.append(log_entry)
    rospy.loginfo(log_entry)
    write_to_file(log_entry)

def alert_callback(msg):
    time_now = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{time_now}] [ALERT] {msg.data}"
    
    alert_log.append(log_entry)
    rospy.loginfo(log_entry)
    write_to_file(log_entry)

def main():
    rospy.init_node('event_logger_node')

    rospy.Subscriber('/security_event', String, event_callback)
    rospy.Subscriber('/security_alert', String, alert_callback)

    rospy.loginfo("Event Logger Started")

    rospy.spin()

    # Close file safely when node shuts down
    log_file.close()

if __name__ == '__main__':
    main()
