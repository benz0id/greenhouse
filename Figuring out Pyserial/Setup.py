import serial
from time import sleep
arduino = serial.Serial('COM7', 9600, timeout=.1)
sleep(4)
from datetime import time
while True:
    def water(duration: int) -> bool:
        """"Waters the plants for <duration> seconds."""
        try:
            arduino.readall()

            arduino.write("water on".encode())
            value = arduino.readall().decode()
            while not value:
                value = arduino.readall().decode()

            print("Watering confirmation received, sending", duration)

            arduino.write(str(duration).encode())

            value2 = arduino.readall()
            while not value2:
                value2 = arduino.readall()

            print("Duration confirmation received")

            return True
        except Exception:
            return False

    water(10000)

    """daily_water = [(0, 120)]
    is_daily_water = True
    
    if is_daily_water:
        print("Watering for", daily_water[0][1], "seconds.")
        if water(daily_water[0][1]):
            print("Watering successful")
        else:
            print("Watering Failed")
        daily_water.pop(0)"""

    sleep(2)

