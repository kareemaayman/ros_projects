cmake_minimum_required(VERSION 3.0.2)
project(multi_view_geometry)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  sensor_msgs
  message_generation
  actionlib_msgs
  actionlib
)

add_message_files(
  FILES
  KeypointArray.msg
  DescriptorArray.msg
  MatchArray.msg
  GeometricInliers.msg
  CameraMotion.msg
  SystemState.msg
)

add_service_files(
  FILES
  CheckGeometry.srv
)

add_action_files(
  FILES
  Report.action
)

generate_messages(
  DEPENDENCIES
  std_msgs
  actionlib_msgs
)

catkin_package(
  CATKIN_DEPENDS rospy std_msgs sensor_msgs message_runtime actionlib_msgs actionlib
)

catkin_install_python(PROGRAMS
  scripts/camera_node.py
  scripts/keypoint_node.py
  scripts/descriptor_node.py
  scripts/matching_node.py
  scripts/filtering_node.py
  scripts/geometry_node.py
  scripts/motion_node.py
  scripts/decision_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
