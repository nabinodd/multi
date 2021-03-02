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

def clamp(value):
    return max(min(1, value), 0)

SAMPLETIME = 0.2

# KP = 0.02
# KD = 0.01
# KI = 0.005

KP = 0.02
KD = 0.01
KI = 0.005



# r = Robot((3,2), (15,14)) 
# # r = Robot((2,3), (14,15)) 

# e1 = Encoder(17)
# e2 = Encoder(27)

# m1_speed = 0.1
# m2_speed = 0.1
# r.value = (m1_speed, m2_speed)

e1_prev_error = 0
e2_prev_error = 0

e1_sum_error = 0
e2_sum_error = 0



# while True:
# def calc_pid(target,m1_speed,m2_speed):
#     global e1_prev_error,e2_prev_error,e1_sum_error,e2_sum_error

#     e1_error = target - e1.value
#     e2_error = target - e2.value

#     m1_speed += (e1_error * KP) + (e1_prev_error * KD) + (e1_sum_error * KI)
#     m2_speed += (e2_error * KP)  + (e1_prev_error * KD) + (e2_sum_error * KI)

#     m1_speed = max(min(1, m1_speed), 0)
#     m2_speed = max(min(1, m2_speed), 0)
#     # r.value = (m1_speed, m2_speed)

#     # print("e1 {} e2 {}".format(e1.value, e2.value))
#     # print("m1 {} m2 {}".format(m1_speed, m2_speed))

#     e1.reset()
#     e2.reset()

#     sleep(SAMPLETIME)

#     e1_prev_error = e1_error
#     e2_prev_error = e2_error

#     e1_sum_error += e1_error
#     e2_sum_error += e2_error
    
#     return(m1_speed,m2_speed)
e1=Encoder(14)
while True:
    print(e1.value)
    e1.reset()
    sleep(0.5)