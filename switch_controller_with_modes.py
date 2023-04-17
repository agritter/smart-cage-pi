from switch import Switch


class SwitchControllerWithModes:
    _MODE_KEY = "mode"
    _IS_ON_KEY = "isOn"

    # Modes
    _ON_MODE = "on"
    _OFF_MODE = "off"
    _SWITCH_TOGGLE_MODE = "switchToggle"
    _SWITCH_VALUE_MODE = "switchValue"

    def __init__(self, switch: Switch, output_name=""):
        self._switch = switch
        self._output_name = output_name
        self._set_is_on(False)
        self._current_mode = self._OFF_MODE

        self._subscription = self._get_firestore_document(
        ).on_snapshot(self._on_firestore_change)

    def _on_firestore_change(self, document_snapshot, changes, read_time):
        document = document_snapshot[0]
        print(f"New {self._output_name} document received: {document.to_dict()}")
        mode = document.get(self._MODE_KEY)
        self._handle_mode(mode)

    def _handle_mode(self, mode):
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

    def _toggle_on_switch_press(self, switch_pressed):
        if switch_pressed:
            self._set_is_on(not self._is_on)

    def _follow_switch_pressed(self, switch_pressed):
        self._set_is_on(switch_pressed)

    def _set_is_on(self, is_on):
        print(f"Setting {self._output_name} is on to {is_on}")
        self._is_on = is_on
        self._get_firestore_document().update(
            {self._IS_ON_KEY: is_on})
        self._set_output_is_on(is_on)

    def cleanup(self):
        self._subscription.unsubscribe()

    def _set_output_is_on(self, is_on):
        raise NotImplementedError

    def _get_firestore_document(self):
        raise NotImplementedError
