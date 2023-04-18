import pigpio


class Light:
    """
        Handles an LED
    """

    def __init__(self, pi: pigpio.pi, pin):
        """
            Initialized an LED connected to {pin}
            {pi} should be an instance of pigpio
        """
        self._pin = pin
        self._pi = pi
        pi.set_mode(pin, pigpio.OUTPUT)

    def set_is_on(self, is_on):
        """
            Turn the light on or off based on {is_on}
        """
        self._pi.write(self._pin, int(is_on))
