from gpiozero import Motor
from gpiozero import OutputDevice
import paho.mqtt.client as mqtt
import threading
import pigpio
import time


mqtt_server=('192.168.0.103',1883,60)


# motl = Motor(4, 12)
# motr= Motor(15, 14)
motl = Motor(15, 1)
motr= Motor(4, 12)
servo_pin=14
pi=pigpio.pi()

lift_up_relay=OutputDevice(5,active_high=False, initial_value=False)
lift_down_relay=OutputDevice(16,active_high=False, initial_value=False)

lr_pos_r=0
fwrev_pos_r=0

reset_delay=0.1


initial_servo_pos=500
max_servo_pos=2500

pi.set_servo_pulsewidth(servo_pin,initial_servo_pos)
servo_pos=initial_servo_pos

servo_thread_running=False
up=False
down=False
running=True

# lifter_thread_running=False
# lift_up=False
# lift_down=False


def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))

	client.subscribe('joystick/lr')
	client.subscribe('joystick/fwrev')
	client.subscribe('joystick/accl')
	client.subscribe('joystick/cam_rst')
	client.subscribe('joystick/cam_up_down')
	client.subscribe('joystick/lifter')

def reset_cam():
    global servo_thread_running,servo_pos,initial_servo_pos
    servo_thread_running=True
    for i in range(servo_pos,initial_servo_pos,-100):
        pi.set_servo_pulsewidth(servo_pin,i)
        print('Reseting camera pos : ',i)
        time.sleep(reset_delay)

    servo_pos=initial_servo_pos
    pi.set_servo_pulsewidth(servo_pin, 0)
    time.sleep(1)
    servo_thread_running=False

def servo_ud():
    global servo_pos,up,down
    while True:
        if up==True:
            print('Moving up : ',servo_pos)
            servo_pos=servo_pos+100
            pi.set_servo_pulsewidth(servo_pin,servo_pos)
            up=False
        elif down==True:
            print('Moving down : ',servo_pos)
            servo_pos=servo_pos-100
            pi.set_servo_pulsewidth(servo_pin,servo_pos)
            down=False
        time.sleep(0.001)

threading.Thread(target=servo_ud,daemon=True).start()

def on_message(client, userdata, msg):
	global lr_pos_r,fwrev_pos_r,accl_val,servo_pos,initial_servo_pos,max_servo_pos,servo_thread_running,up,down

	if msg.topic=='joystick/fwrev':
		fwrev_pos_r=float(msg.payload.decode())

	if msg.topic=='joystick/lr':
		lr_pos_r=float(msg.payload.decode())

	if msg.topic=='joystick/accl':
		accl_val=float(msg.payload.decode())

	if msg.topic=='joystick/cam_rst':
		if servo_thread_running==False and servo_pos!=initial_servo_pos:
			threading.Thread(target=reset_cam,daemon=True).start()

	if msg.topic=='joystick/cam_up_down':
		cam_up_down_val=msg.payload.decode()
		if servo_thread_running==False:
			if cam_up_down_val=='1' and servo_pos<max_servo_pos:
				up=True
				down=False
			elif cam_up_down_val=='-1' and servo_pos>initial_servo_pos:
				down=True
				up=False
	if msg.topic=='joystick/lifter':
		lifter_cmd=msg.payload.decode()
		if lifter_cmd=='up':
			lift_up_relay.on()
			lift_down_relay.off()
			print('Going up')

		elif lifter_cmd=='down':
			print('Going down')
			lift_down_relay.on()
			lift_up_relay.off()


# def lifter_ud():
# 	if lift_up:
# 		print('lifting up')
# 		lift_up=False

# 	elif lift_down:
# 		print('lifting down')
# 		lift_down=False


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


client.connect(mqtt_server[0],mqtt_server[1],mqtt_server[2])
# client.connect('192.168.100.235', 1883, 60)

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

	time.sleep(0.1)

	if(lr_pos==0 and fwrev_pos==0):
		print('Stop')
		motl.stop()
		motr.stop()

	elif (lr_pos==0 and fwrev_pos<0):
		fwrev_pos=map(-fwrev_pos+accl_val)		
		run_motor(fwrev_pos,fwrev_pos,'F','F')
		print('Forward : ',fwrev_pos)

	elif (lr_pos==0 and fwrev_pos>0):
		fwrev_pos=map(fwrev_pos+accl_val)
		run_motor(fwrev_pos,fwrev_pos,'R','R')
		print('Backward : ',fwrev_pos)

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