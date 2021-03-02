import numpy as np
import time
import cv2



cam=cv2.VideoCapture()
cam.open('http://admin:ingnepal123@192.168.0.223/Streaming/channels/101/httppreview')
c=0
while True:
    try:
        ret, frame = cam.read()
        cv2.imshow("test", frame)
    except:
        print('Error')
        time.sleep(2)
        cam.release()
        time.sleep(2)
        cam.open('http://admin:ingnepal123@192.168.0.223/Streaming/channels/101/httppreview')

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed

        img_name=str(c)+'.jpg'
        # cv2.imwrite(img_name, frame)
        cv2.imwrite(img_name,frame,[cv2.IMWRITE_JPEG_QUALITY,100])
        print("{} written!".format(img_name))
        c=c+1

cam.release()

cv2.destroyAllWindows()