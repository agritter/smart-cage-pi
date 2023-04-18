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
    """ Plays audio based on the current mode in Firestore and switch value """
    _VOLUME_KEY = "volume"
    _AUDIO_DIRECTORY = "./audio"
    _VOLUME_TOLERANCE = 0.01

    def __init__(self, switch: Switch, firestore: Firestore):
        """
            Initializes the controller to control audio using the {switch} and the mode and volume in {firestore}
        """
        self._firestore = firestore
        # Get the paths of the files in the audio directory
        self._audio_files = list(map(lambda file: os.path.join(
            self._AUDIO_DIRECTORY, file), os.listdir(self._AUDIO_DIRECTORY)))
        mixer.init()
        super().__init__(switch, "audio")

    def _get_firestore_document(self):
        """
            Returns the firestore document for audio
            Overrides the super class
        """
        return self._firestore.get_audio_document()

    def _on_firestore_change(self, document_snapshot, changes, read_time):
        """
            Handles any change to the audio document
        """
        # Set the volume if it changed
        volume = document_snapshot[0].get(self._VOLUME_KEY) / 100
        # Check if the volume is close to the actual volume
        # (the volume is set to a value slightly different than the volume given)
        if abs(volume - mixer.music.get_volume()) > self._VOLUME_TOLERANCE:
            print(f"Setting volume to {volume}")
            mixer.music.set_volume(volume)

        # The super class handles playing/pausing the audio
        super()._on_firestore_change(document_snapshot, changes, read_time)

    def _set_output_is_on(self, is_on):
        """
            Pause or unpause the audio base on {is_on}
            Overrides the super class
        """
        if is_on:
            mixer.music.unpause()
        else:
            mixer.music.pause()

    def _load_random_audio(self):
        """
            Loads a new audio file chosen at random from the audio folder
        """
        file = random.choice(self._audio_files)

        print("Loading new audio file:", file)
        mixer.music.load(file)
        mixer.music.play()
        if not self._is_on:
            mixer.music.pause()

    def _handle_audio_finished(self):
        """
            Checks if the current audio file has finished and loads another if it has
        """
        if not mixer.music.get_busy() and self._is_on:
            print("Current audio file finished.")
            mixer.music.stop()
            mixer.music.unload()
            self._load_random_audio()

    def handler(self):
        """
            Should be called periodically to handle any periodic processing
            by the audio handler
        """
        self._handle_audio_finished()

    def cleanup(self):
        """
            Cleans up the resources used by the controller
        """
        super().cleanup()
        mixer.quit()
