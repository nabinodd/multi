import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)

class Ultrasonic(object):
    pulse_start=pulse_end=0

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
            self.pulse_start = time.time()              
        while gpio.input(self.echo_pin)==1:              
            self.pulse_end = time.time()                
        pulse_duration = self.pulse_end - self.pulse_start 
        distance = (pulse_duration * 340)/2                  
        time.sleep(0.05)
        distance=distance*100
        return round(distance+2.7,2)

if __name__ == "__main__":
    us_fl=Ultrasonic(27,22)
    us_br=Ultrasonic(20,21)
    us_fr=Ultrasonic(19,26)
    us_bl=Ultrasonic(6,13)
    while True: 
        ubl=us_bl.get_distance()
        ubr=us_br.get_distance()
        ufr=us_fr.get_distance()
        ufl=us_fl.get_distance()
        print('U_FL : ',ufl,' U_FR : ',ufr,' UBL : ',ubl,' UBR : ',ubr)