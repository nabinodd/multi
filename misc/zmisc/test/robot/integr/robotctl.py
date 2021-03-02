import paho.mqtt.client as mqtt
from gpiozero import Motor
import ultrasonic as us

motl = Motor(2, 3)
motr= Motor(14, 15)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe('joystick/left_right')
    client.subscribe('joystick/forward_reverse')
    client.subscribe('joystick/stop')

def on_message(client, userdata, msg):
 
    if msg.topic=='joystick/left_right':
        lr_val=float(msg.payload.decode())
        if lr_val>0.15:
            print('Go right : ',lr_val)
            motl.forward(speed=lr_val)
            motr.backward(speed=lr_val)
        elif lr_val< -0.15:
            print('Go left : ',-lr_val)
            motl.backward(speed=-lr_val)
            motr.forward(speed=-lr_val)
        
    if msg.topic=='joystick/forward_reverse':
        fwrev_val=float(msg.payload.decode())
        if fwrev_val>0.15:
            if us.get_distance()<50:
                print('[STOP] Obstacle detected')
                motl.stop()
                motr.stop()
                return 
            else:            
                print('Go back : ',fwrev_val)
                motl.backward(speed=fwrev_val)
                motr.backward(speed=fwrev_val)
            
        elif fwrev_val<-0.15:
            print('Go forward : ',-fwrev_val)
            motl.forward(speed=-fwrev_val)
            motr.forward(speed=-fwrev_val)
      
    if msg.topic=='joystick/stop':
        print('Motor Stop')
        motl.stop()
        motr.stop()



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('192.168.100.214', 1883, 60)
client.loop_forever()
