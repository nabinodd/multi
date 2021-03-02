import paho.mqtt.client as mqtt
import threading
import pygame
import time


pygame.init()
print('\n\n')

nos_joy=pygame.joystick.get_count()

if nos_joy==0:
    print('[ERR] No Joystick found')
else:
    print('Joysticks : ',pygame.joystick.get_count())
    controller=pygame.joystick.Joystick(0)
    controller.init()
    print('[INF] Controller initalized')

broker='localhost'
client=mqtt.Client('client1')


def on_log(client,userdata,level,buf):
    print('log: '+buf)

def on_connect(client,userdata,flags,rc):
    if rc==0:
        print('Connected OK')
    else:
        print('Not connected : ',rc)


client.on_connect=on_connect
client.on_log=on_log

print('Connecting to broker : ',broker)
client.connect(broker)

client.loop_start()

while True:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            done=True
    if nos_joy!=0:
        time.sleep(0.1)
        left_right=controller.get_axis(0)
        fwd_rev=controller.get_axis(1)
        # bttn_knob=controller.get_axis(2)
        # plus_minus=controller.get_axis(3)
        # trigg_btn=controller.get_button(0)
        # thumb_btn=controller.get_button(1)
    
        if left_right!=0:
            client.publish('joystick/left_right',str(left_right))
            print('LR : ',left_right)

        if fwd_rev!=0:
            client.publish('joystick/forward_reverse',str(fwd_rev))
        
        if left_right==0 and fwd_rev==0:
            client.publish('joystick/stop','1')