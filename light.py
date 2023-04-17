import pigpio


class Light:
    def __init__(self, pi: pigpio.pi, pin):
        self._pin = pin
        self._pi = pi
        pi.set_mode(pin, pigpio.OUTPUT)

    def set_is_on(self, is_on):
        self._pi.write(self._pin, int(is_on))
