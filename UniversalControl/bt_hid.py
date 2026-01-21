
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import os
import socket
import logging
import sys
import dbus.exceptions
import threading
import queue
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BluetoothHID")

class BTProfile(dbus.service.Object):
    def __init__(self, bus, path, service):
        dbus.service.Object.__init__(self, bus, path)
        self.service = service
        self.fd = -1

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Release(self):
        logger.info("Release")
        GLib.MainLoop().quit()

    @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
    def Cancel(self):
        logger.info("Cancel")

    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, fd, properties):
        self.fd = fd.take()
        logger.info(f"NewConnection({path}, {self.fd})")
        try:
            # For BlueZ 5 HID, the NewConnection fd is usually the Control channel implementation? 
            # Or L2CAP. We will treat it as the communication socket.
            # In some implementations, BlueZ might handle the sockets differently. 
            sock = socket.fromfd(self.fd, socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
            sock.setblocking(False)
            self.service.connect_socket(sock)
        except Exception as e:
            logger.error(f"Failed to create socket: {e}")

    @dbus.service.method("org.bluez.Profile1", in_signature="o", out_signature="")
    def RequestDisconnection(self, path):
        logger.info(f"RequestDisconnection({path})")
        self.service.disconnect_socket()

class BluetoothHIDService:
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.path = "/org/bluez/bthid_profile"
        self.profile = BTProfile(self.bus, self.path, self)
        self.sock = None

        # Descriptors
        # Keyboard (Boot) + Mouse
        self.hid_descriptor = [
            0x05, 0x01, 0x09, 0x06, 0xa1, 0x01, 0x85, 0x01, 0x05, 0x07, 0x19, 0xe0, 0x29, 0xe7, 0x15, 0x00, 
            0x25, 0x01, 0x75, 0x01, 0x95, 0x08, 0x81, 0x02, 0x95, 0x01, 0x75, 0x08, 0x81, 0x01, 0x95, 0x05, 
            0x75, 0x01, 0x05, 0x08, 0x19, 0x01, 0x29, 0x05, 0x91, 0x02, 0x95, 0x01, 0x75, 0x03, 0x91, 0x01, 
            0x95, 0x06, 0x75, 0x08, 0x15, 0x00, 0x25, 0x65, 0x05, 0x07, 0x19, 0x00, 0x29, 0x65, 0x81, 0x00, 
            0xc0, 0x05, 0x01, 0x09, 0x02, 0xa1, 0x01, 0x85, 0x02, 0x09, 0x01, 0xa1, 0x00, 0x05, 0x09, 0x19, 
            0x01, 0x29, 0x03, 0x15, 0x00, 0x25, 0x01, 0x95, 0x03, 0x75, 0x01, 0x81, 0x02, 0x95, 0x01, 0x75, 
            0x05, 0x81, 0x03, 0x05, 0x01, 0x09, 0x30, 0x09, 0x31, 0x15, 0x81, 0x25, 0x7f, 0x75, 0x08, 0x95, 
            0x02, 0x81, 0x06, 0x09, 0x38, 0x15, 0x81, 0x25, 0x7f, 0x75, 0x08, 0x95, 0x01, 0x81, 0x06, 0xc0, 
            0xc0
        ]
        
        # Large buffer with TTL dropping (Latency Killer)
        self.send_queue = queue.Queue(maxsize=100)
        self.sdp_xml = self.create_sdp_record()

    def create_sdp_record(self):
        desc_str = "".join([f"{b:02X}" for b in self.hid_descriptor])
        
        # Standard HID SDP Record (Keyboard + Mouse)
        return f"""
<record>
    <attribute id="0x0001">
        <sequence>
            <uuid value="0x1124"/> <!-- Human Interface Device Service -->
        </sequence>
    </attribute>
    <attribute id="0x0004">
        <sequence>
            <sequence>
                <uuid value="0x0100"/> <!-- L2CAP -->
                <uint16 value="0x0011"/> <!-- PSM: HID Control -->
            </sequence>
            <sequence>
                <uuid value="0x0011"/> <!-- HID Protocol -->
                <uint16 value="0x0111"/> <!-- Version 1.11 -->
            </sequence>
        </sequence>
    </attribute>
    <attribute id="0x0005">
        <sequence>
            <uuid value="0x1002"/> <!-- Browse Group: PublicBrowseRoot -->
        </sequence>
    </attribute>
    <attribute id="0x0006">
        <sequence>
            <uint16 value="0x656e"/> <!-- en -->
            <uint16 value="0x006a"/> <!-- UTF-8 -->
            <uint16 value="0x0100"/> <!-- Base ID -->
        </sequence>
    </attribute>
    <attribute id="0x0009">
        <sequence>
            <sequence>
                <uuid value="0x1124"/>
                <uint16 value="0x0100"/>
            </sequence>
        </sequence>
    </attribute>
    <attribute id="0x000d">
        <sequence>
            <sequence>
                <sequence>
                    <uuid value="0x0100"/> <!-- L2CAP -->
                    <uint16 value="0x0013"/> <!-- PSM: HID Interrupt -->
                </sequence>
                <sequence>
                    <uuid value="0x0011"/> <!-- HID Protocol -->
                    <uint16 value="0x0111"/>
                </sequence>
            </sequence>
        </sequence>
    </attribute>
    <attribute id="0x0100">
        <text value="Universal Control Clone"/>
    </attribute>
    <attribute id="0x0101">
        <text value="Linux HID"/>
    </attribute>
    <attribute id="0x0200">
        <uint16 value="0x0111"/> <!-- HID Release Number 1.11 -->
    </attribute>
    <attribute id="0x0201">
        <uint16 value="0x0111"/> <!-- Parser Version 1.11 -->
    </attribute>
    <attribute id="0x0202">
        <uint8 value="0xc0"/> <!-- Subclass: Combo (Keyboard + Mouse) -->
    </attribute>
    <attribute id="0x0203">
        <uint8 value="0x33"/> <!-- Country Code -->
    </attribute>
    <attribute id="0x0204">
        <boolean value="true"/> <!-- Virtual Cable -->
    </attribute>
    <attribute id="0x0205">
        <boolean value="true"/> <!-- Reconnect Initiate -->
    </attribute>
    <attribute id="0x0206">
        <sequence>
            <sequence>
                <uint8 value="0x22"/> <!-- Report Descriptor -->
                <text encoding="hex" value="{desc_str}"/>
            </sequence>
        </sequence>
    </attribute>
    <attribute id="0x0207">
        <sequence>
            <sequence>
                <uint16 value="0x2200"/> <!-- Language -->
                <uint16 value="0x0100"/> <!-- Base ID -->
            </sequence>
        </sequence>
    </attribute>
    <attribute id="0x020b">
        <uint16 value="0x0100"/> <!-- Profile Version -->
    </attribute>
    <attribute id="0x020c">
        <uint16 value="0x0c80"/> <!-- Supervision Timeout -->
    </attribute>
    <attribute id="0x020d">
        <boolean value="false"/> <!-- Normally Connectable -->
    </attribute>
    <attribute id="0x020e">
        <boolean value="true"/> <!-- Boot Device -->
    </attribute>
</record>
"""

    def connect_socket(self, sock):
        self.sock = sock
        logger.info("Socket connected throughout Service")

    def disconnect_socket(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        logger.info("Socket disconnected throughout Service")

    def send_report(self, data):
        if self.sock:
            try:
                # Put in queue (Non-blocking) with Timestamp
                self.send_queue.put_nowait((data, time.time()))
                return True
            except queue.Full:
                return False
            except Exception as e:
                logger.error(f"Queue put failed: {e}")
                return False
        return False

    def sender_loop(self):
        logger.info("Sender Thread started")
        while True:
            try:
                item = self.send_queue.get()
                data, timestamp = item
                
                # TTL Check (Latency Killer)
                # If Mouse packet (ID 0x02) is older than 30ms, DROP IT.
                if len(data) > 1 and data[1] == 0x02:
                     if time.time() - timestamp > 0.03:
                         self.send_queue.task_done()
                         continue
                
                if self.sock:
                    try:
                        self.sock.send(data)
                    except Exception as e:
                        logger.error(f"Send failed: {e}")
                        self.disconnect_socket()
                self.send_queue.task_done()
            except Exception as e:
                logger.error(f"Sender Loop Error: {e}")



    def listen(self):
        logger.info("Listening for connections on L2CAP P17 and P19...")
        self.scontrol = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
        self.sinterrupt = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
        
        self.scontrol.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sinterrupt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Enforce Security (Encryption/Authentication) for iOS compliance
        # BT_SECURITY = 4
        # BT_SECURITY_MEDIUM = 2, BT_SECURITY_HIGH = 3
        try:
            BT_SECURITY = 4
            BT_SECURITY_HIGH = 3
            self.scontrol.setsockopt(socket.SOL_BLUETOOTH, BT_SECURITY, BT_SECURITY_HIGH)
            self.sinterrupt.setsockopt(socket.SOL_BLUETOOTH, BT_SECURITY, BT_SECURITY_HIGH)
            logger.info("L2CAP Socket Security set to HIGH")
        except Exception as e:
            logger.warning(f"Failed to set L2CAP Security: {e}")

        # Bind to L2CAP ports
        self.scontrol.bind((socket.BDADDR_ANY, 17))
        self.sinterrupt.bind((socket.BDADDR_ANY, 19))
        
        
        self.scontrol.listen(1)
        self.sinterrupt.listen(1)
        
        GLib.io_add_watch(self.scontrol, GLib.IO_IN, self.accept_control)
        GLib.io_add_watch(self.sinterrupt, GLib.IO_IN, self.accept_interrupt)

        # Start Sender Thread
        t = threading.Thread(target=self.sender_loop)
        t.daemon = True
        t.start()

    def accept_control(self, source, cond):
        params = source.accept()
        logger.info(f"Accepted Control connection from {params[1]}")
        self.ccontrol, self.cinfo = params
        
        # Start a thread to drain input from Control channel (Handshakes, etc)
        t = threading.Thread(target=self.socket_reader, args=(self.ccontrol, "Control"))
        t.daemon = True
        t.start()
        return True

    def accept_interrupt(self, source, cond):
        params = source.accept()
        logger.info(f"Accepted Interrupt connection from {params[1]}")
        self.cinterrupt, self.cinfo = params
        
        try:
            # Set small Send Buffer to force blocking/dropping in userspace
            # This prevents kernel bufferbloat (latency)
            self.cinterrupt.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 512)
            # Set High Priority (6 = Interactive/Video)
            self.cinterrupt.setsockopt(socket.SOL_SOCKET, socket.SO_PRIORITY, 6)
        except Exception as e:
            logger.error(f"Failed to set Socket Options: {e}")

        self.connect_socket(self.cinterrupt)
        
        # Start a thread to drain input from Interrupt channel (Output reports like LEDs)
        t = threading.Thread(target=self.socket_reader, args=(self.cinterrupt, "Interrupt"))
        t.daemon = True
        t.start()
        return True

    def socket_reader(self, sock, name):
        try:
            while True:
                data = sock.recv(1024)
                if not data:
                    logger.info(f"Reader {name}: Socket closed by peer")
                    break
                logger.info(f"Received on {name}: {data.hex()}")
                
                # Handle HID Control Messages (Handshakes/Commands)
                if name == "Control" and len(data) > 0:
                    # 0x71 = SET_PROTOCOL (Report)
                    # We should reply with HANDSHAKE (SUCCESS) = 0x00
                    if (data[0] & 0xF0) == 0x70: # SET_PROTOCOL
                         logger.info("Received SET_PROTOCOL. Sending HANDSHAKE (SUCCESS)")
                         sock.send(bytes([0x00]))
                    
                    # 0x50 = SET_REPORT
                    elif (data[0] & 0xF0) == 0x50:
                         logger.info("Received SET_REPORT. Sending HANDSHAKE (SUCCESS)")
                         sock.send(bytes([0x00]))
                         
                    # 0x40 = GET_REPORT -> Not handling complex logic, just ACK or Ignore?
                    # Ideally we should send data if GET_REPORT. But usually iOS sends SET_PROTOCOL first.
                    
        except Exception as e:
            logger.error(f"Reader {name} error: {e}")


    def register(self):
        logger.info("Setting up L2CAP listeners...")
        self.listen()
        
        logger.info("Registering profile...")
        manager = dbus.Interface(self.bus.get_object("org.bluez", "/org/bluez"), "org.bluez.ProfileManager1")
        opts = {
            "ServiceRecord": self.sdp_xml,
            "Role": "server",
            "RequireAuthentication": True, 
            "RequireAuthorization": False
        }
        try:
            manager.RegisterProfile(self.path, "00001124-0000-1000-8000-00805f9b34fb", opts)
            logger.info("Profile registered successfully.")
        except dbus.exceptions.DBusException as e:
            if "UUID already registered" in str(e):
                logger.error("UUID already registered. This is expected if the service was not stopped cleanly. Proceeding with listeners...")
            else:
                logger.error(f"Failed to register profile: {e}")
                # We continue anyway because manually listening might work even if profile reg fails (if plugin is disabled)


