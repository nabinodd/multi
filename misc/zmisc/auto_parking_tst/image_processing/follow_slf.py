from picamera.array import PiRGBArray
from picamera import PiCamera
from gpiozero import Motor
import time
import cv2

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 25
rawCapture = PiRGBArray(camera, size=(640, 480))

motl=Motor(19,26)
motr=Motor(16,20)

time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray,(5,5),0)
    # blur=cv2.blur(gray,ksize=(7,7))

    ret,thresh1 = cv2.threshold(blur,10,255,cv2.THRESH_BINARY_INV)
    mask = cv2.erode(thresh1, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, hierarchy = cv2.findContours(mask.copy(),1,cv2.CHAIN_APPROX_NONE)
    if len(contours) > 0:

        c = max(contours, key = cv2.contourArea)
        # TODO Change max to min
        M = cv2.moments(c)
        cx = int(M['m10']/M['m00'])
        # print('Max cont : ',cx)

        if cx<=320:
            print('Go right : ',cx)
            motl.forward(0.3)
            motr.stop()

        elif cx>320 and cx<350:
            motl.forward(0.3)
            motr.forward(0.3)
            print('Go forward : ',cx)
        elif cx>350:
            motl.stop()
            motr.forward(0.3)
            print('Going left : ',cx)
    else:
        motl.stop()
        motr.stop()

    for i in range(len(contours)):
        if hierarchy[0][i][3]==-1:
            cv2.drawContours(image,contours,i,(255,0,0),2)

    # cv2.imshow("Thresh",thresh1)
    cv2.imshow("mask",image)

    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    if key == ord("q"):
        break