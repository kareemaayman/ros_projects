std_msgs/Header header
int32[] query_idx      # index in previous frame descriptors
int32[] train_idx      # index in current frame descriptors
float32[] query_x      # pixel x in previous frame
float32[] query_y      # pixel y in previous frame
float32[] train_x      # pixel x in current frame
float32[] train_y      # pixel y in current frame
float32[] distance     # descriptor distance (Hamming for ORB)
int32 count

