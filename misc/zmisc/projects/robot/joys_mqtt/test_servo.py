from gpiozero import AngularServo
import time

cam_servo = AngularServo(5, min_angle=0, max_angle=180, min_pulse_width=0.0006, max_pulse_width=0.0024)

while True:
    for i in range(80,120):
        cam_servo.angle=i
        print('Fwd : ',i)
        time.sleep(0.1)

    for i in range(120,80,-1):
        cam_servo.angle=i
        print('Rev : ',i)
        time.sleep(0.1)