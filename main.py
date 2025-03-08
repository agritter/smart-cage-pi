from audio_controller import AudioController
from firestore import Firestore
from light import Light
from light_controller import LightController
from switch import Switch
import pigpio
import signal

# Constants
LED_PIN = 16
AUDIO_SWITCH_PIN = 23
LIGHT_SWITCH_PIN = 24

pi = pigpio.pi()
audio_switch = Switch(pi, AUDIO_SWITCH_PIN)
light_switch = Switch(pi, LIGHT_SWITCH_PIN)
light = Light(pi, LED_PIN)
firestore = Firestore()
light_controller = LightController(light_switch, light, firestore)
audio_controller = AudioController(audio_switch, firestore)

try:
    signal.pause()
except KeyboardInterrupt:
    light_controller.cleanup()
    audio_controller.cleanup()
    audio_switch.cleanup()
    light_switch.cleanup()
    firestore.cleanup()
    pi.stop()
