import paho.mqtt.client as mqtt
import encoder_pid as epid

from gpiozero import Motor

import threading
import time
# import ultrasonic as us
import math
# motl = Motor(2, 3)
# motr= Motor(14, 15)
motl = Motor(3, 2)
motr= Motor(15, 14)

lr_pos_r=0
fwrev_pos_r=0


def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))

	client.subscribe('joystick/lr')
	client.subscribe('joystick/fwrev')
	client.subscribe('joystick/accl')

	client.subscribe('joystick/cam_rst')
	client.subscribe('joystick/cam_up_down')
   
def on_message(client, userdata, msg):
	global lr_pos_r,fwrev_pos_r,accl_val

	if msg.topic=='joystick/fwrev':
		fwrev_pos_r=float(msg.payload.decode())

	if msg.topic=='joystick/lr':
		lr_pos_r=float(msg.payload.decode())

	if msg.topic=='joystick/accl':
		accl_val=float(msg.payload.decode())

	if msg.topic=='joystick/cam_rst':
		cam_rst_val=msg.payload.decode()
		print('Cam rst val : ',cam_rst_val)

	if msg.topic=='joystick/cam_up_down':
		cam_up_down_val=msg.payload.decode()
		print('Cam up_down val : ',cam_up_down_val)
	
def run_motor(left,right,lm,rm):
	global motl,motr
	
	if lm=='F':
		motl.forward(speed=left)
	elif lm=='R':
		motl.backward(speed=left)
	elif lm=='S':
		motl.stop()
	if rm=='F':
		motr.forward(speed=right)
	elif rm=='R' :
		motr.backward(speed=right)
	elif rm=='S':
		motr.stop()


def client_loop():
    global client
    while True:
        client.loop()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('192.168.100.235', 1883, 60)

threading.Thread(target=client_loop,daemon=True).start()


def map(v, in_min=0, in_max=2.0, out_min=0, out_max=1.0):
	if v < in_min:
		v = in_min
	if v > in_max:
		v = in_max
	return (v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


while True:
	lr_pos=lr_pos_r
	fwrev_pos=fwrev_pos_r

	time.sleep(0.01)

	if(lr_pos==0 and fwrev_pos==0):
		print('Stop')
		motl.stop()
		motr.stop()

	elif (lr_pos==0 and fwrev_pos<0):
		fwrev_pos=map(-fwrev_pos+accl_val)
		target=int(map(fwrev_pos,in_max=1,out_max=12))
		
		l_mtr,r_mtr=epid.calc_pid(target,fwrev_pos,fwrev_pos)
		print(l_mtr,r_mtr)
		
		# run_motor(fwrev_pos,fwrev_pos,'F','F')
		
		run_motor(l_mtr,r_mtr,'F','F')

		# print('Forward : ',fwrev_pos)

	elif (lr_pos==0 and fwrev_pos>0):
		fwrev_pos=map(fwrev_pos+accl_val)

		target=int(map(fwrev_pos,in_max=1,out_max=12))
		l_mtr,r_mtr=epid.calc_pid(target,fwrev_pos,fwrev_pos)
		print(l_mtr,r_mtr)


		# run_motor(fwrev_pos,fwrev_pos,'R','R')

		run_motor(l_mtr,r_mtr,'R','R')

		# print('Backward : ',fwrev_pos)

	elif (lr_pos<0 and fwrev_pos==0):
		lr_pos=map(-lr_pos+accl_val)
		run_motor(lr_pos,lr_pos,'R','F')
		print('Left : ',lr_pos)

	elif (lr_pos>0 and fwrev_pos==0):
		lr_pos=map(lr_pos+accl_val)
		run_motor(lr_pos,lr_pos,'F','R')
		print('Right : ',lr_pos)



	elif (lr_pos<0 and fwrev_pos<0):
		lr_pos=-lr_pos
		fwrev_pos=-fwrev_pos

		l_pwr=round((fwrev_pos-lr_pos),3)
		if(l_pwr<0):
			l_pwr=0
		r_pwr=round(map(fwrev_pos+lr_pos),3)
		
		l_pwr=map(l_pwr+accl_val)
		r_pwr=map(r_pwr+accl_val)
		
		run_motor(l_pwr,r_pwr,'F','F')
		print('Forward Left : ',l_pwr,r_pwr)
		
	elif (lr_pos<0 and fwrev_pos>0):
		lr_pos=-lr_pos

		l_pwr=round((fwrev_pos-lr_pos),3)
		r_pwr=round(map(fwrev_pos+lr_pos),3)
		if l_pwr<0:
			l_pwr=0
		
		l_pwr=map(l_pwr+accl_val)
		r_pwr=map(r_pwr+accl_val)
		
		run_motor(l_pwr,r_pwr,'R','R')
		print('Backward Left : ',l_pwr,r_pwr)

	elif (lr_pos>0 and fwrev_pos<0):
		fwrev_pos=-fwrev_pos
		l_pwr=round(map(fwrev_pos+lr_pos),3)
		r_pwr=round((fwrev_pos-lr_pos),3)
		if r_pwr<0:
			r_pwr=0

		l_pwr=map(l_pwr+accl_val)
		r_pwr=map(r_pwr+accl_val)
		
		run_motor(l_pwr,r_pwr,'F','F')
		print('Forward Right : ',l_pwr,r_pwr)

	elif (lr_pos>0 and fwrev_pos>0):
		l_pwr=round(map(fwrev_pos+lr_pos),3)
		r_pwr=round((fwrev_pos-lr_pos),3)
		if r_pwr<0:
			r_pwr=0
		
		l_pwr=map(l_pwr+accl_val)
		r_pwr=map(r_pwr+accl_val)
		
		run_motor(l_pwr,r_pwr,'R','R')
		print('Backward Right : ',l_pwr,r_pwr)