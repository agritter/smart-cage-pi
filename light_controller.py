from firestore import Firestore
from switch_controller_with_modes import SwitchControllerWithModes
from light import Light
from switch import Switch


class LightController(SwitchControllerWithModes):
    """
        Controls the LED based on the mode in Firestore and switch's value
    """

    def __init__(self, switch: Switch, light: Light, firestore: Firestore):
        """
            Initializes the controller to control the {light} using {switch} and the mode in {firestore}
        """
        self._light = light
        self._firestore = firestore
        super().__init__(switch, "light")

    def _get_firestore_document(self):
        """
            Returns the Firestore document for the light
            Overrides the super class
        """
        return self._firestore.get_light_document()

    def _set_output_is_on(self, isOn):
        """
            Turn the light on or off based on {is_on}
            Overrides the super class
        """
        self._light.set_is_on(isOn)
