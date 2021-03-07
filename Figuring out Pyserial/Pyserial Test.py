"""import serial
import datetime
import time

arduino = serial.Serial('COM7', 9600, timeout=.1)

while True:
    data = arduino.readline().strip()
    if data:
        print(data)
"""

import serial
import time
arduino = serial.Serial('COM7', 9600, timeout=.1)
time.sleep(1) #give the connection a second to settle
"""arduino.write("Hello from Python!".encode())

while True:
    time.sleep(1) #give the connection a second to settle
    arduino.write("Hello from Python!".encode())
    txt = arduino.readline()
    if txt:
        print(txt.strip())
"""
