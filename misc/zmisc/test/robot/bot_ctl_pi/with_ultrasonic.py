from gpiozero import Motor
import ultrasonic as us

while True:
    print(us.get_distance())