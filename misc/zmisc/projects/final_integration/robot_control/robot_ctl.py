from gpiozero import Motor, AngularServo
import paho.mqtt.client as mqtt
import threading
import time


mqtt_server=('192.168.100.235',1883,60)


motl = Motor(3, 2)
motr= Motor(15, 14)

lr_pos_r=0
fwrev_pos_r=0


cam_servo = AngularServo(5, min_angle=0, max_angle=180, min_pulse_width=0.0006, max_pulse_width=0.0024)

initial_servo_pos=80
max_servo_pos=120

cam_servo.angle=initial_servo_pos
cam_servo.detach()

servo_pos=initial_servo_pos

servo_thread_running=False
up=False
down=False

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))

	client.subscribe('joystick/lr')
	client.subscribe('joystick/fwrev')
	client.subscribe('joystick/accl')
	client.subscribe('joystick/cam_rst')
	client.subscribe('joystick/cam_up_down')
   
def reset_cam():
    global servo_thread_running,servo_pos,initial_servo_pos,cam_servo
    servo_thread_running=True
    for i in range(servo_pos,initial_servo_pos,-1):
        cam_servo.angle=i
        print('Reseting camera pos : ',i)
        time.sleep(0.5)
    servo_pos=initial_servo_pos
    cam_servo.detach()
    time.sleep(1)
    servo_thread_running=False

def servo_ud():
    global servo_pos,cam_servo,up,down
    while True:
        if up==True:
            print('Moving up')
            servo_pos=servo_pos+1
            cam_servo.angle=servo_pos
            up=False
        elif down==True:
            print('Moving down')
            servo_pos=servo_pos-1
            cam_servo.angle=servo_pos
            down=False
        time.sleep(0.1)
        cam_servo.detach()
        time.sleep(0.1)

threading.Thread(target=servo_ud,daemon=True).start()

def on_message(client, userdata, msg):
    global lr_pos_r,fwrev_pos_r,accl_val,servo_pos,initial_servo_pos,max_servo_pos,up,down

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