import gspread
import serial
import waterschedule
import datacollect

from time import sleep
from datetime import datetime, time
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Tuple, Dict

# Programmed before I knew what I was doing.
# Forgive egregious design decisions & general bad code lol.

print("Initiating setup")

print("Accessing google API")
JSON = 'my_API_creds.json'
SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
CREDS = ServiceAccountCredentials.from_json_keyfile_name(
    JSON,
    SCOPE)
CLIENT = gspread.authorize(CREDS)

print("Establishing arduino connection")

arduino = serial.Serial('COM7', 9600, timeout=.1)

print("Setting up measurement classes and tools")
weekly_data = datacollect.SamplingSchedule()
weekly_data.update()
humid = datacollect.Humidity()
temp = datacollect.Temperature()
light = datacollect.Brightness()

measurement_list = [humid, temp, light]


def record_data_all(measurements: List[datacollect.Measurement]) -> bool:
    """Executes the record_data_point method for all of the objects in
    <measurements>"""
    successful = True
    for measurement in measurements:
        if not measurement.record_data_point(arduino):
            successful = False
        else:
            print("Measure", measurement.to_arduino_string, "successful.")

    return successful


print("Setting up watering functions and structures")

weekly_watering = waterschedule.WateringSchedule()
weekly_watering.update()


def water(duration: int) -> bool:
    """"Waters the plants for <duration> seconds."""
    try:
        arduino.readall()

        arduino.write("water on".encode())
        """print("Sending \"water on\"")"""
        value = arduino.readall().decode()
        while not value:
            value = arduino.readall().decode()

        """print("Watering confirmation received, sending /", duration)"""

        arduino.write(str(duration).encode())

        value2 = arduino.readall()
        while not value2:
            value2 = arduino.readall()

        """print("Duration confirmation received")"""

        return True
    except Exception:
        return False


print("Setting up general functions and preparing schedules for use")

daily_water = []
daily_data = []


if not weekly_watering.update() or not weekly_data.update():
    working = False
day = datetime.today().weekday()
daily_water = weekly_watering.weekly_schedule[day]
daily_data = weekly_data.weekly_schedule[day]


def report_error() -> None:
    """Activates the arduino's error light."""
    arduino.write("ERROR".encode())


def to_seconds(tme: datetime.time) -> int:
    """Returns the number of seconds since the start of the day"""
    return tme.hour * 3600 + tme.minute * 60 + tme.second


def clear_old() -> None:
    """Clears all old vales that were missed earlier in the day"""
    current_seconds = to_seconds(datetime.today().time())
    i = 0
    while i < len(daily_water):
        event = daily_water[i]
        if to_seconds(event[0]) + event[1] < current_seconds:
            daily_water.remove(event)
        else:
            i += 1

    current_seconds = to_seconds(datetime.today().time())
    i = 0
    while i < len(daily_data):
        event = daily_data[i]
        if to_seconds(event) < current_seconds:
            daily_data.remove(event)
        else:
            i += 1


clear_old()


current_time = datetime.today().time()
print("Boot-up complete")
print("Data schedule:", daily_data)
print("Watering schedule:", daily_water)

# Infinite loop
while True:
    data = arduino.readall()
    if data:
        print("Serial data detected")
        data = data.decode()
        if "update" in data:
            print("Attempting update")
            if not weekly_watering.update() or not weekly_data.update():
                report_error()
                print("Update failed")
            else:
                print('Update successful')
                print(daily_water)
            daily_water = weekly_watering.weekly_schedule[day]
            daily_data = weekly_data.weekly_schedule[day]
            clear_old()

    last_time = current_time
    current_time = datetime.today().time()

    # checking if a day has passed
    # if so, updates weekly and daily schedules

    if last_time.hour - current_time.hour > 22:
        print("Starting new day")
        a = weekly_watering.update()
        b = weekly_data.update()
        if a and b:
            print("New day successful")
        else:
            print("New day failed")
            report_error()
        day = datetime.today().weekday()
        daily_water = weekly_watering.weekly_schedule[day]
        daily_data = weekly_data.weekly_schedule[day]

    # checking for watering and data collection events
    is_daily_data = bool(daily_data)
    is_daily_water = bool(daily_water)

    if is_daily_data and daily_data[0] < current_time:
        print("Beginning measurements.")
        if record_data_all(measurement_list):
            print("Measurements successful")
        else:
            print("Measurements failed.")
            report_error()
        daily_data.pop(0)
    if is_daily_water and daily_water[0][0] < current_time:
        print("Watering for", daily_water[0][1], "seconds.")
        sleep(0.1)
        if water(daily_water[0][1]):
            print("Watering successful")
        else:
            print("Watering Failed")
            report_error()
        daily_water.pop(0)

        sleep(1)
