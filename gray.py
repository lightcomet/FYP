import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import csv
import time
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
leftX2 = 319
leftY2 = 479

totalLeft = 0
prevLeftY = 0
currentLeftY = 0
diffLeftY = 0
countLeft = 0

currentLeftX = 0
diffLeftX = 0

# Flags
criticalLeftY = -1
criticalLeftX = -1

rightX1 = 320
rightY1 = 0
rightX2 = 639
rightY2 = 479

totalRight = 0

dataLeftX = ['Left X Values']
dataLeftY = ['Left Y Values']
dataRightX = ['Right X Values']
dataRightY = ['Right Y Values']

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

    nonZeroLeft = cv2.findNonZero(leftMask) #2nd 0 is 1st array pair, 3rd 0 is 1st item in array
    nonZeroRight = cv2.findNonZero(rightMask) #2nd 0 is 1st array pair, 3rd 0 is 1st item in array

    # retrieve critical Y value and break loop
    for counter in range(0, len(nonZeroLeft)):
        if(criticalLeftY != -1):
            break
        if(counter == 0):
            prevLeftY = nonZeroLeft[counter][0][1]
        else:
            currentLeftY = nonZeroLeft[counter][0][1]
            diffLeftY = currentLeftY - prevLeftY
            if(diffLeftY == 0):
                countLeft = 0
            else:
                if(countLeft == 1):
                    print("critical Y value is: ",prevLeftY)
                    criticalLeftY = 0
                    break
                else:
                    prevLeftY = currentLeftY
                    countLeft += 1

    # retrieve crtical X value and break loop
    for counter in range(0, len(nonZeroLeft)):
        if (criticalLeftX != -1):
            break
        else:
            currentLeftY = nonZeroLeft[counter][0][1]
            if(currentLeftY == prevLeftY):
                criticalLeftX = nonZeroLeft[counter][0][0]
                print("critical X value is: ",nonZeroLeft[counter][0][0])

    # only add if X value is within critical range
    for counter in range(0, len(nonZeroLeft)):
        if(criticalLeftX == -1 or criticalLeftY == -1):
            break
        else:
            currentLeftX = nonZeroLeft[counter][0][0]
            diffLeftX = currentLeftX - criticalLeftX
##            print("diff: ",diffLeftX)
##            print("current: ",currentLeftX)
##            print("critical: ",criticalLeftX)
            if(diffLeftX >= -3 and diffLeftX <= 3):
                totalLeft += currentLeftX
                criticalLeftX = currentLeftX
    criticalLeftY = -1
    criticalLeftX = -1
    print("left: ",leftX2 - (totalLeft/len(nonZeroLeft)))
    totalLeft = 0
                
##    for counter in range (0, len(nonZeroLeft)):
##        totalLeft += nonZeroLeft[counter][0][0]
##    print("left: ",leftX2 - (totalLeft/len(nonZeroLeft)))
##    totalLeft = 0
##
##    for counter in range (0, len(nonZeroRight)):
##        totalRight += nonZeroRight[counter][0][0]
##    print("right: ",(totalRight/len(nonZeroRight)) - rightX1)
##    totalRight = 0

    # count number of pixels on masked image
##    nonZeroLeft = cv2.countNonZero(leftMask)
##    nonZeroRight = cv2.countNonZero(rightMask)
    
##    print("left: ",nonZeroLeft," right: ",nonZeroRight)
    
    cv2.imshow('mask1',leftMask)
    cv2.imshow('mask2',rightMask)

    rawCapture.truncate(0)

    k = cv2.waitKey(1) & 0xFF
    if (k == 27) or (k == ord("q")) :
        nonZeroLeft = cv2.findNonZero(leftMask)
        nonZeroRight = cv2.findNonZero(rightMask)
        saveOutput = input("Save File? Type 'Y' for yes and 'N' for no \n")
        if(saveOutput == "Y" or saveOutput == "y"):
            
            for counter in range (0, len(nonZeroLeft)):                
                dataLeftX.append(nonZeroLeft[counter][0][0])
                dataLeftY.append(nonZeroLeft[counter][0][1])
                
            for counter in range (0, len(nonZeroRight)):
                dataRightX.append(nonZeroRight[counter][0][0])
                dataRightY.append(nonZeroRight[counter][0][1])

##            print(dataLeftX)
##            print(dataLeftY)
##            print(dataRightX)
##            print(dataRightY)

            timeString = time.strftime("%Y%m%d-%H%M%S")

            with open ('/home/pi/Desktop/FYP/Data/%s.csv' %timeString,'w',newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter = ',')
                writer.writerow(dataLeftX)
                writer.writerow(dataLeftY)
                writer.writerow(dataRightX)
                writer.writerow(dataRightY)
                
            cv2.imwrite('/home/pi/Desktop/FYP/Data/%s.png' %timeString ,edges)
            print("Output is saved")
        else:
            print("Output not saved")
        break
