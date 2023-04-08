import pigpio


class Switch:
    _DEBOUNCETIME = 50000

    def __init__(self, pi: pigpio.pi, pin):
        self._pin = pin
        self._callbacks = []
        self._pi = pi
        self._isOn = False

        pi.set_pull_up_down(pin, pigpio.PUD_UP)
        pi.set_mode(pin, pigpio.INPUT)
        pi.set_glitch_filter(pin, self._DEBOUNCETIME)

        self._setIsOnCallback = self._pi.callback(
            self._pin, pigpio.EITHER_EDGE, self.setIsOn)

    def addOnChange(self, onChange):
        def callback(_, isOff, __): return onChange(not isOff)
        callbackHandle = self._pi.callback(
            self._pin, pigpio.EITHER_EDGE, callback)
        self._callbacks.append(callbackHandle)

    def removeAllOnChanges(self):
        for callback in self._callbacks:
            callback.cancel()

    def isOn(self):
        return self._isOn

    def setIsOn(self, _, isOff, __):
        self._isOn = not isOff

    def cleanup(self):
        self._setIsOnCallback.cancel()
        self.removeAllOnChanges()
