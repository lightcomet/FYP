import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray


def nothing(x):
    pass

setResolution = (640,480)
camera = PiCamera()
camera.resolution = setResolution
camera.exposure_mode = 'antishake'
camera.framerate = 60
rawCapture = PiRGBArray(camera, size=setResolution)

##img = cv2.imread('image5.jpg')
##hsv = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
#// cardboard color
##lower_red = np.array([130,60,60])
##upper_red = np.array([170,255,255])
##
##mask = cv2.inRange(hsv, lower_red, upper_red)
##res = cv2.bitwise_and(img,img,mask = mask)

cv2.namedWindow('window')

cv2.createTrackbar('Canny Min','window',0,900,nothing)
cv2.createTrackbar('Canny Max','window',0,900,nothing)
cv2.setTrackbarPos('Canny Max','window',100)

##cv2.imshow('res',res)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array

    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

##    cv2.imshow('image',image)
    cv2.imshow('mask',hsv)
    
    cannyMin = cv2.getTrackbarPos('Canny Min','window')
    cannyMax = cv2.getTrackbarPos('Canny Max','window')
    edges = cv2.Canny(hsv, cannyMin ,cannyMax)
    cv2.imshow('edges',edges)

    rawCapture.truncate(0)

    k = cv2.waitKey(1) & 0xFF
    if (k == 27) or (k == ord("q")) :
        nonZero = cv2.findNonZero(edges)
        print(nonZero)
        np.savetxt('output.txt',nonZero,fmt="%s")
        break
##    cv2.destroyAllWindows()
