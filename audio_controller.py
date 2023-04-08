from firestore import Firestore
from switch import Switch
import random
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # hide pygame's message
import pygame


class AudioController:
    _ISONKEY = "isOn"
    _VOLUMEKEY = "volume"
    _MODEKEY = "mode"
    _MODEON = "on"
    _MODEOFF = "off"
    _MODESWITCHTOGGLE = "switchToggle"
    _MODESWITCHVALUE = "switchValue"

    _AUDIODIRECTORY = "./audio"

    def __init__(self, switch: Switch, firestore: Firestore):
        self._switch = switch
        self._firestore = firestore
        self._currentMode = self._MODEOFF
        self._isPlaying = False

        self._audioFiles = list(map(lambda file: os.path.join(
            self._AUDIODIRECTORY, file), os.listdir(self._AUDIODIRECTORY)))

        pygame.mixer.init()
        self._loadRandomAudio()

        self._setPlaying(False)

        self._subscription = firestore.getAudioDocument().on_snapshot(self._onFirestoreChange)

    # todo very copied
    def _onFirestoreChange(self, document_snapshot, changes, read_time):
        mode = document_snapshot[0].get(self._MODEKEY)
        if mode != self._currentMode:
            self._currentMode = mode
            self._switch.removeAllOnChanges()
            if mode == self._MODEON:
                self._setPlaying(True)
            elif mode == self._MODEOFF:
                self._setPlaying(False)
            elif mode == self._MODESWITCHTOGGLE:
                self._setPlaying(False)
                self._switch.addOnChange(self._toggleOnSwitchPress)
            elif mode == self._MODESWITCHVALUE:
                self._setPlaying(self._switch.isOn())
                self._switch.addOnChange(self._followSwitchPressed)

        volume = document_snapshot[0].get(self._VOLUMEKEY)
        pygame.mixer.music.set_volume(volume / 100)

    def _setPlaying(self, isPlaying):
        self._isPlaying = isPlaying
        if isPlaying:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self._firestore.getAudioDocument().update(
            {self._ISONKEY: isPlaying})

    def _toggleOnSwitchPress(self, switchPressed):
        if switchPressed:
            self._setPlaying(not self._isPlaying)

    def _followSwitchPressed(self, switchPressed):
        self._setPlaying(switchPressed)

    def _loadRandomAudio(self):
        file = random.choice(self._audioFiles)

        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        if not self._isPlaying:
            pygame.mixer.music.pause()

    def _handleAudioFinished(self):
        if not pygame.mixer.music.get_busy():
           # pygame.mixer.music.unload()
            self._loadRandomAudio()

    def handler(self):
        self._handleAudioFinished()
