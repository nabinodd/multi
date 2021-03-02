import paho.mqtt.client as mqtt
from encoder import Encoder
from gpiozero import Motor
from simple_pid import PID
import threading
import time


broker='192.168.0.102'
client=mqtt.Client('dataPubr')

def on_log(client,userdata,level,buf):
    print('log: '+buf)

def on_connect(client,userdata,flags,rc):
    if rc==0:
        print('Connected OK')
    else:
        print('Not connected : ',rc)


client.on_connect=on_connect
# client.on_log=on_log

print('Connecting to broker : ',broker)
client.connect(broker)

client.loop_start()

pid_sample_time = 0.1
encoder_sample_time=60

KP = 0.5
KI =0
KD = 0

sp=8

lpid=PID(Kp=KP,Ki=KI,Kd=KD,setpoint=sp,sample_time=pid_sample_time,output_limits=(0,1),auto_mode=True)
rpid=PID(Kp=KP,Ki=KI,Kd=KD,setpoint=sp,sample_time=pid_sample_time,output_limits=(0,1),auto_mode=True)

motl_a_pin=4
motl_b_pin=12
motr_a_pin=1
motr_b_pin=15
servo_pin=14

enc_l_pin=18
enc_r_pin=0
enc_l_rate=0
enc_r_rate=0


motl= Motor(motl_a_pin,motl_b_pin)
motr = Motor(motr_a_pin, motr_b_pin)

el=Encoder(enc_l_pin)
er=Encoder(enc_r_pin)

motl.forward(1)
# motr.forward(0.2)
l_pwr=0
def get_encoder_reading():
    global enc_l_rate,enc_r_rate,l_pwr
    while True:
        enc_l_rate=el.value
        enc_r_rate=er.value
        print('L : ',enc_l_rate)
        el.reset()
        er.reset()
        time.sleep(encoder_sample_time)
        
threading.Thread(target=get_encoder_reading,daemon=True).start()

while True:
    l_pwr=lpid(enc_l_rate)
    # motl.forward(l_pwr)
    client.publish('y',str(enc_l_rate))
    time.sleep(0.1)