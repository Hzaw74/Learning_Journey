
import evdev
import logging
from gi.repository import GLib

logger = logging.getLogger("InputManager")

class InputManager:
    def __init__(self, callback):
        self.devices = []
        self.grabbed_devices = {}
        self.callback = callback # Function to call with (device, event)

    def find_devices(self):
        """Finds available keyboard and mouse devices."""
        try:
            paths = evdev.list_devices()
        except Exception:
            # Fallback or permission error handling
            paths = []

        devices = [evdev.InputDevice(path) for path in paths]
        keyboards = []
        mice = []

        for dev in devices:
            cap = dev.capabilities()
            if evdev.ecodes.EV_KEY in cap:
                if evdev.ecodes.KEY_A in cap[evdev.ecodes.EV_KEY]:
                    keyboards.append(dev)
                elif evdev.ecodes.BTN_MOUSE in cap[evdev.ecodes.EV_KEY]:
                    mice.append(dev)
            
        logger.info(f"Found Keyboards: {[d.name for d in keyboards]}")
        logger.info(f"Found Mice: {[d.name for d in mice]}")
        
        self.devices = keyboards + mice
        return self.devices

    def start_monitoring(self):
        """Starts watching devices for events."""
        for dev in self.devices:
            if dev.fd not in self.grabbed_devices:
                self.grabbed_devices[dev.fd] = dev
                GLib.io_add_watch(dev.fd, GLib.IO_IN, self.on_device_event)
                logger.info(f"Started monitoring {dev.name}")

    def stop_monitoring(self):
        """Stops watching all devices."""
        # We just clear the map. The watches will die when they next fire and see missing map entry.
        # But to be cleaner we could return False immediately if we could? 
        # For now, relying on map check is okay, but we must ensure we don't 'resurrect' them if we strictly restart.
        # Ideally we track source IDs. But clearing map works if we assume we stop fully.
        self.grabbed_devices.clear()

    def grab_mode(self):
        """Exclusively grabs the devices."""
        for dev in list(self.grabbed_devices.values()):
            try:
                dev.grab()
                logger.info(f"Grabbed {dev.name}")
            except Exception as e:
                # If already grabbed, it might fail or pass
                pass

    def ungrab_mode(self):
        """Releases exclusive grab (but keeps monitoring)."""
        for dev in list(self.grabbed_devices.values()):
            try:
                dev.ungrab()
                logger.info(f"Ungrabbed {dev.name}")
            except Exception as e:
                pass

    def on_device_event(self, fd, condition):
        dev = self.grabbed_devices.get(fd)
        if not dev:
            return False # Stop watching if device is gone
        
        try:
            for event in dev.read():
                self.callback(dev, event)
        except Exception as e:
            logger.error(f"Error reading device {dev.name}: {e}")
            # return False -> CRITICAL FIX: Do NOT stop monitoring! 
            # If we stop, the user stays grabbed forever!
            return True 
            
        return True # Continue watching

