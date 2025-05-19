import os
from machine import Pin, Timer, RTC
from utime import sleep
import json

LONG_DELAY = 10
SHORT_DELAY = 3


class Led:

    def __init__(self, gpio="LED"):
        self.indicator = Pin(gpio, Pin.OUT)


    def _blink_led(self, count=SHORT_DELAY, delay=0.1):
        for i in range(0, count):
            # Blink the LED
            self.indicator.on()
            sleep(delay)
            self.indicator.off()
            sleep(delay)

    def action(self):
        self._blink_led(SHORT_DELAY, 0.5)

    def error(self):
        self._blink_led(LONG_DELAY, 0.25)
    
    def warn(self):
        self._blink_led(SHORT_DELAY, 0.1)

    def on(self):
        self.indicator.on()

    def off(self):
        self.indicator.off()



def get_system_datetime():
    rtc = RTC()
    year, month, day, dow, hour, mins, secs, subsec = rtc.datetime()
    formatted_date = f"{year:04}-{month:02}-{day:02}"
    formatted_time = f"{hour:02}:{mins:02}:{secs:02}"

    print(f"Date: {formatted_date}, Time: {formatted_time}")
    return formatted_date, formatted_time


class Record:
    FILENAME = "record.json"
    DIR = "/data"

    def __init__(self):
        print("Initializing Record")
        current_directory = os.getcwd()
        entries = os.listdir(current_directory)
        print("Current:", current_directory, entries)
        if self.DIR.replace("/", "") not in entries:
            os.mkdir(self.DIR)
        os.chdir(self.DIR)
        current_directory = os.getcwd()
        entries = os.listdir(current_directory)

        if not self.FILENAME in entries:
            initial_data = {}
            # Create a file if it doesn't exist
            with open(self.FILENAME, "w") as file:
                # Write initial data to the file
                print(f"Creating {self.DIR}/{self.FILENAME}...")
                file.write(json.dumps(initial_data))

    def write_to_file(self, data):
        with open(self.FILENAME, "w") as file:
            data_str = json.dumps(data)
            # Write content to the file
            file.write(data_str)
            # Close the file to save the changes

    def read_from_file(self):
        # To read the file
        file = open(self.FILENAME, "r")
        # Read the content of the file
        data_str = file.read()
        # Convert the string to a dictionary
        data = json.loads(data_str)
        file.close()
        return data
