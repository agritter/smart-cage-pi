from firestore import Firestore
from switch_controller_with_modes import SwitchControllerWithModes
from light import Light
from switch import Switch


class LightController(SwitchControllerWithModes):

    def __init__(self, switch: Switch, light: Light, firestore: Firestore):
        self._light = light
        self._firestore = firestore
        super().__init__(switch, "light")

    def _get_firestore_document(self):
        return self._firestore.get_light_document()

    def _set_output_is_on(self, isOn):
        self._light.set_is_on(isOn)

    def cleanup(self):
        # self._set_output_is_on(False) #todo needed
        super().cleanup()
