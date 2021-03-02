import paho.mqtt.client as mqtt
from gpiozero import Motor
import threading
import time
import ultrasonic as us
# motl = Motor(2, 3)
# motr= Motor(14, 15)
motl = Motor(3, 2)
motr= Motor(15, 14)

joys_pos=[]
lr_pos_r=0
fwrev_pos_r=0

l_stop_val=0
r_stop_val=0

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe('joystick/lr')
    client.subscribe('joystick/fwrev')
   
def on_message(client, userdata, msg):
    global joys_pos,lr_pos_r,fwrev_pos_r

    if msg.topic=='joystick/fwrev':
        fwrev_pos_r=float(msg.payload.decode())
    
    if msg.topic=='joystick/lr':
        lr_pos_r=float(msg.payload.decode())

        # data=msg.payload.decode()
        # joys_pos=data.split(',')
        # lr_pos_r=float(joys_pos[0])
        # fwrev_pos_r=float(joys_pos[1])


def client_loop():
    global client
    while True:
        client.loop()

def motor_stop():
    # for i in range(1,99,1):
    #     l_pwr=l_stop_val-i/100
    #     r_pwr=r_stop_val-i/100

    #     if(l_pwr<0 or l_pwr>1):
    #         pass
    #     else:
    #         motl.forward(l_pwr)

    #     if(r_pwr<0 or r_pwr>1):
    #         pass
    #     else:
    #         motr.forward(r_pwr)

    motl.stop()
    motr.stop()
    print('Stop')


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('192.168.100.235', 1883, 60)

threading.Thread(target=client_loop,daemon=True).start()

while True:
    lr_pos=lr_pos_r
    fwrev_pos=fwrev_pos_r
    lr_pos_r=0
    fwrev_pos_r=0
    time.sleep(0.1)
    if lr_pos==0 and fwrev_pos<0: #forward
        motl.forward(speed=-fwrev_pos)
        motr.forward(speed=-fwrev_pos)
       
        l_stop_val=-fwrev_pos
        r_stop_val=-fwrev_pos

        print('Forward : ',-fwrev_pos)

    elif lr_pos==0 and fwrev_pos>0: #reverse
        if us.get_distance()<50:
            print('[STOP] Obstacle detected')
            motor_stop()
        else: 
            print('Reverse : ',fwrev_pos)
            motl.backward(speed=fwrev_pos)
            motr.backward(speed=fwrev_pos)
 
            l_stop_val=fwrev_pos
            r_stop_val=fwrev_pos

    elif lr_pos<0 and fwrev_pos==0: #left
        motl.backward(-lr_pos)
        motr.forward(-lr_pos)
 
        l_stop_val=-lr_pos
        r_stop_val=-lr_pos

        print('Left : ',lr_pos)
    
    elif lr_pos>0 and fwrev_pos==0: #right
        motl.forward(lr_pos)
        motr.backward(lr_pos)   
        
        l_stop_val=lr_pos
        r_stop_val=lr_pos

        print('Right : ',lr_pos)

    elif lr_pos<0 and fwrev_pos<0: # forward left
        if -lr_pos>-fwrev_pos:
            r_power=-lr_pos
            l_power=-fwrev_pos

        elif -lr_pos<-fwrev_pos:
            r_power=-fwrev_pos
            l_power=-lr_pos

        motl.forward(l_power)
        motr.forward(r_power)

        l_stop_val=l_power
        r_stop_val=r_power

        print('Forward Left')
        print('Mot L : ',l_power,' Mot R : ',r_power)

    elif lr_pos>0 and fwrev_pos<0: # forward right
        if lr_pos>-fwrev_pos:
            r_power=-fwrev_pos
            l_power=lr_pos
              
        elif lr_pos<-fwrev_pos:
            r_power=lr_pos
            l_power=-fwrev_pos

        motl.forward(l_power)
        motr.forward(r_power)

        l_stop_val=l_power
        r_stop_val=r_power

        print('Forward Right')
        print('Mot L : ',l_power,' Mot R : ',r_power)

    elif lr_pos<0 and fwrev_pos>0: # backward left
        if -lr_pos>fwrev_pos:
            r_power=-lr_pos
            l_power=fwrev_pos
              
        elif -lr_pos<fwrev_pos:
            r_power=fwrev_pos
            l_power=-lr_pos
        if us.get_distance()<50:
            print('[STOP] Obstacle detected')
            motor_stop()
        else: 
            motl.backward(l_power)
            motr.backward(r_power)

            l_stop_val=l_power
            r_stop_val=r_power

            print('Backward Left')
            print('Mot L : ',l_power,' Mot R : ',r_power)

    elif lr_pos>0 and fwrev_pos>0: # backward right
        if lr_pos>fwrev_pos:
            r_power=fwrev_pos
            l_power=lr_pos  
        elif lr_pos<fwrev_pos:
            r_power=lr_pos
            l_power=fwrev_pos
        if us.get_distance()<50:
            print('[STOP] Obstacle detected')
            motor_stop()
        else: 
            motl.backward(l_power)
            motr.backward(r_power)

            l_stop_val=l_power
            r_stop_val=r_power

            print('Backward Right')
            print('Mot L : ',l_power,' Mot R : ',r_power)

    elif lr_pos==0 and fwrev_pos==0: # stop
        motor_stop()

