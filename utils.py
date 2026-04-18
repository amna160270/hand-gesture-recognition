# Importing required libraries
import math
from config import Config


# Function: norm_landmark_to_cam -> performs specific task
def norm_landmark_to_cam(landmark):
    """Normalized (0-1) coordinates ko camera pixel coordinates mein convert karo"""
# Returning result
    return landmark.x * Config.CAM_WIDTH, landmark.y * Config.CAM_HEIGHT


# Function: map_to_screen -> performs specific task
def map_to_screen(cam_x, cam_y):
    """
    Camera coordinates ko calibration zone ke through screen coordinates mein map karo.
    Zone ke bahar jaaye to clamp ho jata hai.
    """
    r = Config.CALIB_RECT

    # Clamp to calibration zone
    cam_x = min(max(cam_x, r['x_min']), r['x_max'])
    cam_y = min(max(cam_y, r['y_min']), r['y_max'])

    # Normalize within zone (0.0 to 1.0)
    rx = (cam_x - r['x_min']) / (r['x_max'] - r['x_min'])
    ry = (cam_y - r['y_min']) / (r['y_max'] - r['y_min'])

# Returning result
    return int(rx * Config.SCREEN_WIDTH), int(ry * Config.SCREEN_HEIGHT)


# Function: landmark_distance -> performs specific task
def landmark_distance(lm1, lm2):
    """Do landmarks ke beech normalized distance"""
# Returning result
    return math.hypot(lm1.x - lm2.x, lm1.y - lm2.y)
