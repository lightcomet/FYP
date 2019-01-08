
import time
time1 = time.time()
import cv2
import numpy as np
import math
from picamera import PiCamera
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
from settings import config

def movement (varLeft, varRight, pwma, pwmb, direction):
    print("left: " ,varLeft)
    print("right: " ,varRight)
    print("direction: ", direction)

    if(direction == "up"):
        pwma.start(50)
        pwmb.start(50)
        GPIO.output(settings["AIN1"],1)
        GPIO.output(settings["AIN2"],0)
        GPIO.output(settings["BIN1"],1)
        GPIO.output(settings["BIN2"],0)
        pwma.ChangeFrequency(varRight)
        pwmb.ChangeFrequency(varLeft)
    elif(direction == "down"):
        pwma.start(50)
        pwmb.start(50)
        GPIO.output(settings["AIN1"],0)
        GPIO.output(settings["AIN2"],1)
        GPIO.output(settings["BIN1"],0)
        GPIO.output(settings["BIN2"],1)
        pwma.ChangeFrequency(varRight)
        pwmb.ChangeFrequency(varLeft)
    time.sleep(1)
    

def autoCanny (image, sigma = 0.33):
    # compute the median of the single channel pixel intensities
    median = np.median(image)
    
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * median))
    upper = int(min(255, (1.0 + sigma) * median))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged
    

if __name__ == '__main__':

    settings = config()

    #initialise
    GPIO.setwarnings(False) # no gpio wanrings
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(settings["PWMA"], GPIO.OUT)
    GPIO.setup(settings["AIN1"], GPIO.OUT)
    GPIO.setup(settings["AIN2"], GPIO.OUT)
    GPIO.setup(settings["PWMB"], GPIO.OUT)
    GPIO.setup(settings["BIN1"], GPIO.OUT)
    GPIO.setup(settings["BIN2"], GPIO.OUT)
    GPIO.setup(settings["STNBY"], GPIO.OUT)

    pwma = GPIO.PWM(settings["PWMA"],settings["PWMA_PW"]) # pulse width of 100 Hz
    pwmb = GPIO.PWM(settings["PWMB"],settings["PWMB_PW"]) # pulse width of 100 Hz

    GPIO.output(settings["PWMA"],0)
    GPIO.output(settings["AIN1"],0)
    GPIO.output(settings["AIN2"],0)
    GPIO.output(settings["PWMB"],0)
    GPIO.output(settings["BIN1"],0)
    GPIO.output(settings["BIN2"],0)

    startFlag = False
    direction = False
    varLeft = 1
    varRight = 1

    font = cv2.FONT_HERSHEY_SIMPLEX


    # camera settings
    setResolution = (640,480)
    camera = PiCamera()
    camera.resolution = setResolution
    camera.exposure_mode = 'antishake'
    camera.framerate = 60
    rawCapture = PiRGBArray(camera, size=setResolution)

    # set up time
    time3 = time.time()
    print ('Set up time : ', time3-time1,'secs')

    # camera warm up
    time.sleep(2)

    # capture frames from camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

        pathXList = []
        pathList = []
        pathFilteredList = []
        pathDiffList = []
        pathIndex = []
            
        # image array, processing is done here
        image = frame.array

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        edges = autoCanny(hsv) #settings["cannyMin"] , settings["cannyMax"]

        lines = cv2.HoughLinesP(edges, rho = 1, theta = np.pi/360, threshold =  100, minLineLength = settings["minLineLength"], maxLineGap = settings["maxLineGap"])
        timeStart = time.time()
        if(lines is not None):
            for line in lines:
                for x1,y1,x2,y2 in line:
                    dy = y2-y1
                    dx = x2-x1
                    angle = math.degrees(math.atan2(dy,dx))
                    print(" angle : ", angle)
                    if(angle <= -10 or angle >= 10):
                        print("legit angle")
                        pathXList.extend([x1,x2])
                    print("x1: ",x1, "| y1: ", y1, "| x2: ",x2, "| y2: ",y2)
                    cv2.line(image,(x1,y1),(x2,y2),(0,255,0),2)
##                    cv2.putText(image, str(x1)+ "|"+str(y1)+"|"+str(x2)+"|"+str(y2),(x1-20,y1+20), font, 1, (255,255,255),2,cv2.LINE_AA)

        pathXList = list(set(pathXList))
        pathXList.sort()
        print("pathXList : ",pathXList)
        print("boundary of path = ",pathXList[0]," and ",pathXList[len(pathXList)-1])
##        print("length of pathXlist : ",len(pathXList))
##        i = 0
##        while i < len(pathXList):
##            if(i == 0):
##                pass   
##            else:
##                if(pathXList[i] - pathXList[i-1] <= 30):
##                    average = (pathXList[i] + pathXList[i-1])//2
##                    del pathXList[i]
##                    del pathXList[i-1]
##                    pathXList.insert(i-1,average)
##                    i-= 1
##                else:
##                    pass
##            i+= 1
##        print("final pathXList : ", pathXList)
##        timeStop = time.time()
##        print("time taken : ",(timeStop-timeStart)*1000, "ms")
##        if(len(pathXList) == 2):
##            left = pathXList[0]
##            right = pathXList[1]
##            if(250 <= left and right <= 400):
##                print("gp forward")
##                varLeft = 1000
##                varRight = 2000
##            elif(right > 401):
##                print("turn right")
##                varLeft = 2000
##                varRight = 2000
##            elif(left<249):
##                print("turn left")
##                varLeft = 1000
##                varRight = 3000
        
        
        # show frame
        cv2.imshow("Image", edges)
        cv2.imshow("Line Image", image)
                
        # clear stream in preparation for next frame
        rawCapture.truncate(0)
        
        # wait for input
        key = cv2.waitKey(1) & 0xFF

        # stop movement if keyboard p is pressed
        if key & 0xFF == ord("s"):
            print('start')
            startFlag = True
            direction = "up"
        
        # stop movement if keyboard p is pressed
        if key & 0xFF == ord("p"):
            print('pause')
            startFlag = False
            pwma.stop()
            pwmb.stop()

        # exit from loop if keyboard q is pressed
        if key & 0xFF == ord("q"):
            print('quit')
            startFlag = False
            pwma.stop()
            pwmb.stop()
            break

        if(startFlag == True):
            movement(varLeft,varRight,pwma,pwmb,direction)
        
    time2 = time.time()
    print ('Elapsed time : ', time2-time1,'secs')
    GPIO.cleanup() #important to have to reset the GPIOs
