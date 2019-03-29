import time
time1 = time.time()
import cv2
import numpy as np
import math
from picamera import PiCamera
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
from settings import config

def movement (varLeft, varRight, moreSide, lessSide, pwma, pwmb, direction, findPath):
    pass
##    print("left: ", varLeft, " | ", "right: ", varRight, " | ", "direction: ", direction, " | ", "pathFlag: ",findPath)
##    if(findPath == True):
##        print("finding path")
##        print("no path detected")
##        pwma.stop()
##        pwmb.stop()
####        pwma.start(1)
####        pwmb.start(20)
####        GPIO.output(settings["AIN1"],1)
####        GPIO.output(settings["AIN2"],0)
####        GPIO.output(settings["BIN1"],1)
####        GPIO.output(settings["BIN2"],0)
####        pwma.ChangeFrequency(varRight)
####        pwmb.ChangeFrequency(varLeft)
##    else:
##        if(direction == "up"):
##            print("up movement")
##            print("more side : ", moreSide, "less side : ", lessSide)
##            pwma.start(moreSide)
##            pwmb.start(lessSide)
##            GPIO.output(settings["AIN1"],1)
##            GPIO.output(settings["AIN2"],0)
##            GPIO.output(settings["BIN1"],1)
##            GPIO.output(settings["BIN2"],0)
##            pwma.ChangeFrequency(varRight)
##            pwmb.ChangeFrequency(varLeft)
##            
##        elif(direction == "left"):
##            print("left movement")
##            print("more side : ", moreSide, "less side : ", lessSide)
##            pwma.start(moreSide)
##            pwmb.start(lessSide)
##            GPIO.output(settings["AIN1"],1)
##            GPIO.output(settings["AIN2"],0)
##            GPIO.output(settings["BIN1"],1)
##            GPIO.output(settings["BIN2"],0)
##            pwma.ChangeFrequency(varRight)
##            pwmb.ChangeFrequency(varLeft)
##            
##        elif(direction == "right"):
##            print("right movement")
##            print("more side : ", moreSide, "less side : ", lessSide)
##            pwma.start(lessSide)
##            pwmb.start(moreSide)
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

    startFlag = False
    direction = False
    pathFlag = False
    varLeft = 1
    varRight = 1

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
    print ('Set up time : ', time3-time1,'secs')

    # camera warm up
    time.sleep(2)

    # capture frames from camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

        timeStart = time.time()
        
        pathXList = []
        angleList = []
        parallelAngle = []
        consolidatedList = []
        toBeRemoved = []
        varLeft = 1000
        varRight = 1250
            
        # image array, processing is done here
        image = frame.array

        blur = cv2.GaussianBlur(image,(5,5),0)

        hsv = cv2.cvtColor(blur, cv2.COLOR_RGB2GRAY)
        
##        edges = autoCanny(hsv) #settings["cannyMin"] , settings["cannyMax"]
        edges = cv2.Canny(hsv, 80, 100)
        
        lines = cv2.HoughLinesP(edges, rho = 1, theta = np.pi/360, threshold =  100, minLineLength = settings["minLineLength"], maxLineGap = settings["maxLineGap"])

        print("--------------------------------------------------------------------------------")
        if(lines is not None):
            lenlines = len(lines)
            print("number of lines : ",lenlines)
            if(lenlines <= 8):
                for line in lines:
                    for x1,y1,x2,y2 in line:
                        print("x1 : ",x1," y1 : ",y1, " x2 : ",x2," y2 : ",y2)
                        dy = y2-y1
                        dx = x2-x1
                        angle = round(math.degrees(math.atan2(dy,dx)))
##                        print(" angle : ", angle)
                        if(angle <= -20 or angle >= 20):
                            consolidatedList.append((angle,x1,y1,x2,y2))
                            angleList.append(angle)
            else:
                print("passing")
                pass
        angleList.sort()
        consolidatedList.sort(key = lambda tup : tup[0])#sort by 1st tuple item (angle)
##        print(consolidatedList)
        print("angleList : ",angleList)
        parallelAngle = set(currentParallelAngle for currentParallelAngle in angleList if angleList.count(currentParallelAngle) > 1)
        print("parellel Angle : ",parallelAngle)

        if(parallelAngle == set()):
            print("no parallel angle")
            if(len(angleList) != 0):
                averageAngles = round(sum(angleList)/len(angleList))
                print("average angle", averageAngles)
                for angle in angleList:
                    difference = angle - averageAngles
                    if(abs(difference) <= 10):
                        print("add angle", averageAngles)
                        parallelAngle.add(averageAngles)            


        print("consolidated list : ", consolidatedList)
        for i in consolidatedList:
            angle,x1,y1,x2,y2 = i

            for currentParallelAngle in parallelAngle:
##                print("currentParallelAngle : ",currentParallelAngle)
                difference = currentParallelAngle - angle
                if(abs(difference) <= 2):
                    cv2.line(image,(x1,y1),(x2,y2),(0,255,0),2)
                    pathXList.extend([x1,x2])
                    break
                else:
                    pass
                
        #remove duplicates in list
        pathXList = list(set(pathXList))
        #sort list from smallest to biggest
        pathXList.sort()
##        print(pathXList)
        amtOfPathXList = len(pathXList)
        print("len of path x list : ",amtOfPathXList)
        if(amtOfPathXList != 0):
            if(amtOfPathXList > 16):
                print("too many lines detected, do nothing")
                rawCapture.truncate(0)
                continue
            else:
                averageAngle = currentParallelAngle
##                sum(angleList)/len(angleList)
                print("averageAngle : ",averageAngle)
                print("pathXList : ",pathXList)
                leftBoundary = pathXList[0]
                rightBoundary = pathXList[len(pathXList)-1]
                print("boundary of path = ",leftBoundary," and ",rightBoundary)

                if(229 <= leftBoundary and rightBoundary <= 409): # 0 - 229 = 230 pixels, 409 - 639 = 230 pixels, center pixels = 640 - 230 - 230 = 180
                    print("gp forward")
                    moreSide = 10
                    lessSide = 10
                    movement(varLeft,varRight,moreSide,lessSide,pwma,pwmb,"up",pathFlag)
                    
                elif(rightBoundary > 409):
                    print("right boundary")
                    if(averageAngle < 0):
                        print("turn right")
                        if(averageAngle <= -20 and averageAngle > -37.5):
                            moreSide = 40
                            lessSide = 10
                        elif(averageAngle <= -37.5 and averageAngle > -55):
                            moreSide = 35
                            lessSide = 10
                        elif(averageAngle <= -55 and averageAngle > -72.5):
                            moreSide = 30
                            lessSide = 10    
                        elif(averageAngle <= -72.5 and averageAngle > -90):
                            moreSide = 25
                            lessSide = 10
                        else:
                            moreSide = 10
                            lessSide = 10
                        movement(varLeft,varRight,moreSide,lessSide,pwma,pwmb,"right",pathFlag)
                    elif(averageAngle > 0):
                        print("turn left")
                        if(averageAngle >= 20 and averageAngle < 37.5):
                            moreSide = 40
                            lessSide = 10
                        elif(averageAngle >= 37.5 and averageAngle < 55):
                            moreSide = 35
                            lessSide = 10
                        elif(averageAngle >= 55 and averageAngle < 72.5):
                            moreSide = 30
                            lessSide = 10
                        elif(averageAngle >= 72.5 and averageAngle < 90):
                            moreSide = 25
                            lessSide = 10
                        else:
                            moreSide = 10
                            lessSide = 10
                        movement(varLeft,varRight,moreSide,lessSide,pwma,pwmb,"left",pathFlag) 
                    
                    
                elif(leftBoundary < 229):
                    print("left boundary")
                    if(averageAngle <= 0):
                        print("turn right")
                        if(averageAngle <= -20 and averageAngle > -37.5):
                            moreSide = 40
                            lessSide = 10
                        elif(averageAngle <= -37.5 and averageAngle > -55):
                            moreSide = 35
                            lessSide = 10
                        elif(averageAngle <= -55 and averageAngle > -72.5):
                            moreSide = 30
                            lessSide = 10    
                        elif(averageAngle <= -72.5 and averageAngle > -90):
                            moreSide = 25
                            lessSide = 10
                        movement(varLeft,varRight,moreSide,lessSide,pwma,pwmb,"right",pathFlag)

                    elif(averageAngle >= 0):
                        print("turn left")
                        if(averageAngle >= 20 and averageAngle < 37.5):
                            moreSide = 40
                            lessSide = 10
                        elif(averageAngle >= 37.5 and averageAngle < 55):
                            moreSide = 35
                            lessSide = 10
                        elif(averageAngle >= 55 and averageAngle < 72.5):
                            moreSide = 30
                            lessSide = 10
                        elif(averageAngle >= 72.5 and averageAngle < 90):
                            moreSide = 25
                            lessSide = 10
                        movement(varLeft,varRight,moreSide,lessSide,pwma,pwmb,"left",pathFlag)                    

        else:
            print("finding path")
            pathFlag = True
            moreSide = 50
            lessSide = 50
            movement(varLeft,varRight,moreSide,lessSide,pwma,pwmb,"up",pathFlag)
            
        pathFlag = False

        timeStop = time.time()
        print("time taken : ",(timeStop-timeStart)*1000, "ms")
        
        
        # show frame
##        cv2.imshow("Image", edges)
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
        
    time2 = time.time()
    print ('Elapsed time : ', time2-time1,'secs')
    GPIO.cleanup() #important to have to reset the GPIOs
