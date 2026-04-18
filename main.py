# Importing required libraries
import cv2
# Importing required libraries
import time
from config import Config
from utils import norm_landmark_to_cam, map_to_screen
# Gesture detect + smooth karne ke liye
from hand_gestures import detect_gesture, GestureStabilizer
from mouse_controller import MouseController
from vision import HandVision
# Screen pe jo gesture k liya text show hota hai uska colors
MODE_COLORS = {
    'move':         (50,  210, 100),
    'scroll':       (50,  160, 255),
    'pause':        (160, 160, 160),
    'click':        (255, 140,  50),
    'right_click':  (180,  80, 255),
    'double_click': (255, 180,  80),
    'vol_up':       (50,  220, 180),
    'vol_down':     (50,  180, 220),
    'win_switch':   (255, 200,  50),
    'screenshot':   (50,  200, 255),
    'minimize':     (255, 140, 100),
    'idle':         (90,   90,  90),
}

GESTURE_LABELS = {
    'move':         'MOVE',
    'scroll':       'SCROLL',
    'pause':        'PAUSE',
    'click':        'CLICK',
    'right_click':  'RIGHT CLICK',
    'double_click': 'DOUBLE CLICK',
    'vol_up':       'VOL UP',
    'vol_down':     'VOL DOWN',
    'win_switch':   'WIN SWITCH',
    'screenshot':   'SCREENSHOT',
    'minimize':     'MINIMIZE',
    'idle':         'idle',
}

# One-shot:  Ye gestures sirf ek baar run honge (Screenshot.volume etc)
ONE_SHOT = {
    'vol_up', 'vol_down', 'win_switch',
    'screenshot', 'double_click', 'minimize', 'right_click'
}


# Function: draw_hud  ->Screen pe UI current gesture draw karta
def draw_hud(frame, mode, fps, clicking, angle=None, status_text=""):
    # Checking condition
    display = 'click' if clicking else mode
    color = MODE_COLORS.get(display, (90, 90, 90))
    label = GESTURE_LABELS.get(display, display.upper())

    cv2.rectangle(frame, (0, 0), (Config.CAM_WIDTH, 44), (25, 25, 25), -1)
    cv2.putText(frame, f"FPS {fps}",
                (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
    cv2.putText(frame, label,
                (90, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
# Checking condition
    if status_text:
        cv2.putText(  # Text screen pe likhne ke liye
            frame, status_text,
            (8, Config.CAM_HEIGHT - 8),
            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (80, 220, 220), 1)
    cv2.putText(frame, "Q=quit  G=guide  K=keyboard",
                (Config.CAM_WIDTH - 230, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (100, 100, 100), 1)


# Function: draw_zone ->Screen pe ek rectangle draw karta hai
def draw_zone(frame):
    r = Config.CALIB_RECT
    cv2.rectangle(frame,
                  (r['x_min'], r['y_min']),
                  (r['x_max'], r['y_max']),
                  (60, 200, 100), 1)
    cv2.putText(frame, "move zone",
                (r['x_min'], r['y_min'] - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (60, 200, 100), 1)


# Function: draw_guide ->  Screen pe instructions show karta
def draw_guide(frame):
    lines = [
        "index            = move",
        "thm + mid        = scroll",
        "idx + mid        = left click (type)",
        "idx+mid+rng  = vol up",
        "all 4 up         = vol down",
        "mid + rng + pnk  = minimize",
        "mid + rng        = double click",
        "thm + idx        = alt+tab",
        "pnk + thm        = full screenshot",
        "pnk only         = right click",
        "fist             = pause",
    ]
    bx, by = 8, 54
    cv2.rectangle(frame, (bx-2, by-14),
                  (bx+208, by + len(lines)*16 + 6),
                  (22, 22, 22), -1)
    for i, ln in enumerate(lines):
        cv2.putText(frame, ln, (bx, by + i*16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (190, 190, 190), 1)


# Function: main -> performs specific task
def main():
    try:
        vision = HandVision()  # Camera start + hand detection ready
    except RuntimeError as e:
        print(e)
# Returning result
        return

    mouse = MouseController()  # Mouse control ready
    stabilizer = GestureStabilizer()  # Gesture smooth karega (flickering avoid)
    # variables tracking ke liye
    p_time = 0
    scroll_active = False
    show_guide = True
    prev_gesture = 'idle'
    prev_click_raw = False

    print("\n" + "="*50)
    print("  Gesture Mouse v2  —  Q=quit  G=guide  K=keyboard")
    print("="*50 + "\n")

    try:
        while True:  # Har frame pe ye loop chalega
            frame, results = vision.get_frame()  # Camera se image + hand detection result
# Checking condition
            if frame is None:
                break

            clicking = False
            angle = None

            draw_zone(frame)
# Checking condition
            if show_guide:
                draw_guide(frame)

# Checking condition
            if results and results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]

# Checking condition
                if Config.DEBUG:
                    vision.draw_hand(frame, hand)

                # Raw gesture → smooth gesture
                raw = detect_gesture(hand)
                gesture = stabilizer.update(raw)
                # Index finger ka position nikala
                lm_index = hand.landmark[8]
                ix, iy = norm_landmark_to_cam(lm_index)

                # ── CLICK (raw edge detect for reliable typing) ───
# Checking condition
                if raw == 'click':
                    # Checking condition
                    if scroll_active:
                        mouse.stop_scroll()
                        scroll_active = False
# Checking condition
                    if not prev_click_raw:
                        clicking = mouse.left_click()
                    prev_click_raw = True
                    gesture = 'click'

                # ── PAUSE ─────────────────────────────────────────
# Checking condition
                elif gesture == 'pause':
                    # Checking condition
                    if scroll_active:
                        mouse.stop_scroll()
                        scroll_active = False
                    mouse.reset_click_state()

                # ── MOVE ──────────────────────────────────────────
# Checking condition
                elif gesture == 'move':
                    # Checking condition
                    if scroll_active:
                        mouse.stop_scroll()
                        scroll_active = False
                    mouse.reset_click_state()
                    # Camera → screen mapping
                    sx, sy = map_to_screen(ix, iy)
                    mouse.move(sx, sy)

                # ── SCROLL + CLICK ────────────────────────────────
# Checking condition
                elif gesture == 'scroll':
                    lm_thumb = hand.landmark[4]
                    lm_mid = hand.landmark[12]
                    _, ty = norm_landmark_to_cam(lm_thumb)
                    _, my = norm_landmark_to_cam(lm_mid)
                    scroll_y = (ty + my) / 2.0
# Checking condition
                    if not scroll_active:
                        mouse.start_scroll(scroll_y)
                        scroll_active = True
                    else:
                        mouse.update_scroll(scroll_y)

                # ── ONE-SHOT ACTIONS ──────────────────────────────
# Checking condition
                elif gesture in ONE_SHOT:
                    # Checking condition
                    if scroll_active:
                        mouse.stop_scroll()
                        scroll_active = False
                    mouse.reset_click_state()

# Checking condition
                    if gesture != prev_gesture:   # sirf pehle frame pe
                        # Checking condition
                        if gesture == 'vol_up':
                            mouse.volume_up()
# Checking condition
                        elif gesture == 'vol_down':
                            mouse.volume_down()
# Checking condition
                        elif gesture == 'win_switch':
                            mouse.window_switch()
# Checking condition
                        elif gesture == 'screenshot':
                            mouse.screenshot()
# Checking condition
                        elif gesture == 'double_click':
                            mouse.double_click()
# Checking condition
                        elif gesture == 'minimize':
                            mouse.minimize_window()
# Checking condition
                        elif gesture == 'right_click':
                            mouse.right_click()
# Checking condition
                        elif gesture == 'click':
                            clicking = mouse.left_click()

                # ── IDLE ──────────────────────────────────────────
                else:
                    # Checking condition
                    if scroll_active:
                        mouse.stop_scroll()
                        scroll_active = False
                    mouse.reset_click_state()

# Checking condition
                if raw != 'click':
                    prev_click_raw = False

                prev_gesture = gesture

            else:
                # Hand nahi dikh raha
                stabilizer.reset()
# Checking condition
                if scroll_active:
                    mouse.stop_scroll()
                    scroll_active = False
                mouse.reset_click_state()
                prev_gesture = 'idle'
                prev_click_raw = False
                gesture = 'idle'

            now = time.time()
# Checking condition
            # Kitni fast program chal raha hai
            fps = int(1 / (now - p_time)) if p_time > 0 else 0
            p_time = now

# Checking condition
            draw_hud(frame, gesture if results and results.multi_hand_landmarks else 'idle',
                     fps, clicking, angle, mouse.get_status_text())
            cv2.imshow("Gesture Mouse v2", frame)

            key = cv2.waitKey(1) & 0xFF
# Checking condition
            if key == ord('q'):
                break
# Checking condition
            elif key == ord('g'):
                show_guide = not show_guide
# Checking condition
            elif key == ord('k'):
                mouse.toggle_keyboard()

    finally:
        vision.release()
        print("Gesture Mouse band ho gaya.")


# Checking condition
if __name__ == "__main__":
    main()
