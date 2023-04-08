from firestore import Firestore
from light import Light
from switch import Switch


class LightController:
    _ISONKEY = "isOn"
    _MODEKEY = "mode"
    _MODEON = "on"
    _MODEOFF = "off"
    _MODESWITCHTOGGLE = "switchToggle"
    _MODESWITCHVALUE = "switchValue"

    def __init__(self, switch: Switch, light: Light, firestore: Firestore):
        self._switch = switch
        self._light = light
        self._firestore = firestore
        self._currentMode = self._MODEOFF
        self._setLight(False)

        self._subscription = firestore.getLightDocument().on_snapshot(self._onFirestoreChange)

    def _onFirestoreChange(self, document_snapshot, changes, read_time):
        mode = document_snapshot[0].get(self._MODEKEY)
        if mode != self._currentMode:
            self._currentMode = mode
            self._switch.removeAllOnChanges()
            if mode == self._MODEON:
                self._setLight(True)
            elif mode == self._MODEOFF:
                self._setLight(False)
            elif mode == self._MODESWITCHTOGGLE:
                self._setLight(False)
                self._switch.addOnChange(self._toggleOnSwitchPress)
            elif mode == self._MODESWITCHVALUE:
                self._setLight(self._switch.isOn())
                self._switch.addOnChange(self._followSwitchPressed)

    def _toggleOnSwitchPress(self, switchPressed):
        if switchPressed:
            self._setLight(not self._light.isOn())

    def _followSwitchPressed(self, switchPressed):
        self._setLight(switchPressed)

    def _setLight(self, isOn):
        self._light.setIsOn(isOn)
        self._firestore.getLightDocument().update(
            {self._ISONKEY: isOn})

    def cleanup(self):
        self._setLight(False)
        self._subscription.unsubscribe()
