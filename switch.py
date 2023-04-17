import pigpio


class Switch:
    _DEBOUNCE_TIME = 50000

    def __init__(self, pi: pigpio.pi, pin):
        self._pin = pin
        self._callbacks = []
        self._pi = pi
        self._is_on = False

        pi.set_pull_up_down(pin, pigpio.PUD_UP)
        pi.set_mode(pin, pigpio.INPUT)
        pi.set_glitch_filter(pin, self._DEBOUNCE_TIME)

        self._set_is_on_callback = self._pi.callback(
            self._pin, pigpio.EITHER_EDGE, self.set_is_on)

    def add_on_change(self, on_change):
        def callback(_, is_off, __): return on_change(not is_off)
        callback_handle = self._pi.callback(
            self._pin, pigpio.EITHER_EDGE, callback)
        self._callbacks.append(callback_handle)

    def remove_all_on_changes(self):
        for callback in self._callbacks:
            callback.cancel()

    def is_on(self):
        return self._is_on

    def set_is_on(self, _, is_off, __):
        self._is_on = not is_off

    def cleanup(self):
        self._set_is_on_callback.cancel()
        self.remove_all_on_changes()
