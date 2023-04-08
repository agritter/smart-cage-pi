from firestore import Firestore
from light import Light
from switch import Switch
from light_controller import LightController
from audio_controller import AudioController
import pigpio
import time


LED = 16
AUDIOSWITCH = 24
LIGHTSWITCH = 23

pi = pigpio.pi()

audioSwitch = Switch(pi, AUDIOSWITCH)
lightSwitch = Switch(pi, LIGHTSWITCH)
light = Light(pi, LED)
firestore = Firestore()
lightController = LightController(lightSwitch, light, firestore)
audioController = AudioController(audioSwitch, firestore)

try:
    while True:
        time.sleep(1)
        audioController.handler()
except KeyboardInterrupt:
    lightController.cleanup()
    audioSwitch.cleanup()
    lightSwitch.cleanup()
    pi.stop()
