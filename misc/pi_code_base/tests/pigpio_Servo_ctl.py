
import sys
import time
import random
import pigpio

servo_pin=14

MIN_WIDTH=500
MAX_WIDTH=2499


pi = pigpio.pi()

if not pi.connected:
    exit()

while True:
    # p=int(input('Pulse in us : '))
    try:
        for i in range(MIN_WIDTH,MAX_WIDTH,1):
            pi.set_servo_pulsewidth(servo_pin,i)
            print('Wrote : ',i)
            time.sleep(0.01)

        for i in range(MAX_WIDTH,MIN_WIDTH,-1):
            pi.set_servo_pulsewidth(servo_pin,i)
            print('Wrote : ',i)
            time.sleep(0.01)
    except KeyboardInterrupt:
        break

print("\nTidying up")
pi.set_servo_pulsewidth(14, 0)
pi.stop()