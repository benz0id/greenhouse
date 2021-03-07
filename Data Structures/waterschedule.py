import gspread
from datetime import time, datetime, date
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Tuple, Dict



scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'Green House-3b2a08455850.json',
    scope)
client = gspread.authorize(credentials)


def time_reformat_tuple(dte: str) -> Tuple[time, int]:
    """Turns a date string with duration value (found in spreadsheet) into a
    tuple of two times.
    >>> time_reformat_tuple("14:40:00_20:00")
    
    ("""
    breakdown = []
    sub = ""
    for char in dte + ":":
        if char == ":" or char == "_":
            breakdown.append(sub)
            sub = ""
        else:
            sub = sub + char

    for i in range(0, len(breakdown)):
        num = int(breakdown[i])
        breakdown[i] = num

    time1 = datetime(2001, 1, 4, breakdown[0], breakdown[1], breakdown[2])
    duration = breakdown[-2] * 60 + breakdown[-1]

    time1 = time1.time()

    return time1, duration


class WateringSchedule:
    """Designed to allow for the storing and updating of a watering schedule.

    ---Attributes---
    weekly_schedule: Stores each day of the weeks schedule in tuple format
                     (time, duration).
    """
    weekly_schedule: Dict[int, List[Tuple[time, int]]]

    def __init__(self) -> None:
        """Initiates template schedules"""
        self.weekly_schedule = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

    def update(self) -> bool:
        """Loads a backed up schedule to <weekly_schedule>, returns true iff
        successful"""
        try:
            self.__init__()

            schedulesheet = client.open("Watering Schedule").sheet1

            for i in range(3, 17, 2):
                column_data = schedulesheet.col_values(i)
                day = (i - 3) // 2
                column_data.pop(0)
                for dayte in column_data:
                    t = (time_reformat_tuple(dayte))
                    self.weekly_schedule[day].append(t)

            return True
        except Exception:
            return False

    def get_times(self) -> List[Tuple[time, int]]:
        """Returns a list of times that watering needs to be done on for the
        current day"""
        return self.weekly_schedule[date.today().weekday()]
