import paho.mqtt.client as mqtt
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

front_id=2
back_id=3
marker_size=6 #cm

frame_rd=None
run=True
reading=False

manual_auto='M'

KNOWN_WIDTH=6.0
focal_length=625
known_distance=50 #cm

center=320
center_x=0

broker='192.168.0.102'
client=mqtt.Client('aruco_ctl')
client.will_set('botcmd/stop','1')

L_left_right=-0.2
L_fwd_rev=-0.2

R_left_right=0.2
R_fwd_rev=0

F_left_right=0
F_fwd_rev=-0.4

accl_knob=0.4

def on_log(client,userdata,level,buf):
    print('log: '+buf)

def on_connect(client,userdata,flags,rc):
    if rc==0:
        print('Connected OK')
    else:
        print('Not connected : ',rc)

    client.subscribe('auto_entry')

def on_message(client, userdata, msg):
    global manual_auto,accl_knob
    if msg.topic=='auto_entry':
        print('Msg received......,,,,,,,,,,,,,,,,,,,')
        auto_entry_enable=msg.payload.decode()
        if manual_auto!='A' and auto_entry_enable=='1':
            manual_auto='A'
            print('In automatic mode...')

        elif manual_auto!='M' and auto_entry_enable=='0':
            manual_auto='M'
            print('In manual mode')
            cv2.destroyAllWindows()


client.on_connect=on_connect
client.on_message=on_message
# client.on_log=on_log

print('Connecting to broker : ',broker)
client.connect(broker)

client.loop_start()

def send_cmd():
    global center_x
    while run:
        if manual_auto=='A':
            if center_x>0 and center_x<240:
                client.publish('aruco_cam/lr',str(L_left_right))
                client.publish('aruco_cam/fwrev',str(L_fwd_rev))
                client.publish('aruco_cam/accl',str(accl_knob))
                # print('Going left')

            elif center_x>400:
                client.publish('aruco_cam/lr',str(R_left_right))
                client.publish('aruco_cam/fwrev',str(R_fwd_rev))
                client.publish('aruco_cam/accl',str(accl_knob))
                # print('Going Right')

            elif center_x==0:
                client.publish('aruco_cam/lr',str(0))
                client.publish('aruco_cam/fwrev',str(0))
                # print("STOP")
            elif center_x>239 and center_x<399:
                client.publish('aruco_cam/lr',str(F_left_right))
                client.publish('aruco_cam/fwrev',str(F_fwd_rev))
                client.publish('aruco_cam/accl',str(accl_knob))
                # print("Going Forward")
            center_x=0
            time.sleep(0.1)
        else:
            time.sleep(0.1)

cmd_thread=threading.Thread(target=send_cmd,daemon=True)
cmd_thread.start()

def retry_connect(cam):
    cam.release()
    time.sleep(1)
    cam.open(url)


def distance_to_camera(knownWidth, perWidth):
	return (knownWidth * focal_length) / perWidth


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
    if reading and manual_auto=='A':
        frame=frame_rd
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        corners,ids,rejected= aruco.detectMarkers(image=frame,dictionary=aruco_dict,parameters=parameters,cameraMatrix=camera_matrix,distCoeff=camera_distortion)
        if ids is not None:
            id_list=list(ids[:,0])
            for a_id in id_list:
                if a_id==front_id or back_id:
                    aruco.drawDetectedMarkers(frame, corners)
                    # pt1=tuple(corners[0][0][0])
                    # pt2=tuple(corners[0][0][1])
                    # pt3=tuple(corners[0][0][2])
                    # pt4=tuple(corners[0][0][3])

                    if a_id==front_id:
                        x=id_list.index(front_id)
                    elif a_id==back_id:
                        x=id_list.index(back_id)

                    else:
                        break

                    pt1=tuple(corners[x][0][0])
                    pt2=tuple(corners[x][0][1])
                    pt3=tuple(corners[x][0][2])
                    pt4=tuple(corners[x][0][3])

                    ref_length=int(math.sqrt((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2))
                    distance=distance_to_camera(KNOWN_WIDTH,ref_length)

                    horiz_length=int(math.sqrt((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2))
                    vert_length=int(math.sqrt((pt3[0]-pt4[0])**2+(pt3[1]-pt4[1])**2))

                    M=cv2.moments(corners[x])
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    cv2.circle(frame,(cX,cY),5,(0,0,255),-2)
                    cv2.circle(frame,pt3,5,(0,0,255),-2)
                    center_x=cX
                    # print(cX,cY)
                    average_length=(horiz_length+vert_length)/2

                    # focal_length=(average_length*known_distance)/marker_size
                    # print('Horiz : ',' Vert : ',horiz_length,' Vert : ',vert_length,' Avg : ',average_length)
                    # print('Focal length : ',focal_length)

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