import gspread
import serial
from datetime import time, timedelta, datetime, date
from time import sleep
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Any

# Your JSON filename goes here
json = ''

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    json,
    scope)
client = gspread.authorize(credentials)


def soft_to_hard_date(date: str) -> time:
    """Returns the date in time format."""

    breakdown = []
    sub = ""
    for char in date + ":":
        if char == ":":
            breakdown.append(sub)
            sub = ""
        else:
            sub = sub + char

    for i in range(0, len(breakdown)):
        num = int(breakdown[i])
        breakdown[i] = num

    time1 = datetime(2001, 1, 4, breakdown[0], breakdown[1], breakdown[2])
    time1 = time1.time()

    return time1


class SamplingSchedule:
    """Designed to allow for the storing and updating of the sampling schedule
    ---Attributes---
    weekly_schedule: Stores each day of the weeks schedule in tuple format
                     (time, duration).
    """
    weekly_schedule: Dict[int, List[time]]

    def __init__(self) -> None:
        """Initiates template schedules"""
        self.weekly_schedule = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

    def update(self) -> bool:
        """Loads a backed up schedule to <weekly_schedule>, returns true iff
        successful"""
        try:
            schedule_sheet = client.open("Watering Schedule").sheet1
            read = schedule_sheet.cell(15, 17).value
            self.__init__()

            if read:

                current_time = datetime(2001, 1, 1, 0, 0, 0, 0)
                delta_time = timedelta(0, 0, 0, 0, int(read))

                while (current_time + delta_time).day <= 1:
                    current_time += delta_time
                    self.weekly_schedule[0].append(current_time.time())

                for i in range(1, 7):
                    self.weekly_schedule[i] = self.weekly_schedule[0]

                return True

            else:
                return self.update_from_sheets()
        except Exception:
            return False

    def update_from_sheets(self) -> bool:
        """Updates from a list of times provided on the spreadsheet."""
        try:
            schedule_sheet = client.open("Watering Schedule").sheet1

            for i in range(19, 27):
                column_data = schedule_sheet.col_values(i)
                day = i - 19
                column_data.pop(0)
                for dte in column_data:
                    self.weekly_schedule[day].append(soft_to_hard_date(dte))
            return True
        except Exception:
            return False

    def get_times(self) -> List[time]:
        """Returns a list of times that watering needs to be done on for the
        current day"""
        return self.weekly_schedule[date.today().weekday()]


class Measurement:
    """Parent class for all measurement subclasses. Designed to encompass all
    the methods required to communicate with arduino and record data to
    <spreadsheet_name>.

    ---Attributes---
    to_arduino_str: The string to be printed to the arduino when data collection
                    is required.
    spreadsheet_name: The name of the spreadsheet for measurements to be
                      recorded to.
    _schedule_name: The name of the schedule to which this measurement belongs.
    """

    to_arduino_string: str
    spreadsheet_name: str
    _schedule_name: str

    def __init__(self) -> None:
        _schedule_name = "Watering Schedule"

    def get_data(self, arduino: serial.Serial) -> Any:
        """Returns the measurement recorded from the arduino."""
        arduino.readall()

        arduino.write(self.to_arduino_string.encode())
        sleep(1)
        value = arduino.readall()
        while not value:
            value = arduino.readall()

        value = value.decode()

        return value

    def record_data_point(self, arduino: serial.Serial) -> bool:
        """Records a data point to a given spreadsheet"""

        spreadsheet = client.open(self.spreadsheet_name).sheet1

        data = self.get_data(arduino)
        curdate = datetime.today().isoformat()

        row = self.find_next_row(spreadsheet)
        spreadsheet.update_cell(row, 2, data)
        spreadsheet.update_cell(row, 1, curdate)
        return True

    def find_next_row(self, spreadsheet) -> int:
        """Finds the coordinates of the latest data point to be collected"""

        value = int(spreadsheet.cell(2, 3).value)
        spreadsheet.update_cell(2, 3, value + 1)

        return value


class Brightness(Measurement):
    """Allows for recording and uploading of brightness data.

    ---Attributes---
    to_arduino_str: The string to be printed to the arduino when data collection
                    is required.
    spreadsheet_name: The name of the spreadsheet for measurements to be
                      recorded to.
    _schedule_name: The name of the schedule to which this measurement belongs.
    """

    def __init__(self):
        Measurement.__init__(self)
        self.to_arduino_string = "light"
        self.spreadsheet_name = "Brightness Data"


class Temperature(Measurement):
    """Allows for recording and uploading of temperature data.

    ---Attributes---
    to_arduino_str: The string to be printed to the arduino when data collection
                    is required.
    spreadsheet_name: The name of the spreadsheet for measurements to be
                      recorded to.
    _schedule_name: The name of the schedule to which this measurement belongs.
    """

    def __init__(self):
        Measurement.__init__(self)
        self.to_arduino_string = "temp"
        self.spreadsheet_name = "Temperature Data"


class Humidity(Measurement):
    """Allows for recording and uploading of humidity data.

    ---Attributes---
    to_arduino_str: The string to be printed to the arduino when data collection
                    is required.
    spreadsheet_name: The name of the spreadsheet for measurements to be
                      recorded to.
    _schedule_name: The name of the schedule to which this measurement belongs.
    """

    def __init__(self) -> None:
        Measurement.__init__(self)
        self.to_arduino_string = "humid"
        self.spreadsheet_name = "Humidity Data"
