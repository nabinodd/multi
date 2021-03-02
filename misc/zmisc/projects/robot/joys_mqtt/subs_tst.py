import paho.mqtt.client as mqtt
from gpiozero import Motor

motl = Motor(13, 19)
motr= Motor(18, 12)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe('joystick/left_right')
    client.subscribe('joystick/forward_reverse')

def on_message(client, userdata, msg):
    if msg.topic=='joystick/left_right':
        lr_val=float(msg.payload.decode())
        if lr_val>0:
            print('Go right')
            motl.forward()
            motr.stop()
        elif lr_val<0:
            print('Go left')
            motl.stop()
            motr.forward()
        
    if msg.topic=='joystick/forward_reverse':
        fwrev_val=float(msg.payload.decode())
        if fwrev_val>0:
            print('Go back')
            motl.backward()
            motr.backward()
            motl.forward()
            motr.forward()
        
            motl.forward()
            motr.forward()
        
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('192.168.1.14', 1883, 60)
client.loop_forever()

