std_msgs/Header header
float32[] x              # keypoint x positions
float32[] y              # keypoint y positions
float32[] data           # flattened NxD descriptor matrix
int32 num_keypoints
int32 descriptor_size    # D (cols) — 32 for ORB

