# Importing required libraries for camera usage
import cv2
# Importing required libraries for hand detection
import mediapipe as mp
from config import Config

mp_hands = mp.solutions.hands  # camera se haath detect karega
mp_drawing = mp.solutions.drawing_utils  # draw hand points on screen
# points ka color, thickness, shape
mp_drawing_styles = mp.solutions.drawing_styles


class HandVision:
    # Function: __init__ ->  object banega → ye code run hoga
    def __init__(self):
        # Starting camera 0 = default webcam,Camera ON ho gaya
        self.cap = cv2.VideoCapture(0)

        # Camera open hua ya nahi check karo
# Checking condition
        if not self.cap.isOpened():
            raise RuntimeError(  # Agar camera open nahi hota to ye message show hoga
                "Camera nahi khul raha!\n"
                "Check karo:\n"
                "  1. Webcam connected hai?\n"
                "  2. Koi aur app camera use to nahi kar raha?\n"
                # Starting camera
                "  3. Camera index 0 correct hai? (try VideoCapture(1))"
            )

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  Config.CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAM_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # MediaPipe hands setup
# Initializing hand detection
        self.hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
            model_complexity=0   # 0 = fast (lite), 1 = accurate (full)
        )

        self._failed_frames = 0

# Function: get_frame -> performs specific task
    def get_frame(self):
        """
        Frame read karo aur hand detection chalaao.
        Returns: (frame, results) ya (None, None) agar camera fail ho jaye.
        """
        ret, frame = self.cap.read()

# Checking condition
        if not ret:
            self._failed_frames += 1
# Checking condition
            if self._failed_frames > 10:
                print("Camera se frame nahi aa raha - check karo connection")
# Returning result
                return None, None
# Returning result
            return None, None

        self._failed_frames = 0

        # Mirror flip (selfie view - natural lagta hai)
        frame = cv2.flip(frame, 1)

        # BGR to RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        rgb.flags.writeable = True

# Returning result
        return frame, results

# Function: draw_hand -> performs specific task
    def draw_hand(self, frame, hand_landmarks):
        """Hand ke joints aur connections draw karo"""
        mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style()
        )

# Function: draw_calibration_zone -> performs specific task
    def draw_calibration_zone(self, frame):
        """Calibration zone ka box frame pe draw karo"""
        r = Config.CALIB_RECT
        cv2.rectangle(
            frame,
            (r['x_min'], r['y_min']),
            (r['x_max'], r['y_max']),
            (0, 255, 100), 1
        )
        cv2.putText(
            frame, "Move zone",
            (r['x_min'], r['y_min'] - 6),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 100), 1
        )

# Function: release -> performs specific task
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
