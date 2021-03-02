import RPi.GPIO as gpio                   

import time   

gpio.setmode(gpio.BCM)                     

trigger_pin =4                                   
echo_pin = 23                              

gpio.setup(trigger_pin,gpio.OUT)              
gpio.setup(echo_pin,gpio.IN)                   

def get_distance():
    gpio.output(trigger_pin, False)                   
    gpio.output(trigger_pin, True)                 
    time.sleep(0.00011)                     
    gpio.output(trigger_pin, False)                
    while gpio.input(echo_pin)==0:               
        pulse_start = time.time()              
    while gpio.input(echo_pin)==1:              
        pulse_end = time.time()                
    pulse_duration = pulse_end - pulse_start 
    distance = (pulse_duration * 340)/2                  
    time.sleep(0.05)
    distance=distance*100
    return round(distance+2.7,2)
    
if __name__ == "__main__":
    while True:
        print('Distance : ',round(get_distance(),2))
        time.sleep(0.1)