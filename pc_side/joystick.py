import paho.mqtt.client as mqtt

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

# broker='localhost'
broker='192.168.0.102'
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
client.will_set('botcmd/stop','1')
client.connect(broker)
client.loop_start()

last_accl=0
c=0
while True:
    time.sleep(0.1)
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            done=True

    if nos_joy!=0:
        left_right=controller.get_axis(2)
        fwd_rev=controller.get_axis(1)
        hat_lr=controller.get_hat(0)
        trig_btn=controller.get_button(0)
        left_right=round(left_right,3)
        fwd_rev=round(fwd_rev,3)
        btn7=controller.get_button(6)
        btn11=controller.get_button(10)
        btn8=controller.get_button(7)
        btn12=controller.get_button(11)
        btn2=controller.get_button(1)
        accl_knob=round(-controller.get_axis(3),1)

        btn_ul=controller.get_button(4)
        btn_ur=controller.get_button(5)

        if(btn7 and btn11 and btn2):
            client.publish('joystick/lifter','down')
            # print('Down')
        if(btn8 and btn12 and btn2):
            client.publish('joystick/lifter','up')
            # print('Up')
        if trig_btn==1:
            client.publish('joystick/cam_rst',str(trig_btn))
            # print(trig_btn)
        if hat_lr==(0,1) or hat_lr==(0,-1):
            client.publish('joystick/cam_up_down',str(hat_lr[1]))
            # print(hat_lr[1])
        if(accl_knob!=last_accl):
            client.publish('joystick/accl',str(accl_knob))

        if(btn_ul):
            client.publish('auto_entry','0')
        elif(btn_ur):
            client.publish('auto_entry','1')

        if(left_right==0 and fwd_rev==0):
            if(c<3):
                client.publish('botcmd/stop','1')
                c=c+1

        else:
            c=0
            if (left_right<-0.25 or left_right>0.25):
                client.publish('joystick/lr',str(left_right))
            elif (left_right>-0.25 and left_right<0.25):
                client.publish('joystick/lr','0')

            if (fwd_rev<-0.15 or fwd_rev>0.15):
                client.publish('joystick/fwrev',str(fwd_rev))
            elif(fwd_rev>-0.15 and fwd_rev<0.15):
                client.publish('joystick/fwrev','0')
            client.publish('joystick/xy',str(left_right)+':'+str(fwd_rev))
        last_accl=accl_knob