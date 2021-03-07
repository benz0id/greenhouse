import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)


class Pin:

    pin_num: int
    state: bool

    def __init__(self, pin_num: int, pin_mode: str):
        self.state = False
        self.pin_num = pin_num

        if pin_mode == "O":
            GPIO.setup(pin_num, GPIO.OUT)
        elif pin_mode == "I":
            GPIO.setup(pin_num, GPIO.IN)
        else:
            TypeDoesNotExistError: "Type does not exist"

    def update(self):
        GPIO.output(self.pin_num, self.state)

    def get_state(self) -> bool:
        return self.state

    def on(self):
        self.state = True
        self.update()

    def off(self):
        self.state = False
        self.update()

    def switch_state(self):
        self.state = not self.state
        self.update()


led1 = Pin(11, "O")
led2 = Pin(15, "O")
led3 = Pin(16, "O")
led4 = Pin(18, "O")
led5 = Pin(19, "O")

ledlist = [led1, led2, led3, led4, led5]

# Main loop
while True:
    for led in ledlist:
        led.switch_state()
        print("Turning on " + str(led.pin_num))
        time.sleep(1)

    for led in ledlist:
        led.switch_state()
        print("Turning off " + str(led.pin_num))
        time.sleep(3)
