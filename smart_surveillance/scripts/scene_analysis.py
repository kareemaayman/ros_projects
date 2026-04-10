#!usr/bin/env python3
import rospy
from std_msgs.msg import String
class SceenAnalyzer:
	def __init__(self):
		rospy.init_node("scene_analyzer")
		
		self.danger_distance = rospy.get_param("~danger_distance", 2.0)  # 2 meters
		
		# store
		self.deta\cted_objects=[]
		self.depth_data={}
		
		rospy.Subscriber("/detected_objects", String, self.objects_callback)
		rospy.Subscriber("/object_depth", String, self.depth_callback)
		
		rospy.loginfo("SceneAnalyzer Node Started")
		
	def objects_callback(self, msg):
		self.detected_objects = msg.data.split(";")
		
		
	def depth_callback(self, msg):
		self.depth_data={}
		pairs=msg.data.split(";")
		
		for p in pairs:
			if ":" in p:
				name, dist = p.split(":")
				self.depth_data[name.strip()] = float(dist)
	def analyzw_scene(self):
		results = []
		for obj in self.detected_objects:
			parts = obj.strip().split()
			
			if len(parts) ==0:
				continue
			obj_name = parts[0]
			distance = self.depth_data.get(obj_name, None)
			
			if distance is None:
				continue
			if distance < self.danger_distance:
				status = "Danger"
			else:
				status="Safe"
			
			result = f"{obj_name} {distance:.2f} {status}"
			results.append(result)
		output = ";".join(results)
		self.pub.publish(output)
		
		rospy.loginfo(f"[Scene Analysis]: {output}")

if __name__ == "__main__":
	node = SceneAnalyzer()
	
	rate = rospy.Rate(5)
	
	while not rospy.is_shutdown():
		node.analyze_scene()
		rate.sleep()

