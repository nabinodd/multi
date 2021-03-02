import paho.mqtt.client as mqtt
import threading
import time

broker='192.168.100.53'
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

def lr_fn():
    while True:
        for i in range(-101,101):
            client.publish('joystick/lr',str(i))
            print('LR : ',i/100)
            time.sleep(0.2)

def fwrev_fn():
    while True:
        for i in range(-101,101):
            client.publish('joystick/fwrev',str(i))
            print('FwRev : ',i/100)
            time.sleep(0.3)


x=threading.Thread(target=lr_fn,daemon=True)
y=threading.Thread(target=fwrev_fn,daemon=True)

time.sleep(0.5)
x.start()
time.sleep(0.3)
y.start()
x.join()
y.join()


# while True:
#     for i in range(0,101):
#         print(i/100)
#         time.sleep(0.1)
 