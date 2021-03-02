from gpiozero import AngularServo
from cv2 import aruco
import numpy as np
import threading
import math
import time
import cv2



url='http://admin:ingnepal123@192.168.2.223/Streaming/channels/101/httppreview'

cam=cv2.VideoCapture()
cam.open(url)

aruco_dict  = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
parameters  = aruco.DetectorParameters_create()

camera_matrix   = np.loadtxt('cameraMatrix.txt', delimiter=',')
camera_distortion   = np.loadtxt('cameraDistortion.txt', delimiter=',')

cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

font = cv2.FONT_HERSHEY_PLAIN

id_to_find=16
marker_size=19 #cm

frame_rd=None
run=True
reading=False

KNOWN_WIDTH=7.48

cam_servo = AngularServo(4, min_angle=0, max_angle=180, min_pulse_width=0.0006, max_pulse_width=0.0024)
initial_servo_pos=80
max_servo_pos=120

cam_servo.angle=100
print('Servo init')
# cam_servo.detach()

def retry_connect(cam):
    cam.release()
    time.sleep(1)
    cam.open(url)


def distance_to_camera(knownWidth, focalLength, perWidth):
	return (knownWidth * focalLength) / perWidth


def read_feed():
    global frame_rd,reading,run
    while run:
        try:
            ret,frame_rd=cam.read()
            reading=True
        except:
            retry_connect(cam)
            reading=False

read_thr=threading.Thread(target=read_feed,daemon=True)
read_thr.start()

def map(v, in_min=0, in_max=640.0, out_min=0, out_max=180):
	if v < in_min:
		v = in_min
	if v > in_max:
		v = in_max
	return (v - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

while run:
    if reading:
        frame=frame_rd
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        corners,ids,rejected= aruco.detectMarkers(image=frame,dictionary=aruco_dict,parameters=parameters,cameraMatrix=camera_matrix,distCoeff=camera_distortion) 
        if ids is not None and ids[0]==id_to_find:        
            aruco.drawDetectedMarkers(frame, corners)
            pt1=corners[0][0][0]
            pt2=corners[0][0][1]
            pt3=corners[0][0][2]
            pt4=corners[0][0][3]
            ref_length=int(math.sqrt((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2))
            distance=distance_to_camera(KNOWN_WIDTH,759.35,ref_length)


            length1=int(math.sqrt((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2))
            length2=int(math.sqrt((pt3[0]-pt4[0])**2+(pt3[1]-pt4[1])**2))

            M=cv2.moments(corners[0])
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            
            cv2.circle(frame,(cX,cY),5,(0,0,255),-2)
            cam_servo.angle=180-map(cX)
            # print(180-map(cX))
            # print('Distance : ',distance)
        cv2.imshow('Cam feed',frame)
        if cv2.waitKey(1) & 0xFF==ord('q'):
            run=False
            reading=False
            break
    else:
        print('Waiting @ ',time.time())
        time.sleep(1)

cam.release()
cv2.destroyAllWindows()