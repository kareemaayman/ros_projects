std_msgs/Header header
float32[] query_x        # inlier points in previous frame
float32[] query_y
float32[] train_x        # inlier points in current frame
float32[] train_y
int32 inlier_count       # number of epipolar inliers
int32 total_matches      # total matches before RANSAC
float32 inlier_ratio     # inlier_count / total_matches
