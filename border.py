import time
time1 = time.time()
import cv2
import numpy as np
import math
from picamera import PiCamera
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
from settings import config

slidingWindow = []
amtToRemove = 0

def movement (varLeft, varRight, moreSide, lessSide, pwma, pwmb, direction, findPath):
    print("left: ", varLeft, " | ", "right: ", varRight, " | ", "direction: ", direction, " | ", "pathFlag: ",findPath)
    if(findPath == True):
        print("finding path")
        print("no path detected")
        pwma.stop()
        pwmb.stop()
##        pwma.start(1)
##        pwmb.start(20)
##        GPIO.output(settings["AIN1"],1)
##        GPIO.output(settings["AIN2"],0)
##        GPIO.output(settings["BIN1"],1)
##        GPIO.output(settings["BIN2"],0)
##        pwma.ChangeFrequency(varRight)
##        pwmb.ChangeFrequency(varLeft)
    else:
        if(direction == "up"):
            print("up movement")
            print("more side : ", moreSide, "less side : ", lessSide)
##            pwma.start(moreSide)
##            pwmb.start(lessSide)
##            GPIO.output(settings["AIN1"],1)
##            GPIO.output(settings["AIN2"],0)
##            GPIO.output(settings["BIN1"],1)
##            GPIO.output(settings["BIN2"],0)
##            pwma.ChangeFrequency(varRight)
##            pwmb.ChangeFrequency(varLeft)
            
        elif(direction == "left"):
            print("left movement")
            print("more side : ", moreSide, "less side : ", lessSide)
##            pwma.start(moreSide)
##            pwmb.start(lessSide)
##            GPIO.output(settings["AIN1"],1)
##            GPIO.output(settings["AIN2"],0)
##            GPIO.output(settings["BIN1"],1)
##            GPIO.output(settings["BIN2"],0)
##            pwma.ChangeFrequency(varRight)
##            pwmb.ChangeFrequency(varLeft)
            
        elif(direction == "right"):
            print("right movement")
            print("more side : ", moreSide, "less side : ", lessSide)
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

        pathXList = []
        x1List = []
        y1List = []
        x2List = []
        y2List = []
        lineList = []
        tempWindow = []
        varLeft = 1000
        varRight = 1250
            
        # image array, processing is done here
        image = frame.array

        blur = cv2.GaussianBlur(image,(5,5),0)

        hsv = cv2.cvtColor(blur, cv2.COLOR_RGB2GRAY)

        edges = cv2.Canny(hsv, 80, 100)
        
##        lines = cv2.HoughLinesP(edges, rho = 1, theta = np.pi/360, threshold =  100, minLineLength = settings["minLineLength"], maxLineGap = settings["maxLineGap"])
        timeStart = time.time()
        # show frame
        cv2.imshow("Canny Image", edges)
        
        print("--------------------------------------------------------------------------------")

        nonzero = cv2.findNonZero(edges)
        counter = 0
        for index in nonzero:
            if(index[0][1] == 0 or index[0][1] == 479):
                print("x is : ",index[0][0], " y is ", index[0][1])
                tempWindow.append((index[0][0],index[0][1]))
                counter += 1
            elif(index[0][0] == 0 or index[0][0] == 639):
                print("x`is : ",index[0][0], " y is ", index[0][1])
                tempWindow.append((index[0][0],index[0][1]))
                counter += 1
        
        print(counter)
        tempWindow.sort(key=lambda k : [k[0],k[1]])
        slidingWindow.extend(tempWindow)
        if(amtToRemove == 0):
            amtToRemove = counter
        else:
            print("sliding window : ",slidingWindow, " counter : ",amtToRemove)
            slidingWindow = slidingWindow[amtToRemove:]
            amtToRemove = counter
            print("sliding window : ",slidingWindow, " counter : ",amtToRemove)
            
        pathFlag = False
        timeStop = time.time()
        print("time taken : ",(timeStop-timeStart)*1000, "ms")
        
        
        
                
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
