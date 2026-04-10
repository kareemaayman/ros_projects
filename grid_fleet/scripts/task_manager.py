#!/usr/bin/env python3
import rospy
from std_srvs.srv import Trigger, TriggerResponse
from random import randint


num  = 10
tasks = []
for _ in range(num):
    pickup = (randint(0,7), randint(0,7))
    dropoff = (randint(0,7), randint(0,7))
    tasks.append({'pickup': pickup, 'dropoff': dropoff})

current_index = 0
completed_tasks = 0

rospy.init_node('task_manager_proc')

rospy.loginfo("Task Manager ready with {} tasks.".format(num))


def handle_request(req):
    global current_index, completed_tasks
    if current_index < len(tasks):
        task = tasks[current_index]
        current_index += 1
        completed_tasks += 1

        rospy.loginfo("Assigned task {}: Pickup {} -> Drop-off {}".format(
            current_index, task['pickup'], task['dropoff']))

        # Message: pickup_x pickup_y dropoff_x dropoff_y
        return TriggerResponse(
            success=True,
            message="{} {} {} {}".format(
                task['pickup'][0], task['pickup'][1],
                task['dropoff'][0], task['dropoff'][1]
            )
        )
    else:
        return TriggerResponse(
            success=False,
            message="No more tasks!"
        )


service = rospy.Service('/request_task', Trigger, handle_request)
rospy.spin()

