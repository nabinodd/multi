
import sys
import time
import random
import pigpio

servo_pin=14

MIN_WIDTH=500
MAX_WIDTH=2200


pi = pigpio.pi()

if not pi.connected:
   exit()

while True:
    try:
        for i in range(MIN_WIDTH,MAX_WIDTH):
        # p=int(input('Pulse in us : '))
        # if p>=500 and p<=2500:
            pi.set_servo_pulsewidth(servo_pin,i)
            print('Wrote : ',i)
            time.sleep(0.011)
        for i in range(MAX_WIDTH,MIN_WIDTH,-1):
        # p=int(input('Pulse in us : '))
        # if p>=500 and p<=2500:
            pi.set_servo_pulsewidth(servo_pin,i)
            print('Wrote : ',i)
            time.sleep(0.011)
    except KeyboardInterrupt:
        break

print("\nTidying up")
pi.set_servo_pulsewidth(servo_pin, 0)
pi.stop()
