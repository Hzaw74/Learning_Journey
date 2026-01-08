
import dbus.mainloop.glib
from gi.repository import GLib
import logging
import evdev
import signal
import sys
import time
import os

from bt_hid import BluetoothHIDService
from input_manager import InputManager
from keymap import EVDEV_TO_HID, MODIFIER_MAP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Main")

class UniversalControlApp:
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.loop = GLib.MainLoop()
        
        self.bt_service = BluetoothHIDService()
        self.input_manager = InputManager(self.handle_input_event)
        
        self.mode = "LOCAL" # LOCAL or REMOTE
        self.pressed_keys = set()
        self.modifiers = 0
        
        # Mouse Accumulators
        self.mouse_dx = 0
        self.mouse_dy = 0
        self.mouse_wheel = 0
        self.mouse_buttons = 0
        self.last_mouse_sent = 0
        
        # Trackpad State
        self.last_abs_x = None
        self.last_abs_y = None
        self.touch_active = False
        
        # Sensitivity
        self.mouse_sensitivity = 0.8
        self.scroll_sensitivity = 1.0
        self.remainder_x = 0.0
        self.remainder_y = 0.0
        self.remainder_wheel = 0.0
        
    def start(self):
        logger.info("Starting Universal Control Clone...")
        
        # Register the Bluetooth Service
        self.bt_service.register()
        
        # Find devices
        self.input_manager.find_devices()
        
        # Start monitoring (Local mode initially)
        self.input_manager.start_monitoring()
        
        logger.info("Ready. Press F9 to toggle")
        
        try:
            self.loop.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        logger.info("Stopping...")
        self.input_manager.ungrab_mode()
        self.input_manager.stop_monitoring()
        self.loop.quit()

    def handle_input_event(self, dev, event):
        # Logic to detect Toggle
        if event.type == evdev.ecodes.EV_KEY:
            # Toggle: F9
            if event.code == evdev.ecodes.KEY_F9 and event.value == 1:
                self.toggle_mode()
                return

        if self.mode == "REMOTE":
            self.process_hid_event(event)

    def toggle_mode(self):
        if self.mode == "LOCAL":
            logger.info("Switching to REMOTE")
            self.mode = "REMOTE"
            self.input_manager.grab_mode()
        else:
            logger.info("Switching to LOCAL")
            self.mode = "LOCAL"
            self.input_manager.ungrab_mode()

    def process_hid_event(self, event):
        if event.type == evdev.ecodes.EV_KEY:
            # Trackpad Touch Support
            if event.code == evdev.ecodes.BTN_TOUCH:
                 self.touch_active = (event.value == 1)
                 # Don't return, allow other logic (though unlikely BTN_TOUCH maps to other things)
            
            # Check for Mouse Buttons
            if event.code in [evdev.ecodes.BTN_LEFT, evdev.ecodes.BTN_RIGHT, evdev.ecodes.BTN_MIDDLE]:
                mask = 0
                if event.code == evdev.ecodes.BTN_LEFT:
                    mask = 0x01
                elif event.code == evdev.ecodes.BTN_RIGHT:
                    mask = 0x02
                elif event.code == evdev.ecodes.BTN_MIDDLE:
                    mask = 0x04
                    
                if event.value == 1: # Pressed
                    self.mouse_buttons |= mask
                elif event.value == 0: # Released
                    self.mouse_buttons &= ~mask
                
                self.flush_mouse(force=True)
                return

            # Handle Modifiers
            if event.code in MODIFIER_MAP:
                if event.value == 1: # Pressed
                    self.modifiers |= MODIFIER_MAP[event.code]
                    self.send_keyboard_report()
                elif event.value == 0: # Released
                    self.modifiers &= ~MODIFIER_MAP[event.code]
                    self.send_keyboard_report()
            
            # Handle Normal Keys
            elif event.code in EVDEV_TO_HID:
                hid_code = EVDEV_TO_HID[event.code]
                if event.value == 1: # Pressed
                    self.pressed_keys.add(hid_code)
                    self.send_keyboard_report()
                elif event.value == 0: # Released
                    if hid_code in self.pressed_keys:
                        self.pressed_keys.remove(hid_code)
                        self.send_keyboard_report()
        
        elif event.type == evdev.ecodes.EV_REL:
             # Accumulate deltas
             if event.code == evdev.ecodes.REL_X:
                 self.mouse_dx += event.value
             elif event.code == evdev.ecodes.REL_Y:
                 self.mouse_dy += event.value
             elif event.code == evdev.ecodes.REL_WHEEL:
                 self.mouse_wheel += event.value
        
        elif event.type == evdev.ecodes.EV_ABS:
             # Handle Absolute devices (Trackpads)
             # Convert ABS delta to REL, BUT only if touching (avoids cursor jumps)
             
             if event.code == evdev.ecodes.ABS_X:
                 if self.last_abs_x is not None and self.touch_active:
                     self.mouse_dx += (event.value - self.last_abs_x)
                 self.last_abs_x = event.value
                 
             elif event.code == evdev.ecodes.ABS_Y:
                 if self.last_abs_y is not None and self.touch_active:
                     self.mouse_dy += (event.value - self.last_abs_y)
                 self.last_abs_y = event.value

        elif event.type == evdev.ecodes.EV_SYN:
             # Sync event: flush accumulated mouse data
             if event.code == evdev.ecodes.SYN_REPORT:
                 self.flush_mouse()

    def flush_mouse(self, force=False):
        # Rate Limiting: 60Hz (16ms) - Stable standard
        now = time.time()
        if not force and (now - self.last_mouse_sent < 0.016): 
            return # Accumulate more
    
        # Sensitivity Scaling (0.8x)
        target_x = (self.mouse_dx * self.mouse_sensitivity) + self.remainder_x
        target_y = (self.mouse_dy * self.mouse_sensitivity) + self.remainder_y
        target_w = (self.mouse_wheel * self.scroll_sensitivity) + self.remainder_wheel
        
        send_x = int(target_x)
        send_y = int(target_y)
        send_w = int(target_w)
        
        new_rem_x = target_x - send_x
        new_rem_y = target_y - send_y
        new_rem_w = target_w - send_w

        send = False
        if force:
            send = True
        elif send_x != 0 or send_y != 0 or send_w != 0:
            send = True
            
        if send:
             # Try to send. 
             # If successful, we clear accumulators.
             # If failing (buffer full), we KEEP the delta and try again next tick.
             # This prevents "Sticky Lag" (lost movement).
             if self.send_mouse_report(send_x, send_y, send_w, self.mouse_buttons):
                 self.mouse_dx = 0
                 self.mouse_dy = 0
                 self.mouse_wheel = 0
                 
                 self.remainder_x = new_rem_x
                 self.remainder_y = new_rem_y
                 self.remainder_wheel = new_rem_w
                 
                 self.last_mouse_sent = now

    def send_mouse_report(self, dx, dy, wheel, buttons=0):
        # ... logic ...
        # Clamp values to -127 to 127
        dx = max(-127, min(127, dx))
        dy = max(-127, min(127, dy))
        wheel = max(-127, min(127, wheel))
        
        dx_b = dx & 0xff
        dy_b = dy & 0xff
        wheel_b = wheel & 0xff
        
        # 0xA1 is HIDP_TRANS_DATA_INPUT
        report = bytearray([0xA1, 0x02, buttons, dx_b, dy_b, wheel_b])
        # IMPORTANT: Return True/False result to main loop
        return self.bt_service.send_report(report)

    def send_keyboard_report(self):
        # Report ID 1 (Keyboard)
        # Payload: [ID, Modifiers, Reserved, Key1, Key2, Key3, Key4, Key5, Key6]
        keys = list(self.pressed_keys)[:6] 
        keys += [0] * (6 - len(keys))
        
        # Report ID = 0x01
        # Modifiers = self.modifiers
        # Reserved = 0x00
        # Keys = 6 bytes
        report = bytearray([0xA1, 0x01, self.modifiers, 0x00] + keys)
        
        self.bt_service.send_report(report)

if __name__ == "__main__":
    app = UniversalControlApp()
    app.start()
