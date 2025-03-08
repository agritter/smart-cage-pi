import threading
from switch import Switch


class SwitchControllerWithModes:
    """
        Controls an output based on a mode specified in a Firestore document and a switch's value
        This class is designed to be overridden to handle specific outputs
    """
    _MODE_KEY = "mode"
    _IS_ON_KEY = "isOn"
    _TIMEOUT_KEY = "timeout"

    # Modes
    _ON_MODE = "on"  # Always on
    _OFF_MODE = "off"  # Always off
    _SWITCH_TOGGLE_MODE = "switchToggle"  # Toggles when switch pressed
    _SWITCH_VALUE_MODE = "switchValue"  # On only when switch pressed
    _SWITCH_TIMEOUT_MODE = "switchTimeout"  # On until timeout when switch pressed

    def __init__(self, switch: Switch, output_name=""):
        """
            Initializes the controller to use the {switch}
            {output_name} is used to identify the output in debug messages
        """
        self._switch = switch
        self._output_name = output_name
        self._is_on = False
        self._current_mode = self._OFF_MODE
        self._timeout = 0
        self._timeout_timer = threading.Timer(
            0, lambda: self._set_is_on(False))

        self._subscription = self._get_firestore_document(
        ).on_snapshot(self._on_firestore_change)

    def _on_firestore_change(self, document_snapshot, changes, read_time):
        """
            Handles any change to the mode in the Firestore document
        """
        document = document_snapshot[0]
        print(f"New {self._output_name} document received: {document.to_dict()}")

        timeout = int(document_snapshot[0].get(self._TIMEOUT_KEY))
        mode = document.get(self._MODE_KEY)

        if timeout != self._timeout:
            if mode == self._SWITCH_TIMEOUT_MODE:
                self._timeout_timer.cancel()
                self._set_is_on(False)
            self._timeout = timeout

        if mode != self._current_mode:
            self._current_mode = mode
            self._switch.remove_all_on_changes()
            if mode == self._ON_MODE:
                self._set_is_on(True)
            elif mode == self._OFF_MODE:
                self._set_is_on(False)
            elif mode == self._SWITCH_TOGGLE_MODE:
                self._switch.add_on_change(self._toggle_on_switch_press)
            elif mode == self._SWITCH_VALUE_MODE:
                self._set_is_on(self._switch.is_on())
                self._switch.add_on_change(self._follow_switch_pressed)
            elif mode == self._SWITCH_TIMEOUT_MODE:
                self._set_is_on(self._switch.is_on())
                self._switch.add_on_change(self._timeout_after_switch_release)

    def _toggle_on_switch_press(self, switch_pressed):
        """
            Toggles the output if the switch is pressed
            Called when the switch's value changes when in switch toggle mode
        """
        if switch_pressed:
            self._set_is_on(not self._is_on)

    def _follow_switch_pressed(self, switch_pressed):
        """
            Sets the output to be on if the switch is on and off if it's off
            Called when the switch's value changes when in switch value mode
        """
        self._set_is_on(switch_pressed)

    def _timeout_after_switch_release(self, switch_pressed):
        """
            Sets the output to be on when the switch is pressed and to timeout after it is released
            Called when the switch's value changes when in switch toggle mode
        """
        if switch_pressed:
            self._set_is_on(True)
        else:
            self._timeout_timer = threading.Timer(
                self._timeout * 60, lambda: self._set_is_on(False))
            self._timeout_timer.start()

    def _set_is_on(self, is_on):
        """
            Sets the output base on {is_on} and updates the Firestore document
            to show whether the output is on
        """
        if self._is_on != is_on:
            print(f"Setting {self._output_name} is on to {is_on}")
            self._is_on = is_on
            self._get_firestore_document().update(
                {self._IS_ON_KEY: is_on})
            self._set_output_is_on(is_on)

    def cleanup(self):
        """
            Cleans up the resources used by the controller
        """
        self._set_output_is_on(False)
        self._subscription.unsubscribe()

    def _set_output_is_on(self, is_on):
        """
            Set the output on or off based on {is_on}
            Should be overridden by a child class
        """
        raise NotImplementedError

    def _get_firestore_document(self):
        """
            Returns the Firestore document corresponding to the output
            Should be overridden by a child class
        """
        raise NotImplementedError
