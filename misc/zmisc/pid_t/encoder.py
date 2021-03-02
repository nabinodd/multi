from gpiozero import DigitalInputDevice, Robot
from time import sleep

class Encoder(object):
    def __init__(self, pin):
        self._value = 0

        self.encoder = DigitalInputDevice(pin)
        self.encoder.when_activated = self._increment
        self.encoder.when_deactivated = self._increment
        
    def reset(self):
        self._value = 0

    def _increment(self):
        self._value += 1

    @property
    def value(self):
        return self._value

if __name__ == "__main__":
    e1=Encoder(0)
    e2=Encoder(18)

    while True:
        enc_l=e2.value
        enc_r=e1.value
        diff=enc_r-enc_l
        print('EL : ',enc_l,'ER : ',enc_r)
        print('Diff : ',diff)
        e2.reset()
        e1.reset()
        sleep(0.2)
        #25