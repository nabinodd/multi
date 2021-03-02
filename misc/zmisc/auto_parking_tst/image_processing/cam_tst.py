import time
import picamera
import numpy as np
import cv2
# vs=cv2.VideoCapture(1)

camera =  picamera.PiCamera()
while True:
    # _,feed=vs.read()
    camera.resolution = (320, 240)
    camera.framerate = 24
    # time.sleep(0.1)
    image = np.empty((240 * 320 * 3,), dtype=np.uint8)
    camera.capture(image, 'bgr')
    image = image.reshape((240, 320, 3))
    cv2.imshow('feed',image)
    if cv2.waitKey(1) & 0XFF==ord('q'):
        break
cv2.destroyAllWindows()