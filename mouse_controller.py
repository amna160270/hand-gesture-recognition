# Importing required libraries
import pyautogui
# Importing required libraries
import subprocess
# Importing required libraries
import time
# Importing required libraries
import os
# Importing required libraries
import ctypes
from config import Config

pyautogui.FAILSAFE = False  # Screen corner pe mouse jaaye to program band na ho
pyautogui.PAUSE = 0  # Har action ke baad delay = 0,Speed fast ho gayi

INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("union", INPUT_UNION)]


class MouseController:
    # Function: __init__ -> performs specific task
    def __init__(self):
        self.smoothed_x = Config.SCREEN_WIDTH // 2
        self.smoothed_y = Config.SCREEN_HEIGHT // 2

        self.last_click = {'left': 0, 'right': 0}
        self.last_action = {}
        self.scroll_ref_y = None
        self.scroll_ref_set = False

        # FIX: click one-shot state — click sirf tab hoga jab
        # pehle NOT bent tha aur ab bent hua (rising edge)
        self._click_was_bent = False
        self.last_status = ""

    # ── Movement ──────────────────────────────────────────────────────────
# Function: move -> performs specific task
    def move(self, x, y):
        s = Config.SMOOTHING
        self.smoothed_x = self.smoothed_x * s + x * (1 - s)
        self.smoothed_y = self.smoothed_y * s + y * (1 - s)
        pyautogui.moveTo(int(self.smoothed_x), int(
            self.smoothed_y), duration=0)

    # ── Left click — RISING EDGE only (bent nahi tha → bent hua = click) ──
# Function: process_click -> performs specific task
    def process_click(self, is_bent):
        """
        FIX: click ek baar fire hoga jab finger pehli baar bend ho.
        Finger bent raho = koi repeat nahi.
        Seedha karo phir dobara jhukao = next click.
        """
        fired = False
# Checking condition
        if is_bent and not self._click_was_bent:
            now = time.time()
# Checking condition
            if now - self.last_click['left'] >= Config.DEBOUNCE_LEFT:
                pyautogui.click()
                self.last_click['left'] = now
                fired = True
        self._click_was_bent = is_bent
# Returning result
        return fired

# Function: reset_click_state -> performs specific task
    def reset_click_state(self):
        self._click_was_bent = False

# Function: left_click -> performs specific task
    def left_click(self):
        now = time.time()
# Checking condition
        if now - self.last_click['left'] < Config.DEBOUNCE_LEFT:
            # Returning result
            return False
        try:
            # Cursor ko exact current position pe force set karo.
            x = int(self.smoothed_x)
            y = int(self.smoothed_y)
            ctypes.windll.user32.SetCursorPos(x, y)

            # Native SendInput click: OSK/TabTip par zyada reliable.
            extra = ctypes.c_ulong(0)
            down = INPUT(type=INPUT_MOUSE)
            down.union.mi = MOUSEINPUT(
                0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
            up = INPUT(type=INPUT_MOUSE)
            up.union.mi = MOUSEINPUT(
                0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
            ctypes.windll.user32.SendInput(
                1, ctypes.byref(down), ctypes.sizeof(INPUT))
            time.sleep(0.05)
            ctypes.windll.user32.SendInput(
                1, ctypes.byref(up), ctypes.sizeof(INPUT))
            self.last_status = "CLICK"
        except Exception:
            pyautogui.mouseDown()
            time.sleep(0.05)
            pyautogui.mouseUp()
            self.last_status = "CLICK"
        self.last_click['left'] = now
# Returning result
        return True

    # ── Right click ────────────────────────────────────────────────────────
# Function: right_click -> performs specific task
    def right_click(self):
        now = time.time()
# Checking condition
        if now - self.last_click['right'] < Config.DEBOUNCE_RIGHT:
            # Returning result
            return
        pyautogui.click(button='right')
        self.last_click['right'] = now

    # ── Double click ───────────────────────────────────────────────────────
# Function: double_click -> performs specific task
    def double_click(self):
        # Checking condition
        if not self._can_fire('double_click'):
            # Returning result
            return
        pyautogui.doubleClick()

    # ── Scroll ─────────────────────────────────────────────────────────────
# Function: start_scroll -> performs specific task
    def start_scroll(self, cam_y):
        """
        FIX: reference sirf tab set karo jab scroll mode mein enter ho.
        Transition jump avoid karta hai.
        """
        self.scroll_ref_y = cam_y
        self.scroll_ref_set = True

# Function: update_scroll -> performs specific task
    def update_scroll(self, cam_y):
        # Checking condition
        if not self.scroll_ref_set:
            self.start_scroll(cam_y)
# Returning result
            return

        delta = cam_y - self.scroll_ref_y

# Checking condition
        if abs(delta) > Config.SCROLL_THRESHOLD:
            # delta positive = haath neeche gaya = scroll down (negative scroll)
            amount = -int(delta * Config.SCROLL_SENS / Config.SCROLL_THRESHOLD)
            pyautogui.scroll(amount)
            # FIX: partial update — reference ko mid-point pe shift karo
            # Hard reset karne se next frame pe jump aata tha
            self.scroll_ref_y += delta * 0.6

# Function: stop_scroll -> performs specific task
    def stop_scroll(self):
        self.scroll_ref_y = None
        self.scroll_ref_set = False

    # ── Action debounce ───────────────────────────────────────────────────
# Function: _can_fire -> performs specific task
    def _can_fire(self, name):
        now = time.time()
# Checking condition
        if now - self.last_action.get(name, 0) > Config.DEBOUNCE_ACTION:
            self.last_action[name] = now
# Returning result
            return True
# Returning result
        return False

    # ── Volume ────────────────────────────────────────────────────────────
# Function: volume_up -> performs specific task
    def volume_up(self):
        # Checking condition
        if not self._can_fire('vol_up'):
            # Returning result
            return
        for _ in range(Config.VOLUME_STEP):
            pyautogui.press('volumeup')

# Function: volume_down -> performs specific task
    def volume_down(self):
        # Checking condition
        if not self._can_fire('vol_down'):
            # Returning result
            return
        for _ in range(Config.VOLUME_STEP):
            pyautogui.press('volumedown')

    # ── System actions ────────────────────────────────────────────────────
# Function: window_switch -> performs specific task
    def window_switch(self):
        # Checking condition
        if not self._can_fire('win_switch'):
            # Returning result
            return
        pyautogui.hotkey('alt', 'tab')

# Function: screenshot -> performs specific task
    def screenshot(self):
        # Checking condition
        if not self._can_fire('screenshot'):
            # Returning result
            return
        try:
            save_dir = os.path.join(os.getcwd(), 'screenshots')
            os.makedirs(save_dir, exist_ok=True)
            filename = time.strftime("shot_%Y%m%d_%H%M%S.png")
            save_path = os.path.join(save_dir, filename)
            shot = pyautogui.screenshot()
            shot.save(save_path)
            self.last_status = f"SCREENSHOT saved: {filename}"
        except Exception as e:
            self.last_status = f"SCREENSHOT error: {e}"

# Function: get_status_text -> performs specific task
    def get_status_text(self):
        # Returning result
        return self.last_status

# Function: minimize_window -> performs specific task
    def minimize_window(self):
        # Checking condition
        if not self._can_fire('minimize'):
            # Returning result
            return
        pyautogui.hotkey('win', 'd')

    # ── On-Screen Keyboard ────────────────────────────────────────────────
# Function: toggle_keyboard -> performs specific task
    def toggle_keyboard(self):
        # Checking condition
        if not self._can_fire('keyboard'):
            # Returning result
            return
        try:
            # Checking condition
            if Config.OSK_TYPE == 'tabtip':
                tabtip = r'C:\Program Files\Common Files\microsoft shared\ink\TabTip.exe'
# Checking condition
                if os.path.exists(tabtip):
                    subprocess.Popen([tabtip])
# Returning result
                    return
            subprocess.Popen(['osk.exe'], shell=True,
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        except Exception as e:
            print(f"Keyboard error: {e}")
