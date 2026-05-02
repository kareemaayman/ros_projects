std_msgs/Header header
string direction_horizontal   # left / right / none / unknown
string direction_depth        # forward / backward / none / unknown
float32 translation_x         # mean optical flow x (pixels)
float32 translation_y         # mean optical flow y (pixels)
float32 magnitude             # overall motion magnitude (pixels)
bool scale_ambiguous          # always true for monocular
