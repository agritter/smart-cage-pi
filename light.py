import pigpio


class Light:
    def __init__(self, pi: pigpio.pi, pin):
        self._pin = pin
        self._pi = pi
        self._isOn = False
        pi.set_mode(pin, pigpio.OUTPUT)

    def setIsOn(self, isOn):
        self._isOn = isOn
        self._pi.write(self._pin, int(isOn))

    def isOn(self):
        return self._isOn
