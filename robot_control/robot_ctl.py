from gpiozero import OutputDevice
from ultrasonic import Ultrasonic
import paho.mqtt.client as mqtt
from encoder import Encoder
from gpiozero import Motor
import threading
import pigpio
import time

SAMPLETIME = 0.2
KP = 0.08
KI = 0.009
KD = 0

mqtt_server=('192.168.0.102',1883,60)
encoder_sample_time=0.2
enc_l_rate=0
enc_r_rate=0

########################PIN DEFS########################
ckt_trig_relay_pin=23
lift_up_relay_pin=5
lift_down_relay_pin=16
# motl_a_pin=4
# motl_b_pin=12
# motr_a_pin=1
# motr_b_pin=15

motl_a_pin=12
motl_b_pin=4
motr_a_pin=15
motr_b_pin=1

servo_pin=14
us_fl=Ultrasonic(27,22)
us_br=Ultrasonic(20,21)
us_fr=Ultrasonic(19,26)
us_bl=Ultrasonic(6,13)
enc_l_pin=18
enc_r_pin=0
########################PIN DEFS########################

########################OBJ INITS########################
ckt_trig_relay=OutputDevice(ckt_trig_relay_pin,active_high=False, initial_value=False)
motl= Motor(motl_a_pin,motl_b_pin)
motr = Motor(motr_a_pin, motr_b_pin)
lift_up_relay=OutputDevice(lift_up_relay_pin,active_high=False, initial_value=False)
lift_down_relay=OutputDevice(lift_down_relay_pin,active_high=False, initial_value=False)
pi=pigpio.pi()

el=Encoder(enc_l_pin)
er=Encoder(enc_r_pin)

########################OBJ INITS########################

########################START-UP INITS########################
ckt_trig_relay.on()
initial_servo_pos=2200
pi.set_servo_pulsewidth(servo_pin,initial_servo_pos)
########################START-UP INITS########################

########################ULTRASONIC########################
obstacle_distance=30
front_obstacle=False
back_obstacle=False
pingg=False
########################ULTRASONIC########################

########################SERVO########################
servo_reset_delay=0.01
max_servo_pos=2500
min_servo_pos=1200
servo_pos=initial_servo_pos
servo_reset_running=False
servo_up=False
servo_down=False
reset_servo_pos=False
########################SERVO########################

lr_pos_r=0
fwrev_pos_r=0
accl_val=0

mot_st=['S','S']

manual_auto='M'


def client_loop():
	global client
	while True:
		client.loop()

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))

	client.subscribe('joystick/lr')
	client.subscribe('joystick/fwrev')
	client.subscribe('joystick/accl')
	client.subscribe('joystick/cam_rst')
	client.subscribe('joystick/cam_up_down')
	client.subscribe('joystick/lifter')
	client.subscribe('auto_entry')
	client.subscribe('botcmd/stop')
	client.subscribe('aruco_cam/lr')
	client.subscribe('aruco_cam/fwrev')


def on_message(client, userdata, msg):
	global lr_pos_r,fwrev_pos_r,accl_val,servo_pos,initial_servo_pos,max_servo_pos,servo_up,servo_down,reset_servo_pos,pingg,manual_auto

	if msg.topic=='auto_entry':
		auto_entry_enable=msg.payload.decode()
		if manual_auto!='A' and auto_entry_enable=='1':
			manual_auto='A'
			run_motor()
			print('In automatic mode...')

		elif manual_auto!='M' and auto_entry_enable=='0':
			manual_auto='M'
			print('In manual mode')

	elif msg.topic=='joystick/accl':
		accl_val=float(msg.payload.decode())

	elif msg.topic=='botcmd/stop':
		run_motor()

	elif msg.topic=='joystick/lifter':
		lifter_cmd=msg.payload.decode()
		if lifter_cmd=='up':
			lift_up_relay.on()
			lift_down_relay.off()
			print('Going up')

		elif lifter_cmd=='down':
			print('Going down')
			lift_down_relay.on()
			lift_up_relay.off()

	elif msg.topic=='joystick/cam_rst':
		if servo_reset_running==False and servo_pos!=initial_servo_pos and reset_servo_pos==False:
			print('Going to reset')
			reset_servo_pos=True


	elif msg.topic=='joystick/cam_up_down':
		cam_up_down_val=msg.payload.decode()
		if servo_reset_running==False:
			if cam_up_down_val=='1' and servo_pos<max_servo_pos:
				servo_up=True
				servo_down=False
			elif cam_up_down_val=='-1' and servo_pos>min_servo_pos:
				servo_down=True
				servo_up=False

	if manual_auto=='M':
		if msg.topic=='joystick/fwrev':
			fwrev_pos_r=float(msg.payload.decode())
			if(fwrev_pos_r!=0):
				pingg=True

		elif msg.topic=='joystick/lr':
			lr_pos_r=float(msg.payload.decode())
			pingg=False

	elif manual_auto=='A':
		if msg.topic=='aruco_cam/fwrev':
			fwrev_pos_r=float(msg.payload.decode())
			if(fwrev_pos_r!=0):
				pingg=True

		elif msg.topic=='aruco_cam/lr':
			lr_pos_r=float(msg.payload.decode())
			pingg=False

client = mqtt.Client('robot_ctl')
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_server[0],mqtt_server[1],mqtt_server[2])

mtqq_thread=threading.Thread(target=client_loop,daemon=True)
mtqq_thread.start()

def read_ultrasonic():
	global us_fl_dist,us_fr_dist,us_bl_dist,us_br_dist,pingg,front_obstacle,back_obstacle
	while True:
		if pingg:
			us_fl_dist=us_fl.get_distance()
			us_fr_dist=us_fr.get_distance()
			us_bl_dist=us_bl.get_distance()
			us_br_dist=us_br.get_distance()
			pingg=False
			if(us_fl_dist<obstacle_distance or us_fr_dist<obstacle_distance):
				front_obstacle=True
			else:
				front_obstacle=False
			if(us_bl_dist<obstacle_distance or us_br_dist<obstacle_distance):
				back_obstacle=True
			else:
				back_obstacle=False
			ultrasonic_read=str(us_fl_dist)+','+str(us_fr_dist)+','+str(us_bl_dist)+','+str(us_br_dist)
			client.publish('ultrasonic',ultrasonic_read)
		time.sleep(0.1)

ultrasonic_thread=threading.Thread(target=read_ultrasonic,daemon=True)
ultrasonic_thread.start()

def servo_ctl():
	global servo_pos,servo_up,servo_down,servo_reset_running,reset_servo_pos
	while True:
		if servo_up==True:
			servo_pos=servo_pos+50
			pi.set_servo_pulsewidth(servo_pin,servo_pos)
			servo_up=False
		elif servo_down==True:
			servo_pos=servo_pos-50
			pi.set_servo_pulsewidth(servo_pin,servo_pos)
			servo_down=False

		if(reset_servo_pos):
			servo_reset_running=True
			if(servo_pos>initial_servo_pos):
				for i in range(servo_pos,initial_servo_pos,-5):
					pi.set_servo_pulsewidth(servo_pin,i)
					time.sleep(servo_reset_delay)
			elif (servo_pos<initial_servo_pos):
				for i in range(servo_pos,initial_servo_pos,5):
					pi.set_servo_pulsewidth(servo_pin,i)
					time.sleep(servo_reset_delay)
			servo_pos=initial_servo_pos
			# pi.set_servo_pulsewidth(servo_pin, 0)
			time.sleep(1)
			servo_reset_running=False
			reset_servo_pos=False
		time.sleep(0.1)
servo_thread=threading.Thread(target=servo_ctl,daemon=True)
servo_thread.start()

def get_encoder_reading():
    global enc_l_rate,enc_r_rate
    while True:
        enc_l_rate=el.value
        enc_r_rate=er.value
        el.reset()
        er.reset()
        time.sleep(encoder_sample_time)

threading.Thread(target=get_encoder_reading,daemon=True).start()

def run_motor(left=0,right=0,lm='S',rm='S'):
	global mot_st
	l_speed=map(left+accl_val)
	r_speed=map(right+accl_val)

	if lm=='F':
		motl.forward(speed=l_speed)
		mot_st[0]=lm

	elif lm=='R':
		motl.backward(speed=l_speed)
		mot_st[0]=lm

	elif lm=='S':
		motl.stop()
		mot_st[0]=lm

	if rm=='F':
		motr.forward(speed=r_speed)
		mot_st[1]=rm

	elif rm=='R':
		motr.backward(speed=r_speed)
		mot_st[1]=rm

	elif rm=='S':
		motr.stop()
		mot_st[1]=rm

def map(v, in_min=0, in_max=2.0, out_min=0, out_max=1.0):
	if v < in_min:
		v = in_min
	if v > in_max:
		v = in_max
	return (v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


while True:
	time.sleep(0.1)
	lr_pos=lr_pos_r
	fwrev_pos=fwrev_pos_r

	if(lr_pos==0 and fwrev_pos==0 and mot_st!=['S','S']):
		print('Stop')
		run_motor()
		client.publish('bot_stop','1')

	elif (lr_pos==0 and fwrev_pos<0):
		if(front_obstacle):
			print('Front obstacle')
			run_motor()
		else:
			run_motor(-fwrev_pos,-fwrev_pos,'F','F')
			print('Forward : ',fwrev_pos,' ',enc_l_rate,' ',enc_r_rate)

	elif (lr_pos==0 and fwrev_pos>0):
		if(back_obstacle):
			print('Back obstacle')
			run_motor()
		else:
			run_motor(fwrev_pos,fwrev_pos,'R','R')
			print('Backward : ',fwrev_pos,' ',enc_l_rate,' ',enc_r_rate)

	elif (lr_pos<0 and fwrev_pos==0):
		run_motor(-lr_pos,-lr_pos,'R','F')
		print('Left : ',lr_pos)

	elif (lr_pos>0 and fwrev_pos==0):
		run_motor(lr_pos,lr_pos,'F','R')
		print('Right : ',lr_pos)


	elif (lr_pos<0 and fwrev_pos<0):
		if(front_obstacle):
			print('Front obstacle')
			run_motor()
		else:
			lr_pos=-lr_pos
			fwrev_pos=-fwrev_pos

			l_pwr=round((fwrev_pos-lr_pos),3)
			if(l_pwr<0):
				l_pwr=0
			r_pwr=round(map(fwrev_pos+lr_pos),3)

			run_motor(l_pwr,r_pwr,'F','F')
			print('Forward Left : ',l_pwr,r_pwr)

	elif (lr_pos<0 and fwrev_pos>0):
		if(back_obstacle):
			print('Back obstacle')
			run_motor()
		else:
			lr_pos=-lr_pos

			l_pwr=round((fwrev_pos-lr_pos),3)
			r_pwr=round(map(fwrev_pos+lr_pos),3)
			if l_pwr<0:
				l_pwr=0

			run_motor(l_pwr,r_pwr,'R','R')
			print('Backward Left : ',l_pwr,r_pwr)

	elif (lr_pos>0 and fwrev_pos<0):
		if(front_obstacle):
			print('Front obstacle')
			run_motor()
		else:
			fwrev_pos=-fwrev_pos
			l_pwr=round(map(fwrev_pos+lr_pos),3)
			r_pwr=round((fwrev_pos-lr_pos),3)
			if r_pwr<0:
				r_pwr=0

			run_motor(l_pwr,r_pwr,'F','F')
			print('Forward Right : ',l_pwr,r_pwr)

	elif (lr_pos>0 and fwrev_pos>0):
		if(back_obstacle):
			print('Back obstacle')
			run_motor()
		else:
			l_pwr=round(map(fwrev_pos+lr_pos),3)
			r_pwr=round((fwrev_pos-lr_pos),3)
			if r_pwr<0:
				r_pwr=0
			run_motor(l_pwr,r_pwr,'R','R')
			print('Backward Right : ',l_pwr,r_pwr)