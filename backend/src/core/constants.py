"""
Constants for HDR Blender backend.
"""

# EV (Exposure Value) calculations
EV_STEP_SIZE = 0.3  # Steps between bracketed exposures
EV_TOLERANCE = 0.3  # Tolerance for EV matching

# Image processing constants
MIN_FEATURE_MATCHES = 10  # Minimum matches for alignment
MAX_SCALE_PYRAMID = 6  # Laplacian pyramid levels

# Mertens algorithm parameters
MERTENS_CONTRAST_WEIGHT = 1.0
MERTENS_SATURATION_WEIGHT = 1.0
MERTENS_EXPOSURE_WEIGHT = 0.0

# Output naming
ANGLE_OUTPUT_FORMAT = "angle_{:03d}.{}"

# Processing defaults
DEFAULT_QUALITY_LEVEL = 0.01  # ORB quality threshold
DEFAULT_NMS_THRESHOLD = 0.04  # Non-maximum suppression
