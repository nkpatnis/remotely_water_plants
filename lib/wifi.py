import network
from time import sleep
from utils import Led
import gc

led = Led()

class WiFi:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

    def connect(self):
        print("Connecting to Wi-Fi...")
            
        led.action()
        self.wlan.connect(self.ssid, self.password)

        connection_timeout = 10
        while connection_timeout > 0:
            print(f"Connecting ({self.ssid})...{connection_timeout}")
            if self.wlan.status() >= 3:
                break
            connection_timeout -= 1
            print("Waiting for Wi-Fi connection...")
            sleep(5)

        if not self.is_connected():
            self.delayed_retry()
        else:
            print("Connected!!")
        sleep(1)

    def is_connected(self):
        return self.wlan.status() == 3

    def get_ip(self):
        if self.is_connected():
            return self.wlan.ifconfig()[0]
        else:
            return None

    def disconnect(self):
        self.wlan.disconnect()
        self.wlan.active(False)

    def get_status(self):
        if self.is_connected():
            return "Connected"
        else:
            return "Disconnected"

    def delayed_retry(self):
        print("Retrying connection...")
        # Check if connection is successful
        gc.collect()
        sleep(60 % 5)
        self.connect()
