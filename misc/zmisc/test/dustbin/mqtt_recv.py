import paho.mqtt.client as mqtt



def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe('dustbin/db1') 

def on_message(client, userdata, msg):
    if msg.topic=='dustbin/db1':
        db_data=msg.payload.decode()
        print('Data : ',db_data)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('192.168.100.214', 1883, 60)
client.loop_forever()
