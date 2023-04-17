from firestore import Firestore
from switch_controller_with_modes import SwitchControllerWithModes
from switch import Switch
import random
import os
import warnings
# hide pygame's welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
with warnings.catch_warnings():
    # prevent warning about "neon capabilities"
    warnings.simplefilter("ignore")
    from pygame import mixer


class AudioController(SwitchControllerWithModes):
    _VOLUME_KEY = "volume"

    _AUDIO_DIRECTORY = "./audio"

    def __init__(self, switch: Switch, firestore: Firestore):
        self._firestore = firestore
        self._audio_files = list(map(lambda file: os.path.join(
            self._AUDIO_DIRECTORY, file), os.listdir(self._AUDIO_DIRECTORY)))
        mixer.init()
        super().__init__(switch, "audio")

    def _get_firestore_document(self):
        return self._firestore.get_audio_document()

    def _on_firestore_change(self, document_snapshot, changes, read_time):
        volume = document_snapshot[0].get(self._VOLUME_KEY)
        mixer.music.set_volume(volume / 100)
        super()._on_firestore_change(document_snapshot, changes, read_time)

    def _set_output_is_on(self, is_on):
        if is_on:
            mixer.music.unpause()
        else:
            mixer.music.pause()

    def _load_random_audio(self):
        file = random.choice(self._audio_files)

        print("Loading new audio file:", file)
        mixer.music.load(file)
        mixer.music.play()
        if not self._is_on:
            mixer.music.pause()

    def _handle_audio_finished(self):
        if not mixer.music.get_busy() and self._is_on:
            print("Current audio file finished.")
            mixer.music.stop()
            mixer.music.unload()
            self._load_random_audio()

    def handler(self):
        self._handle_audio_finished()

    def cleanup(self):
        mixer.quit()
        super().cleanup()
