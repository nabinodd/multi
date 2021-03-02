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

mqtt_server=('192.168.0.103',1883,60)
encoder_sample_time=0.2
enc_l_rate=0
enc_r_rate=0

########################PIN DEFS########################
ckt_trig_relay_pin=23
lift_up_relay_pin=5
lift_down_relay_pin=16
motl_a_pin=4
motl_b_pin=12
motr_a_pin=1
motr_b_pin=15
servo_pin=14
us_fl=Ultrasonic(27,22)
us_br=Ultrasonic(20,21)
us_fr=Ultrasonic(19,26)
us_bl=Ultrasonic(6,13)
enc_l_pin=18
enc_r_pin=0
########################PIN DEFS########################

########################OBJ INITS########################
# ckt_trig_relay=OutputDevice(ckt_trig_relay_pin,active_high=False, initial_value=False)
motl= Motor(motl_a_pin,motl_b_pin)
motr = Motor(motr_a_pin, motr_b_pin)
lift_up_relay=OutputDevice(lift_up_relay_pin,active_high=False, initial_value=False)
lift_down_relay=OutputDevice(lift_down_relay_pin,active_high=False, initial_value=False)
pi=pigpio.pi()

el=Encoder(enc_l_pin)
er=Encoder(enc_r_pin)

########################OBJ INITS########################

########################START-UP INITS########################
# ckt_trig_relay.on()
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

def on_message(client, userdata, msg):
	global lr_pos_r,fwrev_pos_r,accl_val,servo_pos,initial_servo_pos,min_servo_pos,servo_reset_running,servo_up,servo_down,pingg,reset_servo_pos

	if msg.topic=='joystick/fwrev':
		fwrev_pos_r=float(msg.payload.decode())
		if(fwrev_pos_r!=0):
			pingg=True

	elif msg.topic=='joystick/lr':
		lr_pos_r=float(msg.payload.decode())
		pingg=False

	elif msg.topic=='joystick/accl':
		accl_val=float(msg.payload.decode())

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

client = mqtt.Client()
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
				client.publish('sensors/ultrasonic/front_alert')
			else:
				front_obstacle=False
			if(us_bl_dist<obstacle_distance or us_br_dist<obstacle_distance):
				back_obstacle=True
				client.publish('sensors/ultrasonic/back_alert')
			else:
				back_obstacle=False
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

def map(v, in_min=0, in_max=2.0, out_min=0, out_max=1.0):
	if v < in_min:
		v = in_min
	if v > in_max:
		v = in_max
	return (v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


while True:
	lr_pos=lr_pos_r
	fwrev_pos=fwrev_pos_r

	time.sleep(0.1)

	if(lr_pos==0 and fwrev_pos==0):
		print('Stop')
		motl.stop()
		motr.stop()

	elif (lr_pos==0 and fwrev_pos<0):
		if(front_obstacle):
			print('Front obstacle')
			motl.stop()
			motr.stop()
		else:
			fwrev_pos=map(-fwrev_pos+accl_val)		
			run_motor(fwrev_pos,fwrev_pos,'F','F')
			print('Forward : ',fwrev_pos,' ',enc_l_rate,' ',enc_r_rate)

	elif (lr_pos==0 and fwrev_pos>0):
		if(back_obstacle):
			print('Back obstacle')
			motl.stop()
			motr.stop()
		else:	
			fwrev_pos=map(fwrev_pos+accl_val)
			run_motor(fwrev_pos,fwrev_pos,'R','R')
			print('Backward : ',fwrev_pos,' ',enc_l_rate,' ',enc_r_rate)

	elif (lr_pos<0 and fwrev_pos==0):
		lr_pos=map(-lr_pos+accl_val)
		run_motor(lr_pos,lr_pos,'R','F')
		print('Left : ',lr_pos)

	elif (lr_pos>0 and fwrev_pos==0):
		lr_pos=map(lr_pos+accl_val)
		run_motor(lr_pos,lr_pos,'F','R')
		print('Right : ',lr_pos)


	elif (lr_pos<0 and fwrev_pos<0):
		if(front_obstacle):
			print('Front obstacle')
			motl.stop()
			motr.stop()
		else:
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
		if(back_obstacle):
			print('Back obstacle')
			motl.stop()
			motr.stop()
		else:	
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
		if(front_obstacle):
			print('Front obstacle')
			motl.stop()
			motr.stop()
		else:
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
		if(back_obstacle):
			print('Back obstacle')
			motl.stop()
			motr.stop()
		else:	
			l_pwr=round(map(fwrev_pos+lr_pos),3)
			r_pwr=round((fwrev_pos-lr_pos),3)
			if r_pwr<0:
				r_pwr=0
			
			l_pwr=map(l_pwr+accl_val)
			r_pwr=map(r_pwr+accl_val)
			
			run_motor(l_pwr,r_pwr,'R','R')
			print('Backward Right : ',l_pwr,r_pwr)