import pigpio


class Switch:
    """
        Handles input from a switch
    """
    _DEBOUNCE_TIME = 50000

    def __init__(self, pi: pigpio.pi, pin):
        """
            Initialize the switch
            The switch should be connected to {pin} and ground
            {pi} should be an instance of pigpio
        """
        self._pin = pin
        self._callbacks = []
        self._pi = pi
        self._is_on = False

        pi.set_pull_up_down(pin, pigpio.PUD_UP)
        pi.set_mode(pin, pigpio.INPUT)
        pi.set_glitch_filter(pin, self._DEBOUNCE_TIME)

        self._set_is_on_callback = self._pi.callback(
            self._pin, pigpio.EITHER_EDGE, self._set_is_on)

    def add_on_change(self, on_change):
        """
            Adds a function ({on_change}) that will be called when the switch's debounced value changes
            {on_change} will be passed a boolean representing whether the switch is pressed
        """
        def callback(_, is_off, __): return on_change(not is_off)
        callback_handle = self._pi.callback(
            self._pin, pigpio.EITHER_EDGE, callback)
        self._callbacks.append(callback_handle)

    def remove_all_on_changes(self):
        """
            Removes any callbacks added by {add_on_change}
        """
        for callback in self._callbacks:
            callback.cancel()

    def is_on(self):
        """
            Returns whether the switch is currently pressed (post-debounce)
        """
        return self._is_on

    def _set_is_on(self, _, is_off, __):
        """
            Sets whether the switch is pressed
            Called when the switch's debounced value changes
        """
        self._is_on = not is_off

    def cleanup(self):
        """
            Cleans up the resources used by the switch
        """
        self._set_is_on_callback.cancel()
        self.remove_all_on_changes()
