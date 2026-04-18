# Importing required libraries
import pyautogui

class Config:
    SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

    CAM_WIDTH  = 640
    CAM_HEIGHT = 480

    # Calibration zone
    CALIB_RECT = {
        'x_min': 210,
        'y_min': 130,
        'x_max': 430,
        'y_max': 340
    }

    HAND = 'right'   # 'right' ya 'left'

    # Mouse smoothing: 0.1=fast  0.5=smooth
    # 0.4 = daily use sweet spot (0.55 bahut slow tha)
    SMOOTHING = 0.4

    # Finger extension: tip kitna upar hona chahiye pip se (normalized)
    # 0.02 = loose (thodi bend pe bhi detected)
    # 0.04 = strict (seedha upar hona chahiye) — ghost movement fix
    FINGER_EXTENSION = 0.035

    # Click threshold (degrees) — index bend angle
    CLICK_THRESHOLD = 145

    # Gesture stabilizer: kitne consecutive frames mein same gesture aaye
    # tab confirm ho. Jitter/flicker band karta hai.
    # 2 = fast response  |  4 = stable (recommended)
    GESTURE_CONFIRM_FRAMES = 2

    # Debounce (seconds)
    DEBOUNCE_LEFT   = 0.20
    DEBOUNCE_RIGHT  = 0.45
    DEBOUNCE_ACTION = 0.8

    # Scroll speed — higher = faster
    # SCROLL_THRESHOLD: cam pixels of movement before scroll fires
    # SCROLL_SENS: scroll amount multiplier
    SCROLL_THRESHOLD = 6     # pehle 12 tha — bahut slow tha
    SCROLL_SENS      = 5     # pehle 3 tha — badha diya
    # Thumb-middle pinch distance (normalized) for scroll gesture
    SCROLL_PINCH_THRESHOLD = 0.11

    # Volume
    VOLUME_STEP = 5

    OSK_TYPE = 'osk'
    DEBUG = True
