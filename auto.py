import time
startProgramTime = time.time()
import cv2
import numpy as np
import math
from picamera import PiCamera
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
from settings import config

def movement (varLeft, varRight, pwma, pwmb, direction, findPath):
    print("left: ", varLeft, " | ", "right: ", varRight, " | ", "direction: ", direction, " | ", "pathFlag: ",findPath)
##    if(findPath == True):
##        pwma.start(1)
##        pwmb.start(30)
##        GPIO.output(settings["AIN1"],1)
##        GPIO.output(settings["AIN2"],0)
##        GPIO.output(settings["BIN1"],1)
##        GPIO.output(settings["BIN2"],0)
##        pwma.ChangeFrequency(varRight)
##        pwmb.ChangeFrequency(varLeft)
##    else:
##        if(direction == "up"):
##            print("up movement")
##            pwma.start(50)
##            pwmb.start(50)
##            GPIO.output(settings["AIN1"],1)
##            GPIO.output(settings["AIN2"],0)
##            GPIO.output(settings["BIN1"],1)
##            GPIO.output(settings["BIN2"],0)
##            pwma.ChangeFrequency(varRight)
##            pwmb.ChangeFrequency(varLeft)
##            
##        elif(direction == "left"):
##            print("left movement")
##            pwma.start(20)
##            pwmb.start(10)
##            GPIO.output(settings["AIN1"],1)
##            GPIO.output(settings["AIN2"],0)
##            GPIO.output(settings["BIN1"],1)
##            GPIO.output(settings["BIN2"],0)
##            pwma.ChangeFrequency(varRight)
##            pwmb.ChangeFrequency(varLeft)
##            
##        elif(direction == "right"):
##            print("right movement")
##            pwma.start(10)
##            pwmb.start(20)
##            GPIO.output(settings["AIN1"],1)
##            GPIO.output(settings["AIN2"],0)
##            GPIO.output(settings["BIN1"],1)
##            GPIO.output(settings["BIN2"],0)
##            pwma.ChangeFrequency(varRight)
##            pwmb.ChangeFrequency(varLeft)

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

    GPIO.output(settings["AIN1"],0)
    GPIO.output(settings["AIN2"],0)
    GPIO.output(settings["BIN1"],0)
    GPIO.output(settings["BIN2"],0)
    GPIO.output(settings["STNBY"],1)

    direction = False
    pathFlag = False
    varLeft = 1
    varRight = 1

    lower_black = np.array([0,0,0])
    upper_black = np.array([235,80,10])

    font = cv2.FONT_HERSHEY_SIMPLEX


    # camera settings
    setResolution = (640,480)
    camera = PiCamera()
    camera.resolution = setResolution
    camera.exposure_mode = 'antishake'
    camera.framerate = 90
    rawCapture = PiRGBArray(camera, size=setResolution)

    # set up time
    time3 = time.time()
    print ('Set up time : ', time3-startProgramTime,'secs')

    # camera warm up
    time.sleep(2)

    # capture frames from camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        pathXList = []
        angleList = []
            
        # image array, processing is done here
        image = frame.array
        
        timeStart = time.time()

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, lower_black, upper_black)

        result = cv2.bitwise_and(cv2.bitwise_not(image), cv2. bitwise_not(image), mask = mask)

        edges = cv2.Canny(result, 80, 300)
        
        lines = cv2.HoughLinesP(edges, rho = 1, theta = np.pi/360, threshold =  100, minLineLength = settings["minLineLength"], maxLineGap = settings["maxLineGap"])
        print("--------------------------------------------------------------------------------")
        if(lines is not None):
            lenlines = len(lines)
            print("number of lines : ",lenlines)
            if(lenlines <= 6):
                for line in lines:
                    for x1,y1,x2,y2 in line:
                        dy = y2-y1
                        dx = x2-x1
                        angle = math.degrees(math.atan2(dy,dx))
##                        print(" angle : ", angle)
                        if(angle <= -20 or angle >= 20):
##                            print("legit angle")
                            angleList.extend([angle])
                            pathXList.extend([x1,x2])
##                        print("x1: ",x1, "| y1: ", y1, "| x2: ",x2, "| y2: ",y2)
                        cv2.line(image,(x1,y1),(x2,y2),(0,255,0),2)
##                        cv2.putText(image, str(x1)+ "|"+str(y1)+"|"+str(x2)+"|"+str(y2),(x1-20,y1+20), font, 1, (255,255,255),2,cv2.LINE_AA)
            else:
                print("passing")
                pass

        angleList.extend([0])
        #remove duplicates in list
        pathXList = list(set(pathXList))
        #sort list from smallest to biggest
        pathXList.sort()
        angleList.sort()
        amtOfPathXList = len(pathXList)
        print("len of path x list : ",amtOfPathXList)
        if(amtOfPathXList != 0):
            if(amtOfPathXList > 12):
                print("too many lines detected, do nothing")
                rawCapture.truncate(0)
                continue
            else:
                print("pathXList : ",pathXList)
                print("angleList : ",angleList)
                leftBoundary = pathXList[0]
                rightBoundary = pathXList[len(pathXList)-1]
                print("boundary of path = ",leftBoundary," and ",rightBoundary)
                zeroAngleIndex = angleList.index(0)
                midPointAngleList = int(math.floor(len(angleList)/2))
                
                print("zero angle index : ",zeroAngleIndex)

                if(250 <= leftBoundary and rightBoundary <= 400):
                    print("gp forward")
                    varLeft = 1000
                    varRight = 2000
                    movement(varLeft,varRight,pwma,pwmb,"up",pathFlag)

                elif(zeroAngleIndex < midPointAngleList): #more positive angles
                    print("turn left")
                    varLeft = 1000
                    varRight = 4000
                    movement(varLeft,varRight,pwma,pwmb,"left",pathFlag)

                elif(zeroAngleIndex > midPointAngleList): #more negative angles
                    print("turn right")
                    varLeft = 2500
                    varRight = 2000
                    movement(varLeft,varRight,pwma,pwmb,"right",pathFlag)
                    
##                elif(rightBoundary > 401 or leftBoundary > 401):
##                    print("turn right")
##                    varLeft = 2500
##                    varRight = 2000
##                    movement(varLeft,varRight,pwma,pwmb,"right",pathFlag)
##                    
##                elif(leftBoundary < 249 or rightBoundary < 249):
##                    print("turn left")
##                    varLeft = 1000
##                    varRight = 4000
##                    movement(varLeft,varRight,pwma,pwmb,"left",pathFlag)
        else:
            print("finding path")
            pathFlag = True
            varLeft = 1000
            varRight = 2000
            movement(varLeft,varRight,pwma,pwmb,"up",pathFlag)
            
        pathFlag = False

        timeStop = time.time()
        print("time taken : ",(timeStop-timeStart)*1000, "ms")
        
        
        # show frame
##        cv2.imshow("Image", edges)
        cv2.imshow("Line Image", image)
##        cv2.imshow("canny",edges)
##        cv2.imshow("mask",mask)
        cv2.imshow("Result", result)
                
        # clear stream in preparation for next frame
        rawCapture.truncate(0)
        
        # wait for input
        key = cv2.waitKey(1) & 0xFF

        # stop movement if keyboard p is pressed
        if key & 0xFF == ord("s"):
            print('start')
            direction = "up"
        
        # stop movement if keyboard p is pressed
        if key & 0xFF == ord("p"):
            print('pause')
            pwma.stop()
            pwmb.stop()

        # exit from loop if keyboard q is pressed
        if key & 0xFF == ord("q"):
            print('quit')
            pwma.stop()
            pwmb.stop()
            break
        
    endProgramTime = time.time()
    print ('Elapsed time : ', endProgramTime-startProgramTime,'secs')
    GPIO.cleanup() #important to have to reset the GPIOs
