import RPi.GPIO as gpio                   
import time                                
gpio.setmode(gpio.BCM)                     

TRIG =4                                   
ECHO = 23                              

gpio.setup(TRIG,gpio.OUT)              
gpio.setup(ECHO,gpio.IN)                   

def get_distance():
    gpio.output(TRIG, False)                   
    gpio.output(TRIG, True)                 
    time.sleep(0.00011)                     
    gpio.output(TRIG, False)                
    while gpio.input(ECHO)==0:               
        pulse_start = time.time()              
    while gpio.input(ECHO)==1:              
        pulse_end = time.time()                
    pulse_duration = pulse_end - pulse_start 
    distance = (pulse_duration * 340)/2                  
    time.sleep(0.05)
    distance=distance*100
    return distance+2.7

while True:
    print(round(get_distance(),2))
    time.sleep(0.1)