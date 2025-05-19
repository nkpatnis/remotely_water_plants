from machine import Timer, RTC
import network
from time import sleep
from utils import Led, LONG_DELAY, SHORT_DELAY
import requests
import json
import gc

led = Led()

class RealTime():
    counter = 0        

    def fetch_time(self):
        rtc = RTC()
        self.counter += 1

        long_retry_time = LONG_DELAY

        print("Fetching Time")

        led.action()
        try:
            # https://timeapi.io/swagger/index.html
            response = requests.get(
                "https://timeapi.io/api/time/current/zone?timeZone=Asia%2FKolkata", timeout=10
            )
            response_code = response.status_code
            if response_code != 200:
                retry_time = long_retry_time if self.counter > 5 else 60
                print(f"Error: Retry after {retry_time} Scs", 0, 16)
                sleep(retry_time)
                self.fetch_time()

            response = json.loads(response.content)

            # Extract time
            year = int(response["year"])
            month = int(response["month"])  # Placeholder
            day = int(response["day"])  # Placeholder
            hour = int(response["hour"])  # Placeholder
            minute = int(response["minute"])  # Placeholder
            second = int(response["seconds"])  # Placeholder

            # Set RTC
            rtc.datetime((year, month, day, 0, hour, minute, second, 0))
            print("time set")
            sleep(1)
        except Exception as e:
            gc.collect()
            print(f"Error: {str(e)}\nRetry in {long_retry_time} Seconds")
            sleep(long_retry_time)
            self.fetch_time()


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

    def sync_rtc(self):
        rt = RealTime()
        rt.fetch_time()
