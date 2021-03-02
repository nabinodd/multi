import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)

class Ultrasonic(object):


    def __init__(self,trigger_pin,echo_pin):
        self.trigger_pin=trigger_pin
        self.echo_pin=echo_pin

        gpio.setup(trigger_pin,gpio.OUT)
        gpio.setup(echo_pin,gpio.IN)


    def get_distance(self):
        gpio.output(self.trigger_pin, False)                   
        gpio.output(self.trigger_pin, True)                 
        time.sleep(0.00011)                     
        gpio.output(self.trigger_pin, False)                
        while gpio.input(self.echo_pin)==0:               
            pulse_start = time.time()              
        while gpio.input(self.echo_pin)==1:              
            pulse_end = time.time()                
        pulse_duration = pulse_end - pulse_start 
        distance = (pulse_duration * 340)/2                  
        time.sleep(0.05)
        distance=distance*100
        return round(distance+2.7,2)

if __name__ == "__main__":
    us1=Ultrasonic(27,22)
    us2=Ultrasonic(20,21)
    us3=Ultrasonic(19,26)
    us4=Ultrasonic(6,13)
    while True: 
        u1=us1.get_distance()
        u2=us2.get_distance()
        u3=us3.get_distance()
        u4=us4.get_distance()

        print('U1 : ',u1,' U2 : ',u2,' U3 : ',u3,' U4 : ',u4)
        # time.sleep(0.01)
    