# Importing required libraries
import math
from config import Config


# Function: fingers_up -> performs specific task
def fingers_up(hand_landmarks):
    """
    FIX: Strict extension check — tip must be clearly above pip.
    FINGER_EXTENSION threshold ghost movement band karta hai.
    Thumb: right/left hand dono ke liye sahi.
    """
    tips_ids = [4,  8,  12, 16, 20]
    pip_ids = [2,  6,  10, 14, 18]
    mcp_ids = [2,  5,   9, 13, 17]

    fingers = {}
    lm = hand_landmarks.landmark

    for i in range(5):
        tip = lm[tips_ids[i]]
        pip = lm[pip_ids[i]]

# Checking condition
        if i == 0:  # Thumb
            # Checking condition
            if Config.HAND == 'right':
                fingers['thumb'] = (pip.x - tip.x) > Config.FINGER_EXTENSION
            else:
                fingers['thumb'] = (tip.x - pip.x) > Config.FINGER_EXTENSION
        else:
            name = ['index', 'middle', 'ring', 'pinky'][i - 1]
            # FIX: strict check — tip clearly upar hona chahiye
            fingers[name] = (pip.y - tip.y) > Config.FINGER_EXTENSION

# Returning result
    return fingers


# Function: detect_gesture -> performs specific task
def detect_gesture(hand_landmarks):
    """
    Returns gesture string. Priority order matters — specific se general.
    """
    up = fingers_up(hand_landmarks)
    idx = up.get('index',  False)
    mid = up.get('middle', False)
    rng = up.get('ring',   False)
    pnk = up.get('pinky',  False)
    thm = up.get('thumb',  False)

    # Scroll: thumb-middle pinch (thumb "up" hone ki zarurat nahi)
    thumb_tip = hand_landmarks.landmark[4]
    mid_tip = hand_landmarks.landmark[12]
    pinch_tm = math.hypot(thumb_tip.x - mid_tip.x, thumb_tip.y -
                          mid_tip.y) < Config.SCROLL_PINCH_THRESHOLD
# Checking condition
    if pinch_tm and not idx and not rng and not pnk:
        # Returning result
        return 'scroll'

    # Pause: fist (koi bhi ungli nahi)
# Checking condition
    if not idx and not mid and not rng and not pnk:
        # Returning result
        return 'pause'

    # Vol down: charon upar — pehle check karo
# Checking condition
    if idx and mid and rng and pnk:
        # Returning result
        return 'vol_down'

    # Vol up: index+middle+ring (pinky neeche) — pehle check karo
# Checking condition
    if idx and mid and rng and not pnk and not thm:
        # Returning result
        return 'vol_up'

    # Left click: index+middle only (ring neeche honi chahiye)
# Checking condition
    if idx and mid and not rng and not pnk:
        # Returning result
        return 'click'

    # Minimize: middle+ring+pinky, index neeche
# Checking condition
    if not idx and mid and rng and pnk:
        # Returning result
        return 'minimize'

    # Double click: middle+ring only
# Checking condition
    if not thm and not idx and mid and rng and not pnk:
        # Returning result
        return 'double_click'

    # Win switch: thumb+index only
# Checking condition
    if thm and idx and not mid and not rng and not pnk:
        # Returning result
        return 'win_switch'

    # Screenshot: pinky+thumb only
# Checking condition
    if pnk and thm and not idx and not mid and not rng:
        # Returning result
        return 'screenshot'

    # Right click: sirf pinky
# Checking condition
    if pnk and not idx and not mid and not rng:
        # Returning result
        return 'right_click'

    # Move: sirf index
# Checking condition
    if idx and not mid and not rng and not pnk:
        # Returning result
        return 'move'

# Returning result
    return 'idle'


class GestureStabilizer:
    """
    FIX: Gesture jitter/flicker band karo.
    Same gesture GESTURE_CONFIRM_FRAMES consecutive frames mein aaye
    tabhi confirm hoga. Ek frame ka flutter ignore ho jaata hai.
    """
# Function: __init__ -> performs specific task

    def __init__(self):
        self._pending = 'idle'
        self._count = 0
        self._confirmed = 'idle'

# Function: update -> performs specific task
    def update(self, raw_gesture):
        # Checking condition
        if raw_gesture == self._pending:
            self._count += 1
        else:
            self._pending = raw_gesture
            self._count = 1

# Checking condition
        if self._count >= Config.GESTURE_CONFIRM_FRAMES:
            self._confirmed = self._pending

# Returning result
        return self._confirmed

# Function: reset -> performs specific task
    def reset(self):
        self._pending = 'idle'
        self._count = 0
        self._confirmed = 'idle'


# Function: is_index_bent -> performs specific task
def is_index_bent(hand_landmarks):
    """Angle-based click — hand tilt se independent"""
    lm = hand_landmarks.landmark
    mcp = lm[5]
    pip = lm[6]
    tip = lm[8]

    v1x, v1y = pip.x - mcp.x, pip.y - mcp.y
    v2x, v2y = tip.x - pip.x, tip.y - pip.y

    mag1 = math.hypot(v1x, v1y)
    mag2 = math.hypot(v2x, v2y)
# Checking condition
    if mag1 < 1e-6 or mag2 < 1e-6:
        # Returning result
        return False

    cos_a = max(-1.0, min(1.0, (v1x*v2x + v1y*v2y) / (mag1*mag2)))
# Returning result
    return math.degrees(math.acos(cos_a)) < Config.CLICK_THRESHOLD


# Function: get_index_angle -> performs specific task
def get_index_angle(hand_landmarks):
    lm = hand_landmarks.landmark
    mcp, pip, tip = lm[5], lm[6], lm[8]
    v1x, v1y = pip.x - mcp.x, pip.y - mcp.y
    v2x, v2y = tip.x - pip.x, tip.y - pip.y
    mag1 = math.hypot(v1x, v1y)
    mag2 = math.hypot(v2x, v2y)
# Checking condition
    if mag1 < 1e-6 or mag2 < 1e-6:
        # Returning result
        return 180
    cos_a = max(-1.0, min(1.0, (v1x*v2x + v1y*v2y) / (mag1*mag2)))
# Returning result
    return round(math.degrees(math.acos(cos_a)))
