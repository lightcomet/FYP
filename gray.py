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

cv2.namedWindow('window')

cv2.createTrackbar('Canny Min','window',0,900,nothing)
cv2.createTrackbar('Canny Max','window',0,900,nothing)
cv2.setTrackbarPos('Canny Min','window',80)
cv2.setTrackbarPos('Canny Max','window',100)

middleBottom = (int(setResolution[0]/2),int(setResolution[1]))
middleTop = (int(setResolution[0]/2), 0)
white = (255,255,255)

leftX1 = 0
leftY1 = 0
leftX2 = 320
leftY2 = 480

rightX1 = 321
rightY1 = 0
rightX2 = 640
rightY2 = 480

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array

    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    cannyMin = cv2.getTrackbarPos('Canny Min','window')
    cannyMax = cv2.getTrackbarPos('Canny Max','window')
    edges = cv2.Canny(hsv, cannyMin ,cannyMax)

##    edges = cv2.line(edges, middleBottom, middleTop, white, 1)

    cv2.imshow('mask',hsv)
    cv2.imshow('edges',edges)

    mask = np.zeros(edges.shape, dtype="uint8")
    cv2.rectangle(mask, (leftX1,leftY1), (leftX2,leftY2),(255,255,255),-1)

    mask2 = np.zeros(edges.shape, dtype="uint8")
    cv2.rectangle(mask2, (rightX1,rightY1), (rightX2,rightY2),(255,255,255),-1)

    leftMask = cv2.bitwise_and(edges,mask)
    rightMask = cv2.bitwise_and(edges,mask2)
    
    nonZeroLeft = cv2.countNonZero(leftMask)
    nonZeroRight = cv2.countNonZero(rightMask)

    print("left: ",nonZeroLeft," right: ",nonZeroRight)
    
    cv2.imshow('mask1',leftMask)
    cv2.imshow('mask2',rightMask)

    rawCapture.truncate(0)

    k = cv2.waitKey(1) & 0xFF
    if (k == 27) or (k == ord("q")) :
        nonZero = cv2.findNonZero(edges)
        print(nonZero)
        saveOutput = input("Save File? Type 'Y' for yes and 'N' for no \n")
        if(saveOutput == "Y" or saveOutput == "y"):
            np.savetxt('output.txt',nonZero,fmt="%s")
            np.savetxt('output.csv',nonZero,fmt="%s",delimiter=",")
            cv2.imwrite('output.png',edges)
            print("Output is saved")
        else:
            print("Output not saved")
        break
