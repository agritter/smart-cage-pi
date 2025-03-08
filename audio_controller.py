from firestore import Firestore
from switch_controller_with_modes import SwitchControllerWithModes
from switch import Switch
import random
import os
import miniaudio
import alsaaudio


class AudioController(SwitchControllerWithModes):
    """ Plays audio based on the current mode in Firestore and switch value """
    _VOLUME_KEY = "volume"
    _AUDIO_DIRECTORY = "./audio"
    _VOLUME_TOLERANCE = 0.01

    _AUDIO_TYPE_KEY = "type"
    _AUDIO_TYPE_BUDGIES = "budgies"
    _AUDIO_TYPE_80S = "eighties"
    _AUDIO_TYPE_LATIN = "latin"
    _AUDIO_TYPE_JAZZ = "jazz"

    def __init__(self, switch: Switch, firestore: Firestore):
        """
            Initializes the controller to control audio using the {switch} and the mode and volume in {firestore}
        """
        self._firestore = firestore
        # Get the paths of the files in the audio directory
        self._audio_files = list(map(lambda file: os.path.join(
            self._AUDIO_DIRECTORY, file), os.listdir(self._AUDIO_DIRECTORY)))
        self._device = miniaudio.PlaybackDevice()

        self._mixer = alsaaudio.Mixer()

        self._audio_type = self._AUDIO_TYPE_BUDGIES

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
        volume = document_snapshot[0].get(self._VOLUME_KEY)
        if (volume != self._mixer.getvolume()[0]):
            print(f"Setting volume to {volume}")
            self._mixer.setvolume(volume)

        # Change the audio type if changed
        audio_type = document_snapshot[0].get(self._AUDIO_TYPE_KEY)
        if audio_type != self._audio_type:
            print(f"Setting audio type to {audio_type}")
            self._audio_type = audio_type
            if self._is_on:
                self._device.stop()
                self._start_stream()

        # The super class handles playing/pausing the audio
        super()._on_firestore_change(document_snapshot, changes, read_time)

    def _set_output_is_on(self, is_on):
        """
            Pause or unpause the audio base on {is_on}
            Overrides the super class
        """
        if is_on:
            self._start_stream()
        else:
            self._device.stop()

    def _start_stream(self):
        try:
            if self._audio_type == self._AUDIO_TYPE_80S:
                stream = self._icecast_stream(
                    "https://stream.mybroadbandradio.com/80srhythmhq")
            elif self._audio_type == self._AUDIO_TYPE_LATIN:
                stream = self._icecast_stream(
                    "http://s37.derstream.net/latinofm.mp3")
            elif self._audio_type == self._AUDIO_TYPE_JAZZ:
                stream = self._icecast_stream(
                    "http://relay.publicdomainradio.org/jazz_swing.mp3")
            else:  # self._AUDIO_TYPE_BUDGIES
                stream = self._random_local_audio_stream()
                next(stream)

            self._device.start(stream)
        except:
            print("Problem starting stream")
            self._set_output_is_on(False)

    def _random_local_audio_stream(self):
        while True:
            file = random.choice(self._audio_files)
            print("Playing new audio file:", file)
            stream = miniaudio.stream_file(file)

            frame_count = yield b""
            try:
                while True:
                    yield stream.send(frame_count)
            except StopIteration:
                pass

    def _icecast_stream(self, url):
        icecast = miniaudio.IceCastClient(url)
        return miniaudio.stream_any(icecast, icecast.audio_format)

    def cleanup(self):
        """
            Cleans up the resources used by the controller
        """
        super().cleanup()
        self._device.close()
