std_msgs/Header header
string state         # RELIABLE | UNRELIABLE | LOW_FEATURES
string reason        # human-readable explanation
int32 num_inliers    # geometric inliers in this frame
int32 num_matches    # total matches before geometry check
