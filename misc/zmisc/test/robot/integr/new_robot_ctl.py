import paho.mqtt.client as mqtt
from gpiozero import Motor
import threading
import time

motl = Motor(2, 3)
motr= Motor(14, 15)

joys_pos=[]

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe('joystick/nav_pos')
   
def on_message(client, userdata, msg):
    global joys_pos,lr_pos,fwrev_pos
    if msg.topic=='joystick/nav_pos':
        data=msg.payload.decode()
        joys_pos=data.split(',')
        lr_pos=float(joys_pos[0])
        fwrev_pos=float(joys_pos[1])

def client_loop():
    global client
    while True:
        client.loop()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('192.168.100.214', 1883, 60)

threading.Thread(target=client_loop,daemon=True).start()

lr_pos=0
fwrev_pos=0

while True:
    time.sleep(0.1)
    if lr_pos==0 and fwrev_pos<0: #forward
        motl.forward(speed=-fwrev_pos)
        motr.forward(speed=-fwrev_pos)
        print('Forward : ',-fwrev_pos)

    elif lr_pos==0 and fwrev_pos>0: #reverse
        motl.backward(speed=fwrev_pos)
        motr.backward(speed=fwrev_pos)
        print('Reverse')

    elif lr_pos<0 and fwrev_pos==0: #left
        motl.backward(-lr_pos)
        motr.forward(-lr_pos)
        print('Left : ',lr_pos)
    
    elif lr_pos>0 and fwrev_pos==0: #right
        motl.forward(lr_pos)
        motr.backward(lr_pos)   
        print('Right : ',lr_pos)

    elif lr_pos<0 and fwrev_pos<0: # forward left
        l_power=1+lr_pos
        r_power=-fwrev_pos
        motl.forward(l_power)
        motr.forward(r_power)
        print('Forward Left')
        print('Mot L : ',l_power,' Mot R : ',r_power)

    elif lr_pos>0 and fwrev_pos<0: # forward right
        motl.forward(-fwrev_pos)
        motr.forward(1-lr_pos)
        print('Mot L : ',-fwrev_pos,' Mot R : ',1-lr_pos)

    elif lr_pos<0 and fwrev_pos>0: # backward left
        motl.backward(1+lr_pos)
        motr.backward(fwrev_pos)
        print('Backward left')
    elif lr_pos>0 and fwrev_pos>0: # backward right
        motl.backward(fwrev_pos)
        motr.backward(1-lr_pos)
        print('Backward right')
    elif lr_pos==0 and fwrev_pos==0: # stop
        motl.stop()
        motr.stop()
        print('Stop')
    lr_pos=0
    fwrev_pos=0


