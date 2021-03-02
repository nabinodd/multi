import matplotlib.pyplot as plt
import pygame
import time
import math

pygame.init()
nos_joy=pygame.joystick.get_count()

if nos_joy==0:
    print('[ERR] No Joystick found')
else:
    print('Joysticks : ',pygame.joystick.get_count())
    controller=pygame.joystick.Joystick(0)
    controller.init()
    print('[INF] Controller initalized')


def map(v, in_min=0, in_max=2.0, out_min=0, out_max=1.0):
	# Check that the value is at least in_min
	if v < in_min:
		v = in_min
	# Check that the value is at most in_max
	if v > in_max:
		v = in_max
	return (v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


while True:
    time.sleep(0.1)
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            done=True
    if nos_joy!=0:
        x=round(controller.get_axis(2),3)
        y=round(controller.get_axis(1),3)

        if x==0 and y<0:
            y=-y
            print('Forward >> L : ',y,' R : ',y)

        elif x<0 or y<0:
            x=-x
            y=-y
            l_pwr=y-x
            r_pwr=y+x
            l_pwr=round(map(l_pwr),3)
            r_pwr=round(map(r_pwr),3)

            if l_pwr>r_pwr:
                print('FwRight >> L : ',l_pwr,' R : ',r_pwr)
            
            elif l_pwr<r_pwr:
                print('FwLeft >> L : ',l_pwr,' R : ',r_pwr)

        elif x==0 and y>0:
            print('Backward >> L : ',y,' R : ',y)

